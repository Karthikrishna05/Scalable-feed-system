from urllib import request
from django.shortcuts import render
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializer import PostSerializer
from core.models import Post, User, Follow
from operator import attrgetter
from django.core.cache import cache


# Create your views here.
@api_view(['GET'])
def feed_pull_based(request):
    """
    Standard 'Pull' Model.
    1. Query DB to find who I follow.
    2. Query DB to find posts by those people.
    3. Sort by time (Expensive Join operation).
    """
    from core.models import User
    if request.user.is_anonymous:
        request.user = User.objects.first()
    #Fetch People who the requested user is following
    followed_users = request.user.following.values_list('following_id', flat=True)

    #Fetch posts from followed users with limit of 20 recent posts
    posts = Post.objects.filter(Author__in=followed_users).order_by('-created_at')[:20]

    #Serialize the posts
    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])

def hybrid_feed(request):
    user = request.user
    # Fetching precomputed feed from Redis for non-celebrity users
    key=f"feed:{user.id}"
    post_ids = cache.client.get_client().lrange(key, 0, 50)
    pushed_posts = list(Post.objects.filter(id__in=post_ids).select_related('Author'))
    # Fetching posts from celebrity users
    celebrity_ids = Follow.objects.filter(follower_id=user.id, following__is_celebrity=True).values_list('following_id', flat=True)
    celebrity_posts = list(Post.objects.filter(Author_id__in=celebrity_ids).select_related('Author').order_by('-created_at')[:50])
    # Merging and sorting posts
    full_feed= pushed_posts + celebrity_posts
    sorted_feed = sorted(full_feed, key=attrgetter('created_at'), reverse=True)[:20]

    serializer = PostSerializer(sorted_feed, many=True)
    return Response(serializer.data)