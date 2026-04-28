from celery import shared_task
from django_redis import get_redis_connection
from core.models import Follow
from django.core.cache import cache


@shared_task
def fan_out_post(post_id, author_id):
    """Push post_id into each follower's Redis feed list."""
    followers_ids = Follow.objects.filter(
        following_id=author_id
    ).values_list('follower_id', flat=True)

    if not followers_ids:
        return f"Author {author_id} has no followers."

    # Pipeline batches all writes into a single round-trip
    redis_client = cache.client.get_client()
    pipe = redis_client.pipeline()
    for user_id in followers_ids:
        key = f"feed:{user_id}"
        pipe.lpush(key, post_id)
        pipe.ltrim(key, 0, 150)  # cap feed length
    pipe.execute()

    return f"Post {post_id} pushed to {len(followers_ids)} followers."