from django.contrib.auth.hashers import make_password, check_password
from django.contrib import admin

from .models import User, Profile, SettingsUser, Position


@admin.register(User)
class AdminUser(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',  'username', 'email', 'is_active', 'created')

    def save_model(self, request, obj, form, change):
        user_database = User.objects.get(pk=obj.pk)
        # Check firs the case in which the password is not encoded, then check in the case that the password is encode
        if not (check_password(form.data['password'], user_database.password) or user_database.password == form.data['password']):
            obj.password = make_password(obj.password)
        else:
            obj.password = user_database.password
        super().save_model(request, obj, form, change)


@admin.register(Profile)
class AdminProfile(admin.ModelAdmin):
    list_display = ('last_name', 'first_name',  'account', 'position', 'paul', 'created')


@admin.register(SettingsUser)
class AdminSettingsUser(admin.ModelAdmin):
    list_display = ('user', 'is_mail_inbox', 'is_mail_movement', 'is_mail_ad')


@admin.register(Position)
class AdminPosition(admin.ModelAdmin):
    list_display = ('name', 'created')


