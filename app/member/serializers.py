""""Serializers for the member API view"""

from django.contrib.auth import (
    get_user_model,
    authenticate,
)
from django.utils.translation import gettext as _

from rest_framework import serializers


class MemberSerializer(serializers.ModelSerializer):
    """Serializer for the member object"""

    class Meta:
        model = get_user_model()
        fields = ['id', 'email', 'password', 'first_name',
                  'last_name', 'join_date']
        read_only_fields = ['id', 'join_date']
        extra_kwargs = {'password': {'write_only': True, 'min_length': 8}}

    def create(self, validated_data):
        """create and return a member with encrypted password"""
        return get_user_model().objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        """Update and return member"""
        password = validated_data.pop('password', None)
        member = super().update(instance, validated_data)

        if password:
            member.set_password(password)
            member.save()

        return member


class AuthTokenSerializer(serializers.Serializer):
    """Serializer for the member auth token"""
    email = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        """Validate and authenticate the member"""

        email = attrs.get('email')
        password = attrs.get('password')
        member = authenticate(
            request=self.context.get('request'),
            username=email,
            password=password,
        )
        if not member:
            msg = _('Unable to authenticate with the credentials provided')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = member
        return attrs
