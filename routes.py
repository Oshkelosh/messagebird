"""MessageBird addon routes."""

from __future__ import annotations

from typing import Any

from app.addons.notifications.shared_routes import build_notification_routers


def _parse_messagebird_config_form(form: Any) -> tuple[dict[str, Any], bool]:
    return (
        {
            "access_key": form.get("access_key", ""),
            "originator": form.get("originator", ""),
        },
        form.get("is_enabled") == "on",
    )


admin_router, jinja_env = build_notification_routers(
    "messagebird",
    template_name="messagebird_config.html",
    page_title="MessageBird Settings",
    secret_keys=("access_key",),
    parse_config_form=_parse_messagebird_config_form,
)
