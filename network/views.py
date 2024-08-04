from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django import forms
from django.core.paginator import Paginator

from .models import *


class NewPostForm(forms.Form):
    new_post_text = forms.CharField(widget=forms.Textarea(attrs={
        'placeholder' : 'Make a new post...',
        'required' : 'True',
        'class' : 'form-control',
        'maxlength': '500',  
        'rows': 2,          
        'cols': 40
    }), label="")


def index(request):
    newPostForm = NewPostForm()

    if request.method == 'POST':
        post_text = request.POST.get('new_post_text')
        user = User.objects.get(pk=request.user.id)

        post = Post(user=user, content=post_text)
        post.save()

        return HttpResponseRedirect(reverse('index'))

    posts_list = Post.objects.all().order_by('-timestamp')
    paginator = Paginator(posts_list, 10)  # 10 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, "network/index.html" ,{
        'newPostForm' : newPostForm,
        'posts' : posts
    })

def profile(request, username):
    profile = User.objects.get(username = username)
    follower = User.objects.get(pk=request.user.id)

    posts_list = Post.objects.filter(user = profile).order_by('-timestamp')
    paginator = Paginator(posts_list, 10)  # 10 posts per page

    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)


    if Follower.objects.filter(user = follower, followers = profile).exists():
        following = True
    
    else:
        following = False
    
    return render(request, 'network/profile.html', {
        'profile' : profile,
        'posts' : posts,
        'following'  : following
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
    
def follow(request, username):
    follow = User.objects.get(username=username)
    follower = User.objects.get(pk=request.user.id)

    if Follower.objects.filter(user = follower, followers = follow).exists():
        item = Follower.objects.filter(user = follower, followers = follow)
        item.delete()
    else:
        following = Follower(user = follower, followers = follow)
        following.save()

    return HttpResponseRedirect(reverse("profile",kwargs={
        'username' : username
    }))

def followingpage(request):
    newPostForm = NewPostForm()
    user = User.objects.get(pk=request.user.id)
    peopleFollowed = Follower.objects.filter(user=user).values_list('followers', flat=True)
    posts_list = Post.objects.filter(user__in=peopleFollowed).order_by('-timestamp')
    
    paginator = Paginator(posts_list, 10)  # 10 posts per page
    page_number = request.GET.get('page')
    posts = paginator.get_page(page_number)

    return render(request, "network/following.html", {
        'posts' : posts,
        'newPostForm' : newPostForm
    })

def edit(request, postId):
    
    post = Post.objects.get(pk = postId)

    if request.method == 'POST':
        post_text = request.POST.get('new_post_text')
        post.content = post_text
        post.save()
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'GET':

        return render(request, 'network/edit.html', {
            'post' : post,
            'newpostform' : NewPostForm(initial={'new_post_text' : post.content})
        })

def like_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    user = User.objects.get(pk=request.user.id)
    liked = False

    try:
        like, created = Like.objects.get_or_create(user=user, post=post)
        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        likes_count = post.likes.count()
        return JsonResponse({'success': True, 'liked': liked, 'likes_count': likes_count})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
