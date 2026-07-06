from celery import Celery, current_app

from care_notifications.settings import plugin_settings
from care_notifications.tasks.booking.notify_cancel import notify_cancel
from care_notifications.tasks.booking.notify_users import (
    notify_cancel_users,
    notify_confirmation_users,
    notify_reminder_users,
    notify_rescheduled_users,
)
from care_notifications.tasks.booking.notify_confirmation import notify_confirmation
from care_notifications.tasks.booking.notify_rescheduled import notify_rescheduled
from care_notifications.tasks.booking.send_reminder import send_reminder
from care_notifications.tasks.booking.sweep_reminders import sweep_reminders
from care_notifications.tasks.diagnostic_report.notify_ready import (
    notify_diagnostic_report_ready,
)
from care_notifications.tasks.encounter.notify_ip_created import (
    notify_encounter_ip_created,
)
from care_notifications.tasks.medication.notify_low_stock import (
    notify_medication_low_stock,
)
from care_notifications.tasks.medication.notify_near_expiry import (
    notify_medication_near_expiry,
)
from care_notifications.tasks.medication.sweep import sweep_medication_stock
from care_notifications.tasks.service_request.notify_raised import (
    notify_service_request_raised,
)


@current_app.on_after_finalize.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    if (
        plugin_settings.TOKEN_BOOKING_NOTIFICATIONS_ENABLED
        and (
            plugin_settings.BOOKING_NOTIFY_REMINDER
            or plugin_settings.BOOKING_NOTIFY_REMINDER_USERS
        )
    ):
        sweep = max(1, int(plugin_settings.BOOKING_REMINDER_SWEEP_MINUTES))
        sender.add_periodic_task(
            sweep * 60,
            sweep_reminders.s(),
            name="care_notifications.sweep_reminders",
        )

    if plugin_settings.MEDICATION_NOTIFICATIONS_ENABLED:
        medication_sweep = max(1, int(plugin_settings.MEDICATION_STOCK_SWEEP_MINUTES))
        sender.add_periodic_task(
            medication_sweep * 60,
            sweep_medication_stock.s(),
            name="care_notifications.sweep_medication_stock",
        )
