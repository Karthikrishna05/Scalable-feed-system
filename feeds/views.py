from urllib import request
from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .serializer import PostSerializer
from core.models import Post

# Create your views here.
@api_view(['GET'])
def feed_pull_based(request):
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