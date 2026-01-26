from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Wait 1-5 seconds between tasks (simulates real human reading)
    wait_time = between(1, 5)

    def on_start(self):
        # 1. Login to get a Token (Simulated)
        pass

    @task(1)
    def test_pull_feed(self):
        self.client.get("/api/feeds/pull/", name="Pull Feed (SQL)")

    @task(3)
    def test_push_feed(self):
        self.client.get("/api/feeds/push/", name="Push Feed (Redis)")