from datetime import timedelta

from care.emr.models.scheduling.booking import TokenBooking
from celery import shared_task
from django.utils import timezone

from care_notifications.common.types import EventType, ResourceType
from care_notifications.models.in_app_notification import InAppNotification
from care_notifications.models.outbound_notification import OutboundNotification
from care_notifications.settings import plugin_settings
from care_notifications.tasks.booking.notify_users import notify_reminder_users
from care_notifications.tasks.booking.send_reminder import send_reminder


@shared_task
def sweep_reminders():
    now = timezone.now()
    lead_cutoff = now + timedelta(minutes=int(plugin_settings.BOOKING_REMINDER_LEAD_MINUTES))

    due = TokenBooking.objects.filter(
        status="booked",
        token_slot__start_datetime__gt=now,
        token_slot__start_datetime__lte=lead_cutoff,
    )

    count = 0

    if plugin_settings.BOOKING_NOTIFY_REMINDER:
        sms_sent = OutboundNotification.objects.filter(
            resource_type=ResourceType.booking.value,
            event_type=EventType.booking_reminder.value,
        ).values_list("resource_id", flat=True)
        for booking_id in due.exclude(external_id__in=sms_sent).values_list("id", flat=True):
            send_reminder.apply_async(args=[booking_id], expires=300)
            count += 1

    # Care-team alert: independent toggle, deduped on its own InAppNotification.
    # ponytail: an empty-audience booking creates no InAppNotification, so it is
    # re-queued each sweep (a harmless no-op) until its slot leaves the window.
    if plugin_settings.BOOKING_NOTIFY_REMINDER_USERS:
        users_alerted = InAppNotification.objects.filter(
            resource_type=ResourceType.booking.value,
            event_type=EventType.booking_reminder.value,
        ).values_list("resource_id", flat=True)
        for booking_id in due.exclude(external_id__in=users_alerted).values_list("id", flat=True):
            notify_reminder_users.apply_async(args=[booking_id], expires=300)
            count += 1

    return count

