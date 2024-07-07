"""Views for the Friends API"""
from datetime import datetime
from django.http import Http404
from django.db.models import Q
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
        """Get friends for authenticated user"""

        return self.queryset.filter(
            Q(user1=self.request.user) | Q(user2=self.request.user))

    @action(detail=False, methods=['GET'])
    def getFriends(self, request):
        """Custom action for getting friends for a given user"""

        user_id = self.request.query_params.get('user_id')
        user = get_user_model().objects.filter(id=user_id).first()

        serializer = self.get_serializer(
            self.queryset.filter(user1=user), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def addFriend(self, request, pk=None):
        """Custom action for adding a friend for a given user"""

        requested_by_id = self.request.data.get('requested_by_id')
        user2_id = self.request.data.get('user2_id')

        requested_by = get_user_model().objects.filter(
            id=requested_by_id).first()
        user2 = get_user_model().objects.filter(id=user2_id).first()

        existing_friend_connections = self.queryset.filter(
            Q(user1=requested_by) | Q(user2=requested_by))

        if existing_friend_connections.filter(
                Q(user1=user2) | Q(user2=user2)).exists():

            return Response({'message': 'Connection already exists for users'},
                            status=status.HTTP_400_BAD_REQUEST)

        friend_connection = Friends.objects.create(
            user1=requested_by,
            user2=user2,
            status='Pending',
            requested_by=requested_by,
        )
        friend_connection.save()
        serializer = self.get_serializer(friend_connection)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PATCH'])
    def response(self, request, pk=None):
        """Custom action for accepting or rejecting a friend"""

        user_id = self.request.data.get('user_id')
        friend_conn_id = self.request.data.get('friend_conn_id')
        new_status = self.request.data.get('status')

        user = get_user_model().objects.filter(
            id=user_id).first()

        friend_connection = self.queryset.filter(
            Q(id=friend_conn_id) & Q(user2=user)
            & Q(status='Pending')).first()

        if not friend_connection:

            return Response({'message': 'No valid friend Connection found'},
                            status=status.HTTP_400_BAD_REQUEST)

        data_to_update = {
            'status': new_status,
            'connected_date': datetime.today().strftime('%Y-%m-%d')
        }
        serializer = self.get_serializer(instance=friend_connection,
                                         data=data_to_update,
                                         partial=True
                                         )

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def deleteFriend(self, request, *args, **kwargs):
        """deletes the friend connection"""

        friend_connection_id = kwargs.get('pk')
        try:
            friend_connection = Friends.objects.filter(
                id=friend_connection_id).first()
            self.perform_destroy(friend_connection)
            return Response({'message': 'Friend Connection deleted'},
                            status=status.HTTP_204_NO_CONTENT)
        except (Http404):
            return Response({'message': 'Friend connection not found'
                             }, status=status.HTTP_400_BAD_REQUEST)
