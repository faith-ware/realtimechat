from django.contrib import admin
from .models import Group,Chat, Member
# Register your models here.

admin.site.register(Group)
admin.site.register(Chat)
admin.site.register(Member)

