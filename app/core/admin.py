# """
# Customised Django admin
# """

# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# from core import models


# class UserAdmin(BaseUserAdmin):
#     """Define Admin pages for users"""

#     ordering = ['id']
#     # list_display = ['email']


# admin.site.register(models.User, UserAdmin)
