import os
from datetime import datetime, timezone

from locust import HttpUser, between, task

RW_ID = os.getenv("HYPEREVAC_RW_ID", "3f0c6b1e-0000-0000-0000-000000000001")
SEGMENT_ID = os.getenv("HYPEREVAC_SEGMENT_ID", "b7a6c5d4-0000-0000-0000-000000000032")
DEVICE_ID = os.getenv("HYPEREVAC_DEVICE_ID", "device-01")


class HyperEvacUser(HttpUser):
    wait_time = between(1, 3)

    @task(4)
    def get_hazards(self):
        self.client.get(f"/v1/hazards?rw={RW_ID}", name="/v1/hazards")

    @task(4)
    def get_evacuation_routes(self):
        self.client.get(
            "/v1/routes/evacuation?lat=4.4683&lng=97.9683",
            name="/v1/routes/evacuation",
        )

    @task(1)
    def submit_report(self):
        self.client.post(
            "/v1/reports",
            json={
                "device_id": DEVICE_ID,
                "segment_id": SEGMENT_ID,
                "tipe": "tertutup",
                "lat": 4.4683,
                "lng": 97.9683,
                "catatan": "Laporan simulasi load test",
                "dibuat_pada": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            },
            name="/v1/reports",
        )

    @task(1)
    def get_health(self):
        self.client.get("/v1/health", name="/v1/health")
