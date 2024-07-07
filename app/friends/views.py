"""Views for the Friends API"""

from django.contrib.auth import get_user_model
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Friends
from friends import serializers


class FriendsViewSet(mixins.CreateModelMixin,
                     mixins.DestroyModelMixin,
                     mixins.UpdateModelMixin,
                     mixins.ListModelMixin,
                     viewsets.GenericViewSet):
    """View for managing group APIs"""

    serializer_class = serializers.FriendsSerializer
    queryset = Friends.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get groups for authenticated user"""

        return self.queryset.filter(member=self.request.user)

    @action(detail=False, methods=['GET'])
    def getFriends(self, request):
        """Custom action for getting friends for a given user"""

        user_id = self.request.query_params.get('user_id')
        user = get_user_model().objects.filter(id=user_id).first()

        serializer = self.get_serializer(
            self.queryset.filter(user1=user), many=True)
        return Response(serializer.data)

    # @action(detail=True, methods=['DELETE'])
    # def deleteGroup(self, request, *args, **kwargs):
    #     """deletes the group"""

    #     group_id = kwargs.get('pk')
    #     try:
    #         group = Group.objects.filter(id=group_id).first()
    #         self.perform_destroy(group)
    #         return Response({'message': 'Group deleted successfully'},
    #                         status=status.HTTP_204_NO_CONTENT)
    #     except (Http404):
    #         return Response({'message': 'Group not found'
    #                          }, status=status.HTTP_400_BAD_REQUEST)
