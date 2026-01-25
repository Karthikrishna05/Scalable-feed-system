from locust import HttpUser, task, between

class WebsiteUser(HttpUser):
    # Wait 1-5 seconds between tasks (simulates real human reading)
    wait_time = between(1, 5)

    def on_start(self):
        # 1. Login to get a Token (Simulated)
        # In a real test, you'd post to /api/token/. 
        # For simplicity, we assume Basic Auth or Session is active.
        # We'll rely on the Django admin session or a hardcoded header.
        pass

    @task(1)
    def test_pull_feed(self):
        # We add a header assuming you might use Token auth later
        # For now, this just hits the endpoint.
        self.client.get("/api/feeds/pull/", name="Pull Feed (SQL)")

    @task(3)
    def test_push_feed(self):
        # We weight this higher (3) because it's faster
        self.client.get("/api/feeds/push/", name="Push Feed (Redis)")