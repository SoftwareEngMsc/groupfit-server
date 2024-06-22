"""
Views for the member API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings

from member.serializers import (
    MemberSerializer,
    AuthTokenSerializer,
)


class CreateMemberView(generics.CreateAPIView):
    """Create a new member in the system"""
    serializer_class = MemberSerializer


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for member"""
    serializer_class = AuthTokenSerializer
    renderer_class = api_settings.DEFAULT_RENDERER_CLASSES


class ManageMemberView(generics.RetrieveUpdateAPIView):
    """Manage the authenticaed member"""
    serializer_class = MemberSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permissions_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """retrieve and return the authenticated member"""
        return self.request.user
