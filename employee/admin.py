from django.contrib import admin
from .models import User, Profile, SettingsUser, Position


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',  'username', 'email', 'is_active', 'created')


@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',  'account', 'position', 'paul', 'created')


@admin.register(SettingsUser)
class AdminSettingsUser(admin.ModelAdmin):
    list_display = ('user', 'is_mail_inbox', 'is_mail_movement', 'is_mail_ad')


@admin.register(Position)
class AdminPosition(admin.ModelAdmin):
    list_display = ('name', 'created')


