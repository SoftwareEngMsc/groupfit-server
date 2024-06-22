""""Serializers for the member API view"""

from django.contrib.auth import get_user_model

from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for the member object"""

    class Meta:
        model = get_user_model()
        fields = ['email', 'password', 'firstname',
                  'lastname', 'date_of_birth']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """create and return a member with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)
