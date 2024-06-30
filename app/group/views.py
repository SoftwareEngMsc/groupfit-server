"""
Views for the Group APIs
"""
from django.contrib.auth import get_user_model

from rest_framework.decorators import action
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import GroupMembership, Group
from group import serializers


class GroupViewSet(viewsets.ModelViewSet):
    """View for managing group APIs"""

    serializer_class = serializers.GroupMembershipSerializer
    queryset = GroupMembership.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get groups for authenticated user"""

        return self.queryset.filter(member=self.request.user)

    @action(detail=False, methods=['GET'])
    def members(self, request):
        """Custom action for getting list of members for a given group"""

        group_id = self.request.query_params.get('group_id')
        serializer = self.get_serializer(
            self.queryset.filter(group_id=group_id), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def addMember(self, request):
        """Adds the membe to the group"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')
        member_role = self.request.data.get('member_role')

        member = get_user_model().objects.filter(id=member_id).first()

        # TODO: change member_role literals and all references to a constant
        if (member_role == 'Member'):
            if (not self.check_admin_user_present(group_id, member)):
                return Response({'message': 'Group must have an Admin member'},
                                status=status.HTTP_403_FORBIDDEN)

        group = Group.objects.filter(id=group_id).first()

        group_member = GroupMembership.objects.create(
            member=member,
            group=group,
            member_role=member_role,
        )
        group_member.save()
        serializer = self.get_serializer(group_member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'])
    def updateMember(self, request, pk=None):
        """updates member role in given group"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')
        new_member_role = self.request.data.get('new_member_role')

        member = get_user_model().objects.filter(id=member_id).first()

        # TODO: change member_role literals and all references to a constant
        if (new_member_role == 'Member'):
            if (not self.check_admin_user_present(group_id, member)):
                return Response({'message': 'Group must have an Admin member'},
                                status=status.HTTP_403_FORBIDDEN)
        member_to_update = self.queryset.filter(group_id=group_id,
                                                member_id=member_id).first()

        serializer = self.get_serializer(instance=member_to_update,
                                         data={'member_role': new_member_role},
                                         partial=True
                                         )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        """Return the serializer class  for  request"""
        if self.action == "members":
            return serializers.GroupMembersListSerializer
        if self.action == "create":
            return serializers.GroupSerializer

        return self.serializer_class

    def check_admin_user_present(self, group_id, member):
        """Checks whether there is an admin user in the group"""
        serializer = self.get_serializer(
            self.queryset.filter(group_id=group_id), many=True)

        if (serializer.data):
            for membership in serializer.data:
                if (membership['member'] != member.email
                        and membership['member_role'] == 'Admin'):
                    return True
            return False
        else:
            return False
