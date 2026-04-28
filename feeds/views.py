from urllib import request
from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .serializer import PostSerializer
from core.models import Post, User, Follow
from operator import attrgetter
from django.core.cache import cache


@api_view(['GET'])
def feed_pull_based(request):
    """Pull model — queries DB on every request."""
    from core.models import User
    if request.user.is_anonymous:
        request.user = User.objects.first()

    followed_users = request.user.following.values_list('following_id', flat=True)

    # select_related prevents N+1 on Author (serializer needs username, is_celebrity)
    posts = Post.objects.filter(
        Author__in=followed_users
    ).select_related('Author').order_by('-created_at')[:20]

    serializer = PostSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def hybrid_feed(request):
    """Hybrid — push for regular users, pull for celebrity posts."""
    from core.models import User
    if request.user.is_anonymous:
        request.user = User.objects.first()
    user = request.user

    # Pre-computed feed from Redis
    key = f"feed:{user.id}"
    post_ids = cache.client.get_client().lrange(key, 0, 50)
    pushed_posts = list(Post.objects.filter(id__in=post_ids).select_related('Author'))

    # Pull celebrity posts on-demand (avoids fan-out to millions of followers)
    celebrity_ids = Follow.objects.filter(
        follower_id=user.id, following__is_celebrity=True
    ).values_list('following_id', flat=True)
    celebrity_posts = list(
        Post.objects.filter(Author_id__in=celebrity_ids)
        .select_related('Author').order_by('-created_at')[:50]
    )

    # Merge and sort
    full_feed = pushed_posts + celebrity_posts
    sorted_feed = sorted(full_feed, key=attrgetter('created_at'), reverse=True)[:20]

    serializer = PostSerializer(sorted_feed, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def feed_push_only(request):
    """Push model — reads pre-computed feed from Redis."""
    from core.models import User
    if request.user.is_anonymous:
        request.user = User.objects.first()
    user = request.user

    key = f"feed:{user.id}"
    post_ids = cache.client.get_client().lrange(key, 0, 20)
    if not post_ids:
        return Response([])
    post_ids = [int(pid) for pid in post_ids]

    # in_bulk gives us {id: obj} dict; select_related avoids N+1 on Author
    posts_dict = Post.objects.filter(id__in=post_ids).select_related('Author').in_bulk()

    # Preserve Redis ordering (most recent first)
    ordered_posts = [posts_dict[pid] for pid in post_ids if pid in posts_dict]

    serializer = PostSerializer(ordered_posts, many=True)
    return Response(serializer.data)