"""Minimal unit tests for the messagebird addon."""

from app.addons.notifications.messagebird.addon import MessagebirdAddon


def test_addon_identity():
    assert MessagebirdAddon.addon_id == "messagebird"
    assert MessagebirdAddon.addon_category == "notification"
