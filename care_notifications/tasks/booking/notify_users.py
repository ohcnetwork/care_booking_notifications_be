from care.emr.models.scheduling.booking import TokenBooking
from celery import shared_task
from django.utils import timezone

from care_notifications.common.types import EventType, ResourceType
from care_notifications.recipients.booking import booking_resource_recipients
from care_notifications.settings import plugin_settings
from care_notifications.tasks.common import notify_users

RETRY = {"autoretry_for": (Exception,), "retry_kwargs": {"max_retries": 3, "countdown": 60}}


def _notify_booking_users(booking_id: int, event_type: str, title_setting: str, body_setting: str):
    try:
        booking = TokenBooking.objects.select_related(
            "patient",
            "token_slot__resource__facility",
            "token_slot__resource__user",
            "token_slot__resource__location",
            "token_slot__resource__healthcare_service",
        ).get(id=booking_id)
    except TokenBooking.DoesNotExist:
        return

    resource = booking.token_slot.resource
    recipients = list(booking_resource_recipients(resource))
    if not recipients:
        return

    context = {
        "patient_name": booking.patient.name,
        "slot_start": timezone.localtime(booking.token_slot.start_datetime),
    }
    notify_users(
        recipients=recipients,
        event_type=event_type,
        resource_type=ResourceType.booking.value,
        resource_id=booking.external_id,
        title=getattr(plugin_settings, title_setting).format(**context),
        body=getattr(plugin_settings, body_setting).format(**context),
        facility_id=resource.facility.external_id,
        payload={"patient_id": str(booking.patient.external_id)},
    )


@shared_task(**RETRY)
def notify_confirmation_users(booking_id: int):
    _notify_booking_users(
        booking_id,
        EventType.booking_confirmation.value,
        "BOOKING_CONFIRMATION_USERS_TITLE",
        "BOOKING_CONFIRMATION_USERS_BODY",
    )


@shared_task(**RETRY)
def notify_cancel_users(booking_id: int):
    _notify_booking_users(
        booking_id,
        EventType.booking_cancellation.value,
        "BOOKING_CANCEL_USERS_TITLE",
        "BOOKING_CANCEL_USERS_BODY",
    )


@shared_task(**RETRY)
def notify_rescheduled_users(booking_id: int):
    _notify_booking_users(
        booking_id,
        EventType.booking_reschedule.value,
        "BOOKING_RESCHEDULED_USERS_TITLE",
        "BOOKING_RESCHEDULED_USERS_BODY",
    )
