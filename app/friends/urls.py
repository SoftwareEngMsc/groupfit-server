"""
URL mappings for  the Friends app
"""

from django.urls import (path, include)

from rest_framework.routers import DefaultRouter

from friends import views


router = DefaultRouter()
router.register('friendsAPI', views.FriendsViewSet, basename='friends')


app_name = 'friends'

urlpatterns = [
    path('', include(router.urls)),
]
