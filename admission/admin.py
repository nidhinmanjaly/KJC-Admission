from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm

from .models import *

User = get_user_model()

# Remove Group Model from admin. We're not using it.
admin.site.unregister(Group)

class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'username', 'password', 'user_type', 'is_staff', 'is_superuser')
    list_filter = ('is_superuser',)

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'user_type')}),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser'),
        }),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password1', 'password2', 'user_type')}),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser'),
        }),
    )

    search_fields = ('email', 'username',)
    ordering = ('email',)
    filter_horizontal = ()

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Applicant_Details)
admin.site.register(Interview)
admin.site.register(Interview_panel)
admin.site.register(Remarks)
admin.site.register(Allotment_Details)
admin.site.register(Reviewers_Indicators)

