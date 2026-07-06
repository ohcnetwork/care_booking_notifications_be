from care.emr.models.diagnostic_report import DiagnosticReport
from celery import shared_task

from care_notifications.common.types import EventType, ResourceType
from care_notifications.recipients.encounter import care_team_members
from care_notifications.settings import plugin_settings
from care_notifications.tasks.common import notify_users


@shared_task(autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60})
def notify_diagnostic_report_ready(diagnostic_report_id: int):
    try:
        diagnostic_report = DiagnosticReport.objects.select_related(
            "service_request__requester", "patient", "encounter__facility"
        ).get(id=diagnostic_report_id)
    except DiagnosticReport.DoesNotExist:
        return

    recipients = set(care_team_members(diagnostic_report.encounter))
    if diagnostic_report.service_request.requester is not None:
        recipients.add(diagnostic_report.service_request.requester)
    if not recipients:
        return

    context = {"patient_name": diagnostic_report.patient.name}
    title = plugin_settings.DIAGNOSTIC_REPORT_READY_TITLE.format(**context)
    body = plugin_settings.DIAGNOSTIC_REPORT_READY_BODY.format(**context)

    notify_users(
        recipients=recipients,
        event_type=EventType.diagnostic_report_ready.value,
        resource_type=ResourceType.diagnostic_report.value,
        resource_id=diagnostic_report.external_id,
        title=title,
        body=body,
        facility_id=diagnostic_report.encounter.facility.external_id,
        payload={"patient_id": str(diagnostic_report.patient.external_id)},
    )
