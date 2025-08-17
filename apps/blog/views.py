
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, F
from .models import BlogPost, BlogCategory, BlogComment
from .forms import BlogCommentForm

def blog_list(request):
    posts = BlogPost.objects.filter(status='published').select_related('category', 'author')
    categories = BlogCategory.objects.filter(is_active=True)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(BlogCategory, slug=category_slug)
        posts = posts.filter(category=category)
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(excerpt__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__icontains=search_query)
        )
    
    # Featured posts
    featured_posts = posts.filter(is_featured=True)[:3]
    
    # Pagination
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'featured_posts': featured_posts,
        'search_query': search_query,
        'selected_category': category_slug,
        'page_title': 'Blog'
    }
    return render(request, 'blog/blog_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug, status='published')
    
    # Increment view count
    BlogPost.objects.filter(pk=post.pk).update(views_count=F('views_count') + 1)
    
    # Get approved comments
    comments = post.comments.filter(is_approved=True).select_related('author')
    
    # Related posts
    related_posts = BlogPost.objects.filter(
        category=post.category,
        status='published'
    ).exclude(pk=post.pk)[:3]
    
    # Comment form
    comment_form = BlogCommentForm()
    
    if request.method == 'POST' and request.user.is_authenticated:
        comment_form = BlogCommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Şərhiniz uğurla göndərildi! Moderasiyadan sonra dərc ediləcək.')
            return redirect('blog:post_detail', slug=post.slug)
    
    context = {
        'post': post,
        'comments': comments,
        'related_posts': related_posts,
        'comment_form': comment_form,
        'page_title': post.title
    }
    return render(request, 'blog/post_detail.html', context)

def category_posts(request, slug):
    category = get_object_or_404(BlogCategory, slug=slug, is_active=True)
    posts = BlogPost.objects.filter(category=category, status='published').select_related('author')
    
    paginator = Paginator(posts, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'category': category,
        'page_title': f'{category.name} - Blog'
    }
    return render(request, 'blog/category_posts.html', context)
