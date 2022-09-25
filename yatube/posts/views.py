from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page

from .models import Post, Group, User, Comment, Follow
from .forms import PostForm, CommentForm

POSTS_ON_SCREEN = 10


def add_paginator(request, object_list, per_page=POSTS_ON_SCREEN):
    paginator = Paginator(object_list, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


@cache_page(20, key_prefix='index_page')
def index(request):
    post_list = Post.objects.select_related('author').all()
    context = {
        'page_obj': add_paginator(request, post_list),
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = group.posts.select_related('author').all()
    context = {
        'group': group,
        'page_obj': add_paginator(request, post_list),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    post_list = author.posts.select_related('author')
    if request.user.is_authenticated and Follow.objects.filter(
            user=request.user, author=author
    ).exists():
        following = True
    else:
        following = False

    context = {
        'author': author,
        'page_obj': add_paginator(request, post_list),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_details(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'form': CommentForm(),
        'comments': Comment.objects.filter(post=post)
    }
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)
    return render(request, 'posts/create_post.html', {'form': form})


def author_only(func):
    def check_author(request, post_id):
        post = get_object_or_404(Post, pk=post_id)
        if request.user.is_authenticated:
            if request.user == post.author:
                return func(request, post_id)
            return redirect('posts:post_details', post_id)
        return redirect('users:login')
    return check_author


@author_only
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_details', post_id)

    context = {
        'form': form,
        'is_edit': True,
    }
    return render(request, 'posts/create_post.html', context)


@login_required()
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_details', post_id=post_id)


@login_required()
def follow_index(request):
    follow_list = Post.objects.filter(author__following__user=request.user)
    context = {
        'page_obj': add_paginator(request, follow_list),
    }
    return render(request, 'posts/follow.html', context)


@login_required()
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user == author:
        return redirect('posts:profile', username=username)
    Follow.objects.get_or_create(
        user=request.user,
        author=author
    )
    return redirect('posts:profile', username=username)


@login_required()
def profile_unfollow(request, username):
    Follow.objects.filter(
        user=request.user,
        author=get_object_or_404(User, username=username)
    ).delete()
    return redirect('posts:profile', username=username)
