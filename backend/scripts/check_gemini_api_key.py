"""Quick health check for Gemini API keys.

Usage:
  python scripts/check_gemini_api_key.py
  python scripts/check_gemini_api_key.py --model gemini-3.1-flash-lite

Environment variables:
  GOOGLE_API_KEY    Single Gemini API key
  GEMINI_API_KEYS   Comma-separated list of keys to try in order
  GEMINI_MODEL      Default model name if --model is not provided
"""

from __future__ import annotations

from contextlib import contextmanager
import argparse
import os
from typing import Iterable

from dotenv import dotenv_values, load_dotenv
from google import genai
from google.genai import errors


def load_keys() -> list[str]:
    """Load API keys from env, preferring the source with the most keys."""

    def split_keys(raw: str | None) -> list[str]:
        if not raw:
            return []
        return [key.strip() for key in raw.split(",") if key.strip()]

    env_values = dotenv_values(".env")
    candidates = [
        split_keys(os.getenv("GEMINI_API_KEYS")),
        split_keys(os.getenv("GEMINI_API_KEY")),
        split_keys(os.getenv("GOOGLE_API_KEY")),
        split_keys(env_values.get("GEMINI_API_KEYS")),
        split_keys(env_values.get("GEMINI_API_KEY")),
        split_keys(env_values.get("GOOGLE_API_KEY")),
    ]

    return max(candidates, key=len, default=[])


def masked_key(key: str) -> str:
    if len(key) <= 8:
        return "****"
    return f"{key[:4]}...{key[-4:]}"


@contextmanager
def isolated_gemini_env(api_key: str):
    """Temporarily remove conflicting Gemini env vars while testing one key."""
    keys_to_restore = {
        name: os.environ.get(name)
        for name in ("GOOGLE_API_KEY", "GEMINI_API_KEY", "GEMINI_API_KEYS")
    }
    try:
        for name in keys_to_restore:
            os.environ.pop(name, None)
        os.environ["GOOGLE_API_KEY"] = api_key
        yield
    finally:
        for name, value in keys_to_restore.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def try_key(api_key: str, model: str) -> tuple[bool, str]:
    """Attempt a tiny Gemini request and return a status tuple."""
    with isolated_gemini_env(api_key):
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model,
            contents="Reply with exactly: OK",
        )
    text = (getattr(response, "text", None) or "").strip()
    if text:
        return True, text
    return True, "Request succeeded, but no text response was returned."


def iter_keys(keys: list[str]) -> Iterable[tuple[int, str]]:
    for index, key in enumerate(keys, start=1):
        yield index, key


def main() -> int:
    load_dotenv(override=False)

    parser = argparse.ArgumentParser(description="Check whether Gemini API keys work.")
    parser.add_argument(
        "--model",
        default=os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite"),
        help="Gemini model name to test.",
    )
    args = parser.parse_args()

    keys = load_keys()
    if not keys:
        print("No API key found. Set GOOGLE_API_KEY or GEMINI_API_KEYS in your environment.")
        return 2

    print(f"Testing model: {args.model}")
    print(f"Keys found: {len(keys)}")

    any_success = False
    for index, key in iter_keys(keys):
        print(f"\n[{index}/{len(keys)}] Testing key {masked_key(key)}")
        try:
            ok, message = try_key(key, args.model)
            if ok:
                any_success = True
                print("PASS")
                print(message)
            else:
                print("FAIL")
                print(message)
        except errors.APIError as exc:
            print("FAIL")
            print(f"Gemini API error: {exc}")
        except Exception as exc:
            print("FAIL")
            print(f"Unexpected error: {exc}")

    if any_success:
        print("\nAt least one Gemini API key worked.")
        return 0

    print("\nNo configured Gemini API key worked.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())