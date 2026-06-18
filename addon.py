"""MessageBird SMS notification integration."""

from __future__ import annotations

from typing import Any, ClassVar, Dict, List

import httpx
from fastapi import APIRouter
from pydantic import BaseModel, Field, SecretStr

from app.addons.notifications.base import NotificationAddon
from app.addons.notifications.helpers import post_json_webhook
from app.addons.log import info, warning
from app.addons.config_serialization import dump_addon_config


class MessagebirdConfig(BaseModel):
    access_key: SecretStr = Field(default=..., description="MessageBird API access key")
    originator: str = Field(default=..., description="Sender name or phone number")

    @classmethod
    def config_model(cls):
        return cls


class MessagebirdAddon(NotificationAddon):
    addon_id: str = "messagebird"
    addon_name: str = "MessageBird"
    addon_description: str = "Send SMS notifications via MessageBird."
    addon_category: str = "notification"
    version: str = "1.0.0"
    is_enabled: bool = False
    supported_channels: ClassVar[list[str]] = ["sms"]

    _config: Dict[str, Any] | None = None
    _access_key: str | None = None
    _originator: str | None = None

    @classmethod
    def config_schema(cls):
        return MessagebirdConfig

    async def initialize(self, config: dict) -> None:
        validated = self.config_schema()(**config)
        self._config = dump_addon_config(validated)
        self._access_key = validated.access_key.get_secret_value()
        self._originator = validated.originator
        self.is_enabled = True
        info("MessageBird", "Initialized (originator={})", self._originator)

    async def validate_config(self, config: dict) -> None:
        from app.core.exceptions import ValidationError

        validated = self.config_schema()(**config)
        access_key = validated.access_key.get_secret_value()
        if not access_key:
            return
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(
                "https://rest.messagebird.com/balance",
                headers={"Authorization": f"AccessKey {access_key}"},
            )
        if resp.status_code == 401:
            raise ValidationError(message="Invalid access key — check your credentials")
        if resp.status_code == 403:
            raise ValidationError(
                message="Access key is valid but missing required permissions: balance:read"
            )
        if resp.status_code >= 400:
            raise ValidationError(message="MessageBird rejected the access key")

    async def shutdown(self) -> None:
        self._access_key = None
        self._originator = None
        self.is_enabled = False

    async def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html: bool = False,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("email", to)

    async def send_sms(self, to: str, body: str) -> Dict[str, Any]:
        if not self._access_key or not self._originator:
            return {"success": False, "message_id": "", "error": "Not configured", "to": to}

        payload = {
            "originator": self._originator,
            "recipients": [to],
            "body": body,
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.post(
                    "https://rest.messagebird.com/messages",
                    headers={
                        "Authorization": f"AccessKey {self._access_key}",
                        "Content-Type": "application/json",
                    },
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                return {
                    "success": True,
                    "message_id": data.get("id", ""),
                    "to": to,
                }
        except Exception as exc:
            warning("MessageBird", "send_sms to={} error: {}", to, exc)
            return {"success": False, "message_id": "", "error": str(exc), "to": to}

    async def send_push(
        self,
        to: str,
        title: str,
        body: str,
        data: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        return self.channel_not_supported("push", to)

    async def send_webhook(self, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        result = await post_json_webhook(url, payload)
        if not result.get("success"):
            warning("MessageBird", "send_webhook to={} error: {}", url, result.get("error"))
        return result

    def get_routers(self) -> List[APIRouter]:
        return []

    def get_admin_routes(self) -> List[APIRouter]:
        from app.addons.notifications.messagebird.routes import admin_router

        return [admin_router]

    def get_admin_templates(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "templates")

    def get_admin_static(self) -> str:
        from pathlib import Path

        return str(Path(__file__).resolve().parent / "static")
