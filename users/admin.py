from django.contrib import admin
from users.models import User, FriendInvite, UserWallPost, UserWallNewsM2M, FriendInfo


class UsersInLine(admin.TabularInline):
    model = UserWallNewsM2M
    extra = 0


class UserAdmin(admin.ModelAdmin):
    inlines = [UsersInLine]


admin.site.register(User, UserAdmin)
admin.site.register(FriendInvite)
admin.site.register(UserWallPost)
admin.site.register(FriendInfo)

