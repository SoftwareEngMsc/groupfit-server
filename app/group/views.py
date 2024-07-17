"""
Views for the Group APIs
"""
from django.contrib.auth import get_user_model
from django.http import Http404
from rest_framework.decorators import action
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (GroupMembership,
                         Group,
                         GroupWorkout,
                         GroupWorkoutEvidence)
from group import serializers


class GroupViewSet(mixins.CreateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.ListModelMixin,
                   viewsets.GenericViewSet):
    """View for managing group APIs"""

    serializer_class = serializers.GroupMembershipSerializer
    queryset = GroupMembership.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get groups for authenticated user"""

        return self.queryset.filter(member=self.request.user)

    @action(detail=False, methods=['GET'])
    def getGroups(self, request):
        """Custom action for getting groups for user"""

        group_ids = list(self.get_queryset().values_list('group'))
        group_ids = list(map(lambda x: x[0], group_ids))

        groups = Group.objects.filter(id__in=group_ids)
        serializer = self.get_serializer(groups, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['DELETE'])
    def deleteGroup(self, request, *args, **kwargs):
        """deletes the group"""

        group_id = kwargs.get('pk')
        try:
            group = Group.objects.filter(id=group_id).first()
            self.perform_destroy(group)
            return Response({'message': 'Group deleted successfully'},
                            status=status.HTTP_204_NO_CONTENT)
        except (Http404):
            return Response({'message': 'Group not found'
                             }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['GET'])
    def members(self, request):
        """Custom action for getting list of members for a given group"""

        group_id = self.request.query_params.get('group_id')
        serializer = self.get_serializer(
            self.queryset.filter(group_id=group_id), many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def addMember(self, request):
        """Adds the membe to the group"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')
        member_role = self.request.data.get('member_role')

        member = get_user_model().objects.filter(id=member_id).first()

        # TODO: change member_role literals and all references to a constant
        if (member_role == 'Member'):
            if (not self.check_admin_user_present(group_id, member)):
                return Response({'message': 'Group must have an Admin member'},
                                status=status.HTTP_403_FORBIDDEN)

        group = Group.objects.filter(id=group_id).first()

        group_member = GroupMembership.objects.create(
            member=member,
            group=group,
            member_role=member_role,
        )
        group_member.save()
        serializer = self.get_serializer(group_member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['PUT'])
    def updateMember(self, request, pk=None):
        """updates member role in given group"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')
        new_member_role = self.request.data.get('new_member_role')

        member = get_user_model().objects.filter(id=member_id).first()

        # TODO: change member_role literals and all references to a constant
        if (new_member_role == 'Member'):
            if (not self.check_admin_user_present(group_id, member)):
                return Response({'message': 'Group must have an Admin member'},
                                status=status.HTTP_403_FORBIDDEN)
        member_to_update = self.queryset.filter(group_id=group_id,
                                                member_id=member_id).first()
        if not member_to_update:
            return Response({'message': 'Member does not exist in given group'
                             }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(instance=member_to_update,
                                         data={'member_role': new_member_role},
                                         partial=True
                                         )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['DELETE'])
    def deleteMember(self, request, pk=None):
        """updates member role in given group"""
        group_id = self.request.data.get('group')
        member_id = self.request.data.get('member')

        member = get_user_model().objects.filter(id=member_id).first()

        if (not self.check_admin_user_present(group_id, member)):
            return Response({'message': 'Group must have an Admin member'},
                            status=status.HTTP_403_FORBIDDEN)

        member_to_delete = self.queryset.filter(group_id=group_id,
                                                member_id=member_id).first()
        if not member_to_delete:
            return Response({'message': 'Member does not exist in given group'
                             }, status=status.HTTP_400_BAD_REQUEST)

        group = Group.objects.filter(id=group_id).first()

        if group.created_by == member_to_delete.member.id:
            return Response(
                {'message': 'Groups owner cannot be deleted from the group.'
                 }, status=status.HTTP_400_BAD_REQUEST)
        member_to_delete.delete()
        return Response({'res': 'Member successfully deleted from group'},
                        status=status.HTTP_204_NO_CONTENT)

    def get_serializer_class(self):
        """Return the serializer class  for  request"""
        if self.action == "members":
            return serializers.GroupMembersListSerializer
        elif self.action == "create":
            return serializers.GroupSerializer
        elif self.action == "getGroups":
            return serializers.GroupSerializer

        return self.serializer_class

    def check_admin_user_present(self, group_id, member):
        """Checks whether there is an admin user in the group"""
        serializer = self.get_serializer(
            self.queryset.filter(group_id=group_id), many=True)

        if (serializer.data):
            for membership in serializer.data:
                if (membership['member'] != member.email
                        and membership['member_role'] == 'Admin'):
                    return True
            return False
        else:
            return False


class GroupWorkoutViewSet(mixins.CreateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.UpdateModelMixin,
                          mixins.ListModelMixin,
                          mixins.RetrieveModelMixin,
                          viewsets.GenericViewSet):
    """View for managing group workout APIs"""

    serializer_class = serializers.GroupWorkoutSerializer
    queryset = GroupWorkout.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get group workouts for authenticated user"""

        return self.queryset.filter(member=self.request.user)

    @action(detail=True, methods=['GET'])
    def workout(self, request, pk=None, *args, **kwargs):
        """updates member role in given group"""
        group_id = self.request.query_params['group_id']
        queryset_res = self.queryset.filter(group_id=group_id)
        serializer = self.get_serializer(queryset_res, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def addWorkout(self, request, pk=None, *args, **kwargs):
        """Adds the workout to the group"""
        name = self.request.data.get('name')
        description = self.request.data.get('description')
        group_id = self.request.data.get('group_id')
        link = self.request.data.get('link')

        group = Group.objects.filter(id=group_id).first()

        workout = GroupWorkout.objects.create(
            name=name,
            description=description,
            link=link,
            group=group,
        )

        workout.save()
        serializer = self.get_serializer(workout)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['DELETE'])
    def deleteWorkout(self, request, pk=None):
        """deletes workout in given group"""
        workout_id = self.request.data.get('workout_id')

        workout_to_delete = self.queryset.filter(id=workout_id).first()
        if not workout_to_delete:
            return Response({'message': 'Workout does not exist in given group'
                             }, status=status.HTTP_400_BAD_REQUEST)

        workout_to_delete.delete()
        return Response({'res': 'Workout successfully deleted from group'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def evidence(self, request, pk=None, *args, **kwargs):
        """updates member role in given group"""
        member_id = self.request.query_params['member_id']
        workout_id = self.request.query_params['workout_id']

        queryset_res = GroupWorkoutEvidence.objects.filter(
            workout_id=workout_id, member_id=member_id)

        serializer = self.get_serializer(queryset_res, many=True)

        return Response(serializer.data)

    @action(detail=True, methods=['GET'])
    def evidenceLog(self, request, pk=None, *args, **kwargs):
        """updates member role in given group"""
        member_id = self.request.query_params['member_id']
        group_id = self.request.query_params['group_id']

        workout_ids = GroupWorkout.objects.filter(
            group_id=group_id).values_list('id')

        workout_ids = list(map(lambda x: x[0], workout_ids))

        queryset_res = GroupWorkoutEvidence.objects.filter(
            member_id=member_id, workout_id__in=workout_ids)

        serializer = self.get_serializer(queryset_res, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['POST'])
    def uploadEvidence(self, request, pk=None, *args, **kwargs):
        """uploads workout evidence"""

        workout_id = self.request.data.get('workout_id')
        evidence = self.request.data.get('evidence_image')

        workout_evidence = GroupWorkoutEvidence.objects.filter(
            workout_id=workout_id, member_id=self.request.user.id).first()

        serializer = self.get_serializer(
            workout_evidence, data={'member': workout_evidence.member.id,
                                    'workout': workout_evidence.workout.id,
                                    'evidence_image': evidence})

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        """Return the serializer class  for  request"""

        if self.action == "evidence" or self.action == "evidenceLog":
            return serializers.GroupWorkoutEvidenceSerializer
        elif self.action == 'uploadEvidence':
            return serializers.WorkoutEvidenceImageSerializer

        return self.serializer_class
