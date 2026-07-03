import json
import logging

from pywebpush import WebPushException, webpush

from care_notifications.models.web_push_subscription import WebPushSubscription
from care_notifications.settings import plugin_settings

logger = logging.getLogger(__name__)


def dispatch_webpush(*, recipients, title: str, body: str = "", payload: dict | None = None) -> int:
    user_ids = [user.id for user in recipients]
    if not user_ids:
        return 0

    subscriptions = WebPushSubscription.objects.filter(user_id__in=user_ids)
    data = json.dumps({"title": title, "body": body, **(payload or {})})
    vapid_claims = {"sub": f"mailto:{plugin_settings.WEBPUSH_VAPID_ADMIN_EMAIL}"}

    sent = 0
    dead_ids: list[int] = []
    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=data,
                vapid_private_key=plugin_settings.WEBPUSH_VAPID_PRIVATE_KEY,
                vapid_claims=vapid_claims,
            )
            sent += 1
        except WebPushException as exc:
            status = getattr(exc.response, "status_code", None)
            if status in (404, 410):
                dead_ids.append(sub.id)
            else:
                logger.exception("web push failed for subscription=%s", sub.id)

    if dead_ids:
        WebPushSubscription.objects.filter(id__in=dead_ids).delete()

    return sent
