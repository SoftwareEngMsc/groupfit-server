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
        """creates the group and adds user as an admin"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')

        group = Group.objects.filter(id=group_id).first()
        member = get_user_model().objects.filter(id=member_id).first()
        group_member = GroupMembership.objects.create(
            member=member,
            group=group,
            member_role=self.request.data.get('member_role'),
        )
        group_member.save()
        serializer = self.get_serializer(group_member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        """Return the serializer class  for  request"""
        if self.action == "members":
            return serializers.GroupMembersListSerializer
        if self.action == "create":
            return serializers.GroupSerializer

        return self.serializer_class
