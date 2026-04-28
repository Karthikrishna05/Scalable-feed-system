"""
Re-populate Redis feeds from existing DB posts.

Useful after Redis restart/flush or when setting up from an existing database.
Requires Celery to be running.

Usage:
  python manage.py warm_redis              # default: 5000 posts
  python manage.py warm_redis --limit 10000
"""

from django.core.management.base import BaseCommand
from core.models import Post


class Command(BaseCommand):
    help = "Queue Celery fan-out tasks for the N most recent posts"

    def add_arguments(self, parser):
        parser.add_argument(
            '--limit', type=int, default=5000,
            help='Number of recent posts to fan-out (default: 5000)',
        )

    def handle(self, *args, **options):
        limit = options['limit']
        from feeds.tasks import fan_out_post

        posts = Post.objects.order_by('-id')[:limit]
        total = posts.count()

        if total == 0:
            self.stdout.write(self.style.ERROR(
                "No posts found. Run seed_data first."
            ))
            return

        self.stdout.write(f"Queuing {total} fan-out tasks...")
        queued = 0
        for post in posts.iterator():
            fan_out_post.delay(post.id, post.Author_id)
            queued += 1
            if queued % 500 == 0:
                self.stdout.write(f"  Queued {queued} / {total}...")

        self.stdout.write(f"  Queued {queued} tasks total.")
        self.stdout.write(self.style.WARNING(
            "Wait 30-60s for Celery to process before running Locust."
        ))
        self.stdout.write(self.style.SUCCESS("Done!"))
