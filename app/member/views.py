"""
Views for the member API
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from django.db.models import Q

from member.serializers import (
    MemberSerializer,
    AuthTokenSerializer,
)

from django.contrib.auth import (
    get_user_model,
    authenticate,
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


class MemberViewSet(mixins.RetrieveModelMixin,
                    viewsets.GenericViewSet):

    serializer_class = MemberSerializer
    authentication_classes = [authentication.TokenAuthentication]
    permissions_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """Get members"""

        return get_user_model().objects

    @action(detail=False, methods=['GET'])
    def getMemberSearchResults(self, request):
        """Custom action for getting members matching a string pattern"""

        search_string = self.request.query_params.get('search_string')

        result = get_user_model().objects.filter(
            Q(first_name__icontains=search_string) |
            Q(last_name__icontains=search_string))

        serializer = self.get_serializer(result, many=True)

        return Response(serializer.data)
