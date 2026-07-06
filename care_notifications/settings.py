from typing import Any

import environ
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.dispatch import receiver
from rest_framework.settings import perform_import

from care_notifications.apps import PLUGIN_NAME

env = environ.Env()


class PluginSettings:
    def __init__(
        self,
        plugin_name: str = None,
        defaults: dict | None = None,
        import_strings: set | None = None,
        required_settings: set | None = None,
    ) -> None:
        if not plugin_name:
            raise ValueError("Plugin name must be provided")
        self.plugin_name = plugin_name
        self.defaults = defaults or {}
        self.import_strings = import_strings or set()
        self.required_settings = required_settings or set()
        self._cached_attrs = set()
        self.validate()

    def __getattr__(self, attr) -> Any:
        if attr not in self.defaults:
            raise AttributeError(f"Invalid setting: '{attr}'")

        val = self.defaults[attr]
        try:
            val = self.user_settings[attr]
        except KeyError:
            try:
                val = env(attr, cast=type(val))
            except environ.ImproperlyConfigured:
                pass

        if attr in self.import_strings:
            val = perform_import(val, attr)

        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    @property
    def user_settings(self) -> dict:
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, "PLUGIN_CONFIGS", {}).get(self.plugin_name, {})
        return self._user_settings

    def validate(self) -> None:
        for setting in self.required_settings:
            if not getattr(self, setting):
                raise ImproperlyConfigured(
                    f'The "{setting}" setting is required. '
                    f'Please set the "{setting}" in the environment or the {PLUGIN_NAME} plugin config.'
                )

        if self.WEBPUSH_NOTIFICATIONS_ENABLED:
            missing = [
                name
                for name in (
                    "WEBPUSH_VAPID_PUBLIC_KEY",
                    "WEBPUSH_VAPID_PRIVATE_KEY",
                    "WEBPUSH_VAPID_ADMIN_EMAIL",
                )
                if not getattr(self, name)
            ]
            if missing:
                raise ImproperlyConfigured(
                    f"WEBPUSH_NOTIFICATIONS_ENABLED is True but required settings are missing: "
                    f"{', '.join(missing)}. Set them via environment or the {PLUGIN_NAME} plugin config, "
                    f"or set WEBPUSH_NOTIFICATIONS_ENABLED=False to disable web push."
                )

    def reload(self) -> None:
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, "_user_settings"):
            delattr(self, "_user_settings")


DEFAULTS = {
    "TOKEN_BOOKING_NOTIFICATIONS_ENABLED": True,
    "BOOKING_REMINDER_LEAD_MINUTES": 60,
    "BOOKING_REMINDER_SWEEP_MINUTES": 1,
    "BOOKING_NOTIFY_CONFIRMATION": True,
    "BOOKING_NOTIFY_CONFIRMATION_USERS": True,
    "BOOKING_NOTIFY_REMINDER": True,
    "BOOKING_NOTIFY_REMINDER_USERS": True,
    "BOOKING_NOTIFY_CANCEL": True,
    "BOOKING_NOTIFY_CANCEL_USERS": True,
    "BOOKING_NOTIFY_RESCHEDULED": True,
    "BOOKING_NOTIFY_RESCHEDULED_USERS": True,
    "BOOKING_CONFIRMATION_SMS_TEXT": "Hi {patient_name}, your appointment is confirmed for {slot_start:%a, %d %b %Y %H:%M}. - Care",
    "BOOKING_REMINDER_SMS_TEXT": "Reminder: {patient_name}, your appointment is at {slot_start:%a, %d %b %Y %H:%M}. - Care",
    "BOOKING_CANCEL_SMS_TEXT": "Hi {patient_name}, your appointment for {slot_start:%a, %d %b %Y %H:%M} has been cancelled. - Care",
    "BOOKING_RESCHEDULED_SMS_TEXT": "Hi {patient_name}, your previous appointment has been rescheduled. - Care",
    "BOOKING_CONFIRMATION_USERS_TITLE": "New appointment: {patient_name}",
    "BOOKING_CONFIRMATION_USERS_BODY": "{slot_start:%a, %d %b %Y %H:%M}",
    "BOOKING_CANCEL_USERS_TITLE": "Appointment cancelled: {patient_name}",
    "BOOKING_CANCEL_USERS_BODY": "{slot_start:%a, %d %b %Y %H:%M}",
    "BOOKING_RESCHEDULED_USERS_TITLE": "Appointment rescheduled: {patient_name}",
    "BOOKING_RESCHEDULED_USERS_BODY": "{slot_start:%a, %d %b %Y %H:%M}",
    "BOOKING_REMINDER_USERS_TITLE": "Upcoming appointment: {patient_name}",
    "BOOKING_REMINDER_USERS_BODY": "{slot_start:%a, %d %b %Y %H:%M}",
    "DIAGNOSTIC_REPORT_NOTIFICATIONS_ENABLED": True,
    "DIAGNOSTIC_REPORT_NOTIFY_READY": True,
    "DIAGNOSTIC_REPORT_READY_TITLE": "Diagnostic report ready for {patient_name}",
    "DIAGNOSTIC_REPORT_READY_BODY": "",
    "SERVICE_REQUEST_NOTIFICATIONS_ENABLED": True,
    "SERVICE_REQUEST_NOTIFY_RAISED": True,
    "SERVICE_REQUEST_RAISED_TITLE": "New {service_request_title} request",
    "SERVICE_REQUEST_RAISED_BODY": "Patient: {patient_name}",
    "ENCOUNTER_NOTIFICATIONS_ENABLED": True,
    "ENCOUNTER_NOTIFY_IP_CREATED": True,
    "ENCOUNTER_IP_CREATED_TITLE": "New IP encounter: {patient_name}",
    "ENCOUNTER_IP_CREATED_BODY": "Location: {location_name}",
    "MEDICATION_NOTIFICATIONS_ENABLED": True,
    "MEDICATION_NOTIFY_NEAR_EXPIRY": True,
    "MEDICATION_NOTIFY_LOW_STOCK": True,
    "MEDICATION_STOCK_SWEEP_MINUTES": 60 * 24,
    "MEDICATION_NEAR_EXPIRY_LEAD_DAYS": 30,
    "MEDICATION_LOW_STOCK_THRESHOLD": 10,
    "MEDICATION_NEAR_EXPIRY_TITLE": "Medication near expiry: {product_name}",
    "MEDICATION_NEAR_EXPIRY_BODY": "Expires {expiration_date}. Location: {location_name}.",
    "MEDICATION_LOW_STOCK_TITLE": "Low stock: {product_name}",
    "MEDICATION_LOW_STOCK_BODY": "Remaining {net_content}. Location: {location_name}.",
    "WEBPUSH_NOTIFICATIONS_ENABLED": True,
    "WEBPUSH_VAPID_PUBLIC_KEY": "",
    "WEBPUSH_VAPID_PRIVATE_KEY": "",
    "WEBPUSH_VAPID_ADMIN_EMAIL": "",
}

REQUIRED_SETTINGS: set[str] = set()

plugin_settings = PluginSettings(PLUGIN_NAME, defaults=DEFAULTS, required_settings=REQUIRED_SETTINGS)


@receiver(setting_changed)
def reload_plugin_settings(*args, **kwargs) -> None:
    setting = kwargs["setting"]
    if setting == "PLUGIN_CONFIGS":
        plugin_settings.reload()
