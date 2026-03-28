import os
import threading
import time
import requests
from django.apps import AppConfig


class BooksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "books"

    def ready(self):
        
        if os.environ.get("RUN_MAIN") != "true":
            return
        
        if "migrate" in os.sys.argv or "makemigrations" in os.sys.argv:
            return

        thread = threading.Thread(target=self._keep_alive, daemon=True)
        thread.start()

    def _keep_alive(self):
        backend_url = os.getenv("RENDER_EXTERNAL_URL", "")
        if not backend_url:
            print("RENDER_EXTERNAL_URL not set — keep-alive disabled")
            return
        print(f"Keep-alive started → pinging {backend_url}/health/ every 14 min")
        while True:
            time.sleep(14 * 60)
            try:
                requests.get(f"{backend_url}/health/", timeout=10)
                print("✓ Keep-alive ping sent")
            except Exception as e:
                print(f"✗ Keep-alive failed: {e}")