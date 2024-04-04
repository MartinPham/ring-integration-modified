# coding: utf-8
# vim:sw=4:ts=4:et:
"""Python Ring Other (Intercom) wrapper."""
import logging
import time
import uuid

from .generic import RingGeneric

from .const import (
    INTERCOM_ALLOWED_USERS,
    INTERCOM_INVITATIONS_DELETE_ENDPOINT,
    INTERCOM_INVITATIONS_ENDPOINT,
    INTERCOM_KINDS,
    INTERCOM_OPEN_ENDPOINT,
    INTERCOM_SETTINGS_ENDPOINT,
    INTERCOM_NOTIFICATION_SETTINGS_ENDPOINT,
    INTERCOM_SUBSCRIBE_ENDPOINT,
    INTERCOM_UNSUBSCRIBE_ENDPOINT,
)

_LOGGER = logging.getLogger(__name__)


class Other(RingGeneric):
    """Implementation for Ring Intercom."""

    def __init__(self, ring, device_id, shared=False):
        super().__init__(ring, device_id)
        self.shared = shared

    @property
    def family(self):
        """Return Ring device family type."""
        return "other"

    @property
    def model(self):
        """Return Ring device model name."""
        if self.kind in INTERCOM_KINDS:
            return "Intercom"
        return None

    def has_capability(self, capability):
        """Return if device has specific capability."""
        if capability == "open":
            return self.kind in INTERCOM_KINDS
        return False

    @property
    def battery_life(self):
        """Return battery life."""
        if self.kind in INTERCOM_KINDS:
            if self._attrs.get("battery_life") is None:
                return None

            value = int(self._attrs.get("battery_life", 0))
            if value and value > 100:
                value = 100

            return value
        return None

    @property
    def subscribed(self):
        """Return if is online."""
        if self.kind in INTERCOM_KINDS:
            result = self._attrs.get("subscribed")
            if result is None:
                return False
            return True
        return None

    @property
    def subscriptions(self):
        """Return event type subscriptions."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("subscriptions", []).get("event_types", [])
        return None

    @property
    def has_subscription(self):
        """Return boolean if the account has subscription."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("features").get("show_recordings")
        return None

    @property
    def doorbell_volume(self):
        """Return doorbell volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("doorbell_volume")
        return None

    @property
    def user_id(self):
        """Return user_id."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("health").get("user_id")
        return None

    @property
    def mic_volume(self):
        """Return mic volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("mic_volume")
        return None

    @property
    def voice_volume(self):
        """Return voice volume."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("settings").get("voice_volume")
        return None

    @property
    def connection_status(self):
        """Return connection status."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("alerts").get("connection")
        return None

    @property
    def location_id(self):
        """Return location id."""
        if self.kind in INTERCOM_KINDS:
            return self._attrs.get("location_id", None)
        return None

    @property
    def allowed_users(self):
        """Return list of users allowed or invited to access"""
        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_ALLOWED_USERS.format(self.location_id)
            return self._ring.query(url, method="GET").json()

        return None

    def set_volume(self, key, volume):
        """Set volume"""

        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_SETTINGS_ENDPOINT.format(self.id)
            payload = {"volume_settings": {}}
            payload["volume_settings"][key] = int(volume)

            self._ring.query(url, method="PATCH", json=payload).json()
            self._ring.update_devices()

        return False

    def set_unlock_notification(self, flag):
        """Set unlock notification"""

        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_NOTIFICATION_SETTINGS_ENDPOINT.format(self.id)
            method = "POST" if flag else "DELETE"

            self._ring.query(url, method=method)
            self._ring.update_devices()

        return False

    def set_alert_notification(self, flag):
        """Set alert notification"""

        if self.kind in INTERCOM_KINDS:
            url = (
                INTERCOM_SUBSCRIBE_ENDPOINT.format(self.id)
                if flag
                else INTERCOM_UNSUBSCRIBE_ENDPOINT.format(self.id)
            )

            self._ring.query(url, method="POST", json={})
            self._ring.update_devices()

        return False

    def open_door(self):
        """Open the door"""

        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_OPEN_ENDPOINT.format(self.id)
            request_id = str(uuid.uuid4())
            request_timestamp = int(time.time() * 1000)
            payload = {
                "command_name": "device_rpc",
                "request": {
                    "id": request_id,
                    "jsonrpc": "2.0",
                    "method": "unlock_door",
                    "params": {
                        "command_timeout": 5,
                        "door_id": 0,
                        "issue_time": request_timestamp,
                        "user_id": self.user_id,
                    },
                },
            }

            response = self._ring.query(url, method="PUT", json=payload).json()
            self._ring.update_devices()
            if response.get("result", -1).get("code", -1) == 0:
                return True

        return False

    def invite_access(self, email):
        """Invite user"""

        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_INVITATIONS_ENDPOINT.format(self.location_id)
            payload = {
                "invitation": {
                    "doorbot_ids": [self.id],
                    "invited_email": email,
                    "group_ids": [],
                }
            }
            self._ring.query(url, method="POST", json=payload)
            return True

        return False

    def remove_access(self, user_id):
        """Remove user access or invitation"""

        if self.kind in INTERCOM_KINDS:
            url = INTERCOM_INVITATIONS_DELETE_ENDPOINT.format(self.location_id, user_id)
            self._ring.query(url, method="DELETE")
            return True

        return False
