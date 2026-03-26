"""LMS API client service."""

import httpx
from typing import Any


class LMSClient:
    """Client for the LMS backend API."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Lazy httpx client with auth headers."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=10.0,
            )
        return self._client

    def get_items(self) -> list[dict[str, Any]]:
        """Fetch all items (labs, tasks) from the backend."""
        response = self.client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict[str, Any]]:
        """Fetch pass rates for a specific lab. Returns list of tasks with scores."""
        response = self.client.get(
            "/analytics/pass-rates",
            params={"lab": lab},
        )
        response.raise_for_status()
        return response.json()

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            self._client.close()
