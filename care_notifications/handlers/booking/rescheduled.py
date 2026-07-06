from django.db import transaction

from care_notifications.models.outbound_notification import OutboundNotification
from care_notifications.settings import plugin_settings
from care_notifications.tasks import notify_rescheduled, notify_rescheduled_users
from care_notifications.common.types import EventType, ResourceType


def handle_rescheduled(booking) -> None:
    confirmed = OutboundNotification.objects.filter(
        resource_type=ResourceType.booking.value,
        resource_id=booking.external_id,
        event_type=EventType.booking_confirmation.value,
    ).exists()

    if confirmed and plugin_settings.BOOKING_NOTIFY_RESCHEDULED:
        transaction.on_commit(lambda: notify_rescheduled.delay(booking.id))

    if plugin_settings.BOOKING_NOTIFY_RESCHEDULED_USERS:
        transaction.on_commit(lambda: notify_rescheduled_users.delay(booking.id))
