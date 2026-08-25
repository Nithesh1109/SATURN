"""Explicit real-cloud smoke tests for SATURN.

These checks are intentionally opt-in and never execute desktop actions. They
validate the two external AI boundaries before the first end-to-end desktop
run: cloud text planning and optional cloud vision of a captured screenshot.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from saturn.ai.cloud_provider import CloudAIProvider
from saturn.ai.providers import AIRequest
from saturn.vision.cloud_provider import CloudVisionProvider
from saturn.vision.perception import ScreenCapture


def require_api_key() -> None:
    if not os.getenv("NVIDIA_API_KEY"):
        raise SystemExit(
            "NVIDIA_API_KEY is not set. Export it in this shell; never put the key in source code."
        )


def text_smoke() -> None:
    provider = CloudAIProvider()
    request = AIRequest(
        prompt="Return exactly this JSON object: {\"status\":\"ok\",\"component\":\"saturn-text\"}",
        system="Return JSON only. Do not use markdown fences.",
        max_tokens=64,
        temperature=0.0,
    )
    response = provider.generate(request)
    print(f"TEXT: provider={response.provider} model={response.model}")
    print(f"TEXT: response={response.text}")


def vision_smoke(image_path: str) -> None:
    provider = CloudVisionProvider()
    capture_path = Path(image_path)
    if not capture_path.is_file():
        raise SystemExit(f"Screenshot not found: {capture_path}")

    from PIL import Image

    with Image.open(capture_path) as image:
        width, height = image.size
    observation = provider.analyze(
        ScreenCapture(path=str(capture_path), width=width, height=height)
    )
    print(f"VISION: model={provider.model}")
    print(f"VISION: summary={observation.summary}")
    print(f"VISION: targets={len(observation.targets)}")


def main() -> int:
    parser = argparse.ArgumentParser(description="SATURN real cloud AI smoke test")
    parser.add_argument(
        "--vision-image",
        help="Existing screenshot to send to the configured vision model.",
    )
    args = parser.parse_args()

    require_api_key()
    text_smoke()
    if args.vision_image:
        vision_smoke(args.vision_image)
    print("SATURN cloud AI smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
