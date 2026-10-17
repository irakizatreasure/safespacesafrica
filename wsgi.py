"""Production WSGI entry point used by Gunicorn and compatible hosts."""

import os


def validate_production_environment() -> None:
    if os.environ.get("SISP_ENV", "").lower() != "production":
        return

    email = os.environ.get("SISP_ADMIN_EMAIL", "").strip()
    password = os.environ.get("SISP_ADMIN_PASSWORD", "")
    example_domain = email.rsplit("@", 1)[-1].lower() if "@" in email else ""
    if (
        "@" not in email
        or example_domain in {"example.com", "example.net", "example.org"}
        or len(password) < 14
        or "replace-with" in password.lower()
    ):
        raise RuntimeError(
            "Production startup requires SISP_ADMIN_EMAIL and a unique "
            "SISP_ADMIN_PASSWORD of at least 14 characters. Set both in the host's secret manager."
        )
    if os.environ.get("SISP_COOKIE_SECURE", "").lower() != "true":
        raise RuntimeError("Production startup requires SISP_COOKIE_SECURE=true behind HTTPS.")

    provider = os.environ.get("SISP_AI_PROVIDER", "").lower()
    if provider and provider not in {"openai", "gemini"}:
        raise RuntimeError("SISP_AI_PROVIDER must be openai or gemini when configured.")
    if provider and not all(os.environ.get(key) for key in ("SISP_AI_API_KEY", "SISP_AI_MODEL")):
        raise RuntimeError("Configured AI requires SISP_AI_API_KEY and SISP_AI_MODEL in the host's secret manager.")


validate_production_environment()

from app import Application  # noqa: E402


application = Application()
