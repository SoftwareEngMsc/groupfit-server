"""
Views for the member API
"""

from rest_framework import generics

from member.serializers import MemberSerializer


class CreateMemberView(generics.CreateAPIView):
    """Create a new member in the system"""
    serializer_class = MemberSerializer
