from django.contrib import admin
from .models import Group,Chat, Member, Connected_channel, Online
# Register your models here.

admin.site.register(Group)
admin.site.register(Chat)
admin.site.register(Member)
admin.site.register(Connected_channel)
admin.site.register(Online)

