import random

from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from . import models
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from django.shortcuts import get_object_or_404
from itertools import chain

@login_required(login_url='signin')
def index(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    posts = Post.objects.all()

    user_following_list = []
    feed = []

    user_following = FollowersCount.objects.filter(follower=request.user.username)

    for users in user_following:
        user_following_list.append(users.user)

    for usernames in user_following_list:
        feed_lists = Post.objects.filter(user=usernames)
        feed.append(feed_lists)

    feed_list = list(chain(*feed))


    # user suggestion

    all_users = User.objects.all()
    user_following_all = []

    for user in user_following:
        user_list = User.objects.get(username=user.user)
        user_following_all.append(user_list)

    new_user_suggestion = [x for x in list(all_users) if (x not in list(user_following_all))]
    current_user = User.objects.filter(username=request.user.username)
    final_suggestion_list = [x for x in list(new_user_suggestion) if x not in list(current_user)]
    random.shuffle(final_suggestion_list)

    username_profile = []
    username_profile_list = []

    for users in final_suggestion_list:
        username_profile.append(users.id)

    for ids in username_profile:
        username_profile_list.append(Profile.objects.filter(id_user=ids))

    suggestion_username_profiles = list(chain(*username_profile_list))

    users_count = len(suggestion_username_profiles)
    context = {
        "profile" : user_profile,
        "posts" : feed_list,
        "suggestion" : suggestion_username_profiles[:4],
        "users_count" : users_count,
    }


    return render(request, 'index.html', context)



@login_required(login_url="signin")
def search(request):
    user_object = User.objects.get(username=request.user.username)
    user_profile = Profile.objects.get(user=user_object)

    if request.method == "POST":
        username = request.POST['username']
        username_object = User.objects.filter(username__icontains=username)

        username_profile = []
        username_profile_list = []

        for users in username_object:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        username_profile_list = list(chain(*username_profile_list))

        user_count = len(username_profile_list)

        context = {
            "profile" : user_profile,
            "username_profile_list" : username_profile_list,
            'users_count' : user_count,
        }
        print(user_count)
        return render(request, "search.html", context)
    else:
        redirect('/')





@login_required(login_url='signin')
def follow(request):
    if request.method == "POST":
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()

        return redirect(f"/profile/{user}")







@login_required(login_url='signin')
def profile(request, pk):
    user_object = User.objects.get(username=pk)
    profile = Profile.objects.get(user=user_object)
    user_post_profile = []
    posts = Post.objects.filter(user=pk)

    follower = request.user.username
    user = pk




    if FollowersCount.objects.filter(user=user, follower=follower).first():
        btn_text = "Unfollow"
    else:
        btn_text = "Follow"

    user_amount = len(FollowersCount.objects.filter(user=user))
    following_amount = len(FollowersCount.objects.filter(follower=user))

    users = {
        "follower" : follower,
        "user_profile" : user,
        "btn_text" : btn_text,
        "followers" : user_amount,
        "following" : following_amount,
    }

    context = {
        'user_object' : user_object,
        'profile' : profile,
        'posts' : posts,
        'post_amount' : len(posts),
        "users" : users,
    }


    return render(request, 'profile.html', context)


@login_required(login_url='signin')
def like(request):
    username = request.user.username
    post_id = request.GET.get("post_id")

    post = Post.objects.get(id=post_id)

    #if mo like from user
    like_filter = LikePost.objects.filter(post_id=post_id, username=username).first()

    if like_filter == None:
        new_like = LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.number_of_likes += 1
        post.save()
        return redirect("index")
    else:
        like_filter.delete()
        post.number_of_likes -= 1
        post.save()
        return redirect('index')




def signup(request):
    #get values from signup page
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        confirm_password = request.POST['confirm-password']


        # if password does not match
        if password == confirm_password:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email was taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username was taken')
                return redirect('signup')
            else:
                # registering a new user that does not exist in db
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                # log in user and redirect to settings page

                user_login = auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #CREATE A NEW PROFILE FOR A NEW USER
                user_model = User.objects.get(username=username)
                new_profile = models.Profile(user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Password does not match')
            return redirect('signup')


    else:
        return render(request, 'signup.html')


def singin(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = auth.authenticate(username=username, password=password)

        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Error!')
            return redirect('signin')

    else:
        return render(request, 'signin.html')


@login_required(login_url='signin')
def logout(request):
    auth.logout(request)
    return redirect('signin')

"""
Этот код использует get_object_or_404, чтобы получить профиль пользователя на основе request.user. 
Он автоматически вызывает Http404 в случае, если профиль не найден, что предотвращает Internal Server Error.
"""

@login_required(login_url='signin')
def settings(request):
    # get user info from login request
    user_profile = Profile.objects.get(user=request.user)

    if request.method == 'POST':

        # if there is no image
        if request.FILES.get('image') is None:
            image = user_profile.profileing
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileing = image
            user_profile.bio = bio.strip()
            user_profile.location = location
            user_profile.save()

        # if there is an image
        if request.FILES.get('image') is not None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileing = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()

        return redirect('settings')

    return render(request, 'setting.html', {
        "profile": user_profile
    })


@login_required(login_url="singin")
def upload(request):

    if request.method == "POST":
        #get username
        user = request.user.username
        image = request.FILES.get('image_upload')
        caption = request.POST['caption']

        new_post = Post.objects.create(user = user, image=image, caption=caption)
        new_post.save()


        return redirect('index')
    else:
        return redirect('settings')
        print("Error")
