"""
Serializers for Group API
"""

from rest_framework import serializers

from core.models import Group, GroupMembership, GroupWorkout, GroupWorkoutEvidence
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
    # group = GroupSerializer()
    # member = MemberSerializer()

    group = serializers.SlugRelatedField(
        read_only=True,
        slug_field='group_name'
    )

    member = serializers.SlugRelatedField(
        read_only=True,
        slug_field='email'
    )

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


class GroupWorkoutSerializer(serializers.ModelSerializer):
    """Serializer for workout list for group"""

    group = GroupSerializer()

    class Meta:
        model = GroupWorkout
        fields = ['id', 'name', 'group', 'description', 'link', 'created_date']
        read_only_fields = ['id', 'created_date']


class GroupWorkoutEvidenceSerializer(serializers.ModelSerializer):
    """Serializer for workout evidence list for groupmembers"""

    member = MemberSerializer()
    workout = GroupWorkoutSerializer()

    class Meta:
        model = GroupWorkoutEvidence
        fields = ['id', 'member', 'workout',
                  'evidence_image', 'comment', 'submission_date']
        read_only_fields = ['id', 'created_date']
