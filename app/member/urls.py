"""
URL mappings for the member API.
"""

from django.urls import path

from member import views

app_name = 'member'

urlpatterns = [
    path('create/', views.CreateMemberView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageMemberView.as_view(), name='me'),
]
