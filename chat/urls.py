from os import name
from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("chat/<str:room_name>/", views.room, name="room"),
    path("generate/", views.generate_group_name, name="generate"),
    path("userlogin/<str:room_name>/", views.user_auth, name="user_auth"),
    path("delete_channel/<str:room_name>/", views.delete_user_channel, name="delete_user_channel")
]
