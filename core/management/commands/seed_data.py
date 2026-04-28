import random
from faker import Faker
from django.core.management.base import BaseCommand
from core.models import User, Post, Follow

fake = Faker()


class Command(BaseCommand):
    help = 'Generates fake users, follows, and posts'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data... this may take a minute.")

        # 1. Create 1,000 users
        users = []
        for _ in range(1000):
            users.append(User(username=fake.user_name(), password="password"))

        User.objects.bulk_create(users, ignore_conflicts=True)
        all_users = list(User.objects.all())
        self.stdout.write(f"Created {len(all_users)} users.")

        # 2. Make test user (first user) follow 500 random people
        test_user = all_users[0]
        follows = []
        targets = random.sample(all_users[1:], 500)
        for target in targets:
            follows.append(Follow(follower=test_user, following=target))

        Follow.objects.bulk_create(follows, ignore_conflicts=True)
        self.stdout.write(f"User {test_user.username} now follows 500 people.")

        # 3. Create 10,000 posts across all users
        posts = []
        for _ in range(10000):
            author = random.choice(all_users)
            posts.append(Post(Author=author, content=fake.sentence()))

        Post.objects.bulk_create(posts, ignore_conflicts=True)
        self.stdout.write("Created 10,000 posts.")

        # 4. Queue fan-out tasks (bulk_create bypasses signals, so we do it manually)
        self.stdout.write("Queuing fan-out tasks for Redis...")
        from feeds.tasks import fan_out_post

        created_posts = Post.objects.order_by('-id')[:10000]
        queued = 0
        for post in created_posts.iterator():
            fan_out_post.delay(post.id, post.Author_id)
            queued += 1
            if queued % 2000 == 0:
                self.stdout.write(f"  Queued {queued} / 10,000...")

        self.stdout.write(f"  Queued {queued} tasks total.")
        self.stdout.write(
            self.style.WARNING("Wait 30-60s for Celery to process before running Locust.")
        )
        self.stdout.write(self.style.SUCCESS('Done!'))