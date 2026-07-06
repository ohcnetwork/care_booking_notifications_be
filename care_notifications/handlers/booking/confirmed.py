from django.db import transaction

from care_notifications.settings import plugin_settings
from care_notifications.tasks import notify_confirmation, notify_confirmation_users


def handle_confirmed(booking) -> None:
    if plugin_settings.BOOKING_NOTIFY_CONFIRMATION:
        transaction.on_commit(lambda: notify_confirmation.delay(booking.id))
    if plugin_settings.BOOKING_NOTIFY_CONFIRMATION_USERS:
        transaction.on_commit(lambda: notify_confirmation_users.delay(booking.id))
