"""
URL mappins for  the Group app
"""

from django.urls import (path, include)

from rest_framework.routers import DefaultRouter

from group import views


router = DefaultRouter()
router.register('groups', views.GroupViewSet, basename='group')

app_name = 'group'

urlpatterns = [
    path('', include(router.urls)),
]
