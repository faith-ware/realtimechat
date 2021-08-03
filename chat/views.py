from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http.response import JsonResponse
from django.urls import reverse
from .models import Group, Member, Connected_channel
import string, random
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login
from django.contrib import messages

def index(request):
    context = {

    }
    return render(request, "index.html", context)


def room(request, room_name):
    # Check if group exists
    try:
        group_id = Group.objects.filter(name = room_name)[0].id
    except:
        return redirect(reverse("chat:index"))

    user_id = request.user.id
    check_member = Member.objects.filter(user_id = user_id, group_id = group_id).exists()
    check_group = Group.objects.filter(name = room_name).exists()
    group_members = Member.objects.filter(group_id = group_id)

    if check_member:
        if request.user.is_authenticated:
            context = {
                "room_name" : room_name,
                "current_user" : request.user,
                "group_members" : group_members
            }
            return render(request, "chat/room.html", context)
        else:
            return redirect(reverse("chat:user_auth", args=[room_name]))
            
    elif check_group:
        return redirect(reverse("chat:user_auth", args=[room_name]))

    else:
        return redirect(reverse("chat:index"))


# Generate a group name and password randomly
def generate_group_name(request):
    char = string.ascii_letters + string.digits 
    name = (random.choice(char) for _ in range(11))
    generated_name = "".join(name)
    check_name = Group.objects.filter(name = generated_name).exists()
    
    if check_name:
        generate_group_name(request)
    else:
        password = (random.choice(char) for _ in range(10))
        generated_password = "".join(password)
        group = Group(name = generated_name, password = generated_password)
        group.save()
        
        response = {
            "generated_name" : generated_name,
            "generated_password" : generated_password,
        }
        return JsonResponse(response)


def user_auth(request, room_name):
    context = {}
    try:
        group_id = Group.objects.filter(name = room_name)[0].id
    except:
        return redirect(reverse("chat:index"))

    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        if len(password) > 3:
            group_password = request.POST["group-password"]
            group_name = room_name
            group_id = Group.objects.filter(name = room_name)[0].id

            # Check if group exists and authenticate
            try:
                group = Group.objects.filter(name = group_name)[0]

                # Check if the group password is correct
                if check_password(group_password, group.password):

                    # Check if user already exists
                    check_user = User.objects.filter(username = username).exists()

                    if check_user:
                        user = authenticate(username = username, password = password)

                        # Log user in if credentials are correct
                        if user is not None:
                            login(request, user)
                            user_id = request.user.id

                            # Check if the existing user is already a member of the group 
                            check_member = Member.objects.filter(user_id = user_id, group_id = group_id).exists()
                            if check_member:
                                return redirect(reverse("chat:room", args=[room_name]))
                            
                            # Add existing user as a member of the group
                            elif check_member == False:
                                new_member = Member(user_id = user_id, group_id = group_id)
                                new_member.save()
                                return redirect(reverse("chat:room", args=[room_name]))

                        else:
                            messages.warning(request, "Incorrect username or password")
                            # return redirect(reverse("chat:user_auth", args=[room_name]))

                    # Create new user and add to the group if the user is not a member 
                    else:
                        new_user = User.objects.create_user(username, password = password)
                        new_user.save()
                        new_member = Member(user_id = new_user.id, group_id = group.id)
                        new_member.save()
                        new_user_auth = authenticate(username = username, password = password)

                        if new_user_auth is not None:
                            login(request, new_user_auth)
                            return redirect(reverse("chat:room", args=[room_name]))
                else:
                    messages.warning(request, "Incorrect group password")
            # Redirect to login page if credentials are not correct
            except:
                return redirect(reverse("chat:user_auth", args=[room_name]))
        
        else:
            messages.warning(request, "Password is too short")

    return render(request, "chat/user_login.html", context)


def delete_user_channel(request, room_name):
    user_id = request.user.id
    group_id = Group.objects.filter(name = room_name)[0]
    user_channels = Connected_channel.objects.filter(user_id = user_id, group_id = group_id)
    user_channels.delete()
    response = {
        "deleted" : "deleted",
    }
    return JsonResponse(response)
