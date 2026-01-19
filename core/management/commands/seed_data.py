import random
from faker import Faker
from django.core.management.base import BaseCommand
from core.models import User, Post, Follow

# We use a transaction to make the DB writes 100x faster
from django.db import transaction 

fake = Faker()

class Command(BaseCommand):
    help = 'Generates fake users, follows, and posts'

    def handle(self, *args, **kwargs):
        self.stdout.write("Seeding data... this may take a minute.")

        # 1. Create 1,000 Users
        users = []
        # Optimization: bulk_create is much faster than looping .save()
        for _ in range(1000):
            users.append(User(username=fake.user_name(), password="password"))

        User.objects.bulk_create(users, ignore_conflicts=True)
        all_users = list(User.objects.all())
        self.stdout.write(f"Created {len(all_users)} users.")

        # 2. Create Follows
        # We want User #1 (Our Test User) to follow 500 people (Simulating heavy load)
        test_user = all_users[0] 
        follows = []

        # Make User 1 follow 500 random people
        targets = random.sample(all_users[1:], 500)
        for target in targets:
            follows.append(Follow(follower=test_user, following=target))

        Follow.objects.bulk_create(follows, ignore_conflicts=True)
        self.stdout.write(f"User {test_user.username} is now following 500 people.")

        # 3. Create Posts
        # Generate 20,000 posts randomly across all users
        posts = []
        for _ in range(20000):
            author = random.choice(all_users)
            posts.append(Post(Author=author, content=fake.sentence()))

        Post.objects.bulk_create(posts, ignore_conflicts=True)
        self.stdout.write(f"Created 20,000 posts.")

        self.stdout.write(self.style.SUCCESS('Data seeding complete!'))