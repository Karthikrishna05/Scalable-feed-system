from celery import shared_task
from django_redis import get_redis_connection
from core.models import Follow
from django.core.cache import cache

@shared_task
def fan_out_post(post_id,author_id):
    """
    The 'Fan-out-on-Write' logic.
    1. Fetch all followers of the author.
    2. Push the new post_id to each follower's Redis list.
    """
    # Fetch all followers of the author
    followers_ids = Follow.objects.filter(following_id=author_id).values_list('follower_id', flat=True)
    if not followers_ids:
        return f"Author {author_id} has no followers."
    
    # Redis pipeline for efficient bulk operations
    redis_client=cache.client.get_client()
    pipe = redis_client.pipeline()
    for user_id in followers_ids:
        key=f"feed:{user_id}"
        pipe.lpush(key, post_id)
        pipe.ltrim(key, 0, 150)
    pipe.execute()
    return f"Post {post_id} pushed/updated to {len(followers_ids)} followers."