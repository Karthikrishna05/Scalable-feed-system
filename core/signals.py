from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Post
from feeds.tasks import fan_out_post

@receiver(post_save, sender=Post)
def post_created_trigger(sender, instance, created, **kwargs):
    if created:
        if instance.Author.is_celebrity:
            print(f"Skipping fan-out for celebrity: {instance.Author.username}")
            return
        fan_out_post.delay(instance.id, instance.Author.id)