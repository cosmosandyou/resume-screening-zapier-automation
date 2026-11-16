"""Small, testable Zapier Catch Hook client."""
from __future__ import annotations

import json
import os
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ZapierDeliveryError(Exception):
    pass


def send_to_zapier(payload: dict[str, Any]) -> dict[str, Any]:
    url = os.getenv("ZAPIER_WEBHOOK_URL")
    if not url or "your-hook-id" in url:
        raise ZapierDeliveryError("ZAPIER_WEBHOOK_URL is not configured.")
    request = Request(url, data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(request, timeout=10) as response:  # nosec: URL is explicit admin configuration
            if not 200 <= response.status < 300:
                raise ZapierDeliveryError(f"Zapier returned HTTP {response.status}.")
            return {"delivered": True, "status": response.status}
    except HTTPError as exc:
        raise ZapierDeliveryError(f"Zapier returned HTTP {exc.code}.") from exc
    except URLError as exc:
        raise ZapierDeliveryError("Could not reach Zapier.") from exc
