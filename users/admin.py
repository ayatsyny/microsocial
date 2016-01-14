from django.contrib import admin
from users.models import User, Order, UserWallPost#, UserFriends


# class RelationshipInline(admin.StackedInline):
#     model = UserFriends
#     fk_name = 'from_user'
#     extra = 1
#
#
# class PersonAdmin(admin.ModelAdmin):
#     inlines = [RelationshipInline]


admin.site.register(User)
admin.site.register(Order)
# admin.site.register(User, PersonAdmin)
admin.site.register(UserWallPost)
