"""
Serializers for Group API
"""

from rest_framework import serializers

from core.models import Group, GroupMembership
from member.serializers import MemberSerializer


class GroupSerializer(serializers.ModelSerializer):
    """Serializer for groups"""

    class Meta:
        model = Group
        fields = ['id', 'group_name',
                  'target_workout_number_per_week', 'created_by']
        read_only_fields = ['id']


class GroupMembershipSerializer(serializers.ModelSerializer):
    """Serializer for Group Membership"""
    group = GroupSerializer()
    member = MemberSerializer()

    class Meta:
        model = GroupMembership
        fields = ['id', 'member_role', 'group', 'member']
        read_only_fields = ['id']


class GroupMembersListSerializer(serializers.ModelSerializer):
    """Serializer for members list for group"""

    member = MemberSerializer()

    class Meta:
        model = GroupMembership
        fields = ['member']
