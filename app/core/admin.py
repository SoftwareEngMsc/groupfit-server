"""
Customised Django admin
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models


class UserAdmin(BaseUserAdmin):
    """Define Admin pages for users"""

    ordering = ['id']
    list_display = ['id', 'email', 'first_name', 'last_name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email',
                'password1',
                'password2',
                'first_name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )


class Groups():
    """Define admin pages for Group"""
    ordering = ['id']
    list_display = ['id', 'group_name',
                    'target_workout_number_per_week', 'created_by']


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Group)
admin.site.register(models.GroupMembership)
admin.site.register(models.GroupWorkout)
admin.site.register(models.GroupWorkoutEvidence)
