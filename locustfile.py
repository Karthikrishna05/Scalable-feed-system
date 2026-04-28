"""
Locust load test — compares Pull (SQL) vs Push (Redis) feed strategies.

Usage:
  locust -f locustfile.py --host=http://127.0.0.1:8000 --users 100 --spawn-rate 10
"""

from locust import HttpUser, task, between


class FeedUser(HttpUser):
    wait_time = between(0.5, 2)

    @task(1)
    def test_pull_feed(self):
        with self.client.get(
            "/api/feeds/pull/", name="Pull Feed (SQL)", catch_response=True
        ) as response:
            if response.status_code == 200 and len(response.content) <= 2:
                response.failure("Empty feed — no posts returned")

    @task(3)
    def test_push_feed(self):
        with self.client.get(
            "/api/feeds/push/", name="Push Feed (Redis)", catch_response=True
        ) as response:
            if response.status_code == 200 and len(response.content) <= 2:
                response.failure("Empty Redis feed — run warm_redis first")