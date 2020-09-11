from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.views.decorators.cache import cache_page

from .models import Post, Group, Comment, Follow
from .forms import PostForm, CommentForm


def index(request):
    template_name = "index.html"
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        'post_list': post_list,
        'page': page,
        'paginator': paginator
    }
    return render(request, template_name, context)


def group_posts(request, slug):
    template_name = 'group.html'
    group = get_object_or_404(Group, slug=slug)
    post_list = group.groups.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)

    context = {
        "group": group,
        "post_list": post_list,
        'page': page,
        'paginator': paginator
    }
    return render(request, template_name, context)


@login_required
def new_post(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('index')
    return render(request, 'new.html', {'form': form})


def profile(request, username=None):
    author = get_object_or_404(get_user_model(), username=username)
    post_list = author.posts.all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    count_post = author.posts.all().count()
    followers = author.follower.all().count()
    followings = author.following.all().count()
    context = {
        'author': author,
        'page': page,
        'paginator': paginator,
        'count_post': count_post,
        'followers': followers,
        'followings': followings,
    }
    return render(request, 'profile.html', context)


def post_view(request, username, post_id):
    author = get_object_or_404(get_user_model(), username=username)
    post = get_object_or_404(Post, id=post_id)
    count_post = author.posts.all().count()
    form = CommentForm()
    comments = post.comments.all()
    context = {
        'author': author,
        'post': post,
        'count_post': count_post,
        'form': form,
        'comments': comments,
        }
    return render(request, 'post.html', context)


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(get_user_model(), username=username)
    edit_post = get_object_or_404(Post, id=post_id)
    if edit_post.author != request.user:
        return redirect(reverse('post', args=[username, post_id]))
    form = PostForm(request.POST or None, files=request.FILES or None,
                    instance=edit_post)
    if form.is_valid():
        form.save()
        return redirect(reverse('post', args=[username, post_id]))
    context = {
        'edit_post': edit_post,
        'author': author,
        'form': form,
        'is_edit': True,
        }
    return render(request, 'new.html', context)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment_new = form.save(commit=False)
        comment_new.author = request.user
        comment_new.post = post
        form.save()
    return redirect(reverse('post', args=[username, post_id]))


@login_required
def follow_index(request):
    post_list = Post.objects.filter(author__following__user=request.user)
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    context = {
        'post_list': post_list,
        'page': page,
        'paginator': paginator
    }
    return render(request, 'follow.html', context)


@login_required
def profile_follow(request, username):
    user = request.user
    author = get_object_or_404(get_user_model(), username=username)
    Follow.objects.get_or_create(user=user, author=author)
    return redirect('profile', username=username)


@login_required
def profile_unfollow(request, username):
    user = request.user
    author = get_object_or_404(get_user_model(), username=username)
    follow_obj = Follow.objects.filter(user=user, author=author)
    follow_obj.delete()
    return redirect("profile", username=username)
