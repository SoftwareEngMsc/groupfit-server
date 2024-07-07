"""Serializers for the Friends API"""

from member.serializers import MemberSerializer
from core.models import Friends
from rest_framework import serializers


class FriendsSerializer(serializers.ModelSerializer):
    """Serializer for Friends"""

    user1 = MemberSerializer()
    user2 = MemberSerializer()
    requested_by = MemberSerializer()

    class Meta:
        model = Friends
        fields = ['id', 'user1', 'user2',
                  'connected_date', 'status',
                  'requested_by', 'request_date']
        read_only_fields = ['id', 'requested_by', 'request_date']
