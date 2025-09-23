from django.contrib import admin
from .models import User, Category, Photo, Comment, Like
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

admin.site.register(Category)
admin.site.register(Photo)
admin.site.register(Comment)
admin.site.register(Like)