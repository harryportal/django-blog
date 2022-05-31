from django.shortcuts import render, get_object_or_404
from .models import Post, Comment
from django.views.generic import ListView
from .form import EmailForm, CommentForm
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from taggit.models import Tag
from django.db.models import Count

"""class PostList(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/posts.html'"""

def post_list(request, tag_slug=None):
    posts = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])
    paginator = Paginator(posts, 3) # 3 posts in each page
    page = request.GET.get('page')
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1) # returns the first page
    except EmptyPage:
        posts = paginator.pagr(paginator.num_pages) # returns the last page
    context = {'page':page, 'posts':posts, 'tag':tag}
    return render(request, 'blog/post/posts.html', context)



def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post, status='published',
                             publish__year=year, publish__month=month,
                             publish__day=day)
    # lists of similar posts
    posts_tags_ids = post.tags.values_list('id',flat=True) # retrieve all the tags for the current post
    similar_posts = Post.published.filter(tags__in=posts_tags_ids).exclude(id=post.id) # similar posts except  the
    # current post
    similar_posts = similar_posts.annotate(name_tags=Count('tags')).order_by('-name_tags','-publish')[:4]

    # adding the comment logic
    comments = post.comments.filter(active=True)        # list of active comments for this post
    new_comment = None
    if request.method == 'POST':     # a comment was posted
        form = CommentForm(request.POST) # fills the form with the client data
        if form.is_valid():
            new_comment = form.save(commit=False) # create a new_comment object without saving it to the database
            new_comment.post = post
            new_comment.save()
    else:
        form = CommentForm()
    context = {'post': post, 'form':form, 'comments':comments, 'new_comment':new_comment,'similar_posts':similar_posts}
    return render(request, 'blog/post/detail.html', context)


def post_share(request, post_id):
    # retrieve post by id
    post = get_object_or_404(Post, id=post_id, status='published')
    sent = False
    if request.method == 'POST':  # if the form is submitted
        form = EmailForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # creates and send mail
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} invites you to read this post .. {post.title}"
            message = f"Read this post at {post_url}. {cd['name']} comments: {cd['comment']}"
            send_mail(subject, message,'mystrikeplans@gmail.com', [cd['to']])
            sent = True
            context = {'form': form, 'post': post, 'sent':sent}
            return render(request, 'blog/post/share.html', context)
    else:
        form = EmailForm()
        return render(request, 'blog/post/share.html', {'form': form, 'post': post})
