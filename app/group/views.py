"""
Views for the Group APIs
"""
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import GroupMembership
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
        serializer = self.get_serializer(self.queryset.all(), many=True)
        return Response(serializer.data)

    def get_serializer_class(self):
        """Return the serializer class  for  request"""
        if self.action == "members":
            return serializers.GroupMembersListSerializer

        return self.serializer_class
