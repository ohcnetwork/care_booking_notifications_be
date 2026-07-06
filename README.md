# care_notifications_be

CARE plug that sends notifications to patients (SMS) and clinicians (in-app + web push).

## Currently supports

1. Token bookings — confirm, reminder, cancel, reschedule. (patient SMS + user in-app/web push)
2. Service requests — raised. (in-app)
3. Diagnostic reports — ready. (in-app)
4. Encounters — IP admission with location assigned. (in-app)
5. Medication stock — near expiry, low stock. (in-app)
6. Web push — every clinician (in-app) notification is also delivered to subscribed browsers/devices. (web push)

## Install

Add to `plug_config.py`:

```python
care_notifications = Plug(
    name="care_notifications",
    package_name="git+https://github.com/ohcnetwork/care_notifications_be.git",
    version="@main",
    configs={},
)
plugs = [care_notifications]
```

Then `make build && make up`.

## Settings

### Token bookings (SMS)

| Key | Default | Description |
|---|---|---|
| `TOKEN_BOOKING_NOTIFICATIONS_ENABLED` | `True` | Master switch for all token booking notifications. |
| `BOOKING_REMINDER_LEAD_MINUTES` | `60` | Minutes before slot start to send the reminder. |
| `BOOKING_REMINDER_SWEEP_MINUTES` | `1` | How often the reminder sweep runs. |
| `BOOKING_NOTIFY_CONFIRMATION` | `True` | Send confirmation SMS to the patient. |
| `BOOKING_NOTIFY_CONFIRMATION_USERS` | `True` | Send an in-app / web-push alert to the users behind the booked resource — practitioner → the practitioner; healthcare_service → its managing-org members; location → the location's org members. |
| `BOOKING_NOTIFY_REMINDER` | `True` | Send reminder SMS. |
| `BOOKING_NOTIFY_REMINDER_USERS` | `True` | Send a reminder in-app / web-push alert to the resource's users (same audience rule as confirmation) when a booking's slot enters the lead window. |
| `BOOKING_NOTIFY_CANCEL` | `True` | Send cancellation SMS. |
| `BOOKING_NOTIFY_CANCEL_USERS` | `True` | Send a cancellation in-app / web-push alert to the resource's users (same audience rule as confirmation). |
| `BOOKING_NOTIFY_RESCHEDULED` | `True` | Send reschedule SMS. |
| `BOOKING_NOTIFY_RESCHEDULED_USERS` | `True` | Send a reschedule in-app / web-push alert to the resource's users (same audience rule as confirmation). |
| `BOOKING_CONFIRMATION_SMS_TEXT` | `Hi {patient_name}, your appointment is confirmed for {slot_start:%a, %d %b %Y %H:%M}. - Care` | Confirmation SMS body. |
| `BOOKING_REMINDER_SMS_TEXT` | `Reminder: {patient_name}, your appointment is at {slot_start:%a, %d %b %Y %H:%M}. - Care` | Reminder SMS body. |
| `BOOKING_CANCEL_SMS_TEXT` | `Hi {patient_name}, your appointment for {slot_start:%a, %d %b %Y %H:%M} has been cancelled. - Care` | Cancel SMS body. |
| `BOOKING_RESCHEDULED_SMS_TEXT` | `Hi {patient_name}, your previous appointment has been rescheduled. - Care` | Reschedule SMS body. |
| `BOOKING_CONFIRMATION_USERS_TITLE` | `New appointment: {patient_name}` | Confirmation alert title. Placeholders: `{patient_name}`, `{slot_start}`. |
| `BOOKING_CONFIRMATION_USERS_BODY` | `{slot_start:%a, %d %b %Y %H:%M}` | Confirmation alert body. Same placeholders. |
| `BOOKING_CANCEL_USERS_TITLE` | `Appointment cancelled: {patient_name}` | Cancellation alert title. Same placeholders. |
| `BOOKING_CANCEL_USERS_BODY` | `{slot_start:%a, %d %b %Y %H:%M}` | Cancellation alert body. Same placeholders. |
| `BOOKING_RESCHEDULED_USERS_TITLE` | `Appointment rescheduled: {patient_name}` | Reschedule alert title. Same placeholders. |
| `BOOKING_RESCHEDULED_USERS_BODY` | `{slot_start:%a, %d %b %Y %H:%M}` | Reschedule alert body. Same placeholders. |
| `BOOKING_REMINDER_USERS_TITLE` | `Upcoming appointment: {patient_name}` | Reminder alert title. Same placeholders. |
| `BOOKING_REMINDER_USERS_BODY` | `{slot_start:%a, %d %b %Y %H:%M}` | Reminder alert body. Same placeholders. |

### Service requests (in-app)

| Key | Default | Description |
|---|---|---|
| `SERVICE_REQUEST_NOTIFICATIONS_ENABLED` | `True` | Master switch for all service request notifications. |
| `SERVICE_REQUEST_NOTIFY_RAISED` | `True` | Notify when an SR transitions to `active`. Sent to members of `sr.healthcare_service.managing_organization`. |
| `SERVICE_REQUEST_RAISED_TITLE` | `New {service_request_title} request` | Inbox title. |
| `SERVICE_REQUEST_RAISED_BODY` | `Patient: {patient_name}` | Inbox body. |

### Diagnostic reports (in-app)

| Key | Default | Description                                                                                                               |
|---|---|---------------------------------------------------------------------------------------------------------------------------|
| `DIAGNOSTIC_REPORT_NOTIFICATIONS_ENABLED` | `True` | Master switch for all diagnostic report notifications.                                                                    |
| `DIAGNOSTIC_REPORT_NOTIFY_READY` | `True` | Notify when a DR transitions to `final`. Sent to the encounter's care team **and** the originating SR's requester.        |
| `DIAGNOSTIC_REPORT_READY_TITLE` | `Diagnostic report ready for {patient_name}` | Inbox title.                                                                                                              |
| `DIAGNOSTIC_REPORT_READY_BODY` | `` | Inbox body (empty by default; title carries enough).                                                                      |

### Encounters (in-app)

| Key | Default | Description |
|---|---|---|
| `ENCOUNTER_NOTIFICATIONS_ENABLED` | `True` | Master switch for all encounter notifications. |
| `ENCOUNTER_NOTIFY_IP_CREATED` | `True` | Notify when an encounter newly becomes IP (`encounter_class="imp"`) with a `current_location` assigned. Sent to care team + members of every facility-org in the encounter's access cache. |
| `ENCOUNTER_IP_CREATED_TITLE` | `Bed {location_name} assigned to {patient_name}` | Inbox title. |
| `ENCOUNTER_IP_CREATED_BODY` | `{patient_name} is assigned to bed {location_name}` | Inbox body. |

### Medication stock (in-app)

| Key | Default | Description |
|---|---|---|
| `MEDICATION_NOTIFICATIONS_ENABLED` | `True` | Master switch for all medication stock notifications. |
| `MEDICATION_NOTIFY_NEAR_EXPIRY` | `True` | Notify when a medication InventoryItem's product expires within the lead window and has stock on hand. |
| `MEDICATION_NOTIFY_LOW_STOCK` | `True` | Notify when a medication InventoryItem's `net_content` drops below the threshold. |
| `MEDICATION_STOCK_SWEEP_MINUTES` | `1440` | How often the medication stock sweep runs. |
| `MEDICATION_NEAR_EXPIRY_LEAD_DAYS` | `30` | Days before expiry at which to fire near-expiry. |
| `MEDICATION_LOW_STOCK_THRESHOLD` | `10` | Threshold below which `net_content` triggers low-stock. |
| `MEDICATION_NEAR_EXPIRY_TITLE` | `Medication near expiry: {product_name}` | Inbox title. |
| `MEDICATION_NEAR_EXPIRY_BODY` | `Expires {expiration_date}. Location: {location_name}.` | Inbox body. |
| `MEDICATION_LOW_STOCK_TITLE` | `Low stock: {product_name}` | Inbox title. |
| `MEDICATION_LOW_STOCK_BODY` | `Remaining {net_content}. Location: {location_name}.` | Inbox body. |

### Web push (in-app companion)

Every clinician in-app notification is also pushed to the user's subscribed browsers/devices via the [Web Push protocol](https://developer.mozilla.org/en-US/docs/Web/API/Push_API) (`pywebpush` + VAPID), reusing the same title/body. Requires a frontend service worker to receive and display. Generate a keypair with the `py-vapid` CLI (ships with `pywebpush`): `vapid --gen`.

| Key | Default | Description |
|---|---|---|
| `WEBPUSH_NOTIFICATIONS_ENABLED` | `True` | Master switch. When `True`, the three VAPID settings below are **required at startup** — the app refuses to boot without them. |
| `WEBPUSH_VAPID_PUBLIC_KEY` | `""` | VAPID public key (base64url), served to the frontend so it can subscribe. |
| `WEBPUSH_VAPID_PRIVATE_KEY` | `""` | VAPID private key (base64url), used to sign sends. Set via env / `PLUGIN_CONFIGS`, never commit. |
| `WEBPUSH_VAPID_ADMIN_EMAIL` | `""` | Operator contact; becomes the `mailto:` `sub` claim in the VAPID JWT. |

Message bodies are Python `str.format` templates. Available placeholders per event:

| Event | Placeholders |
|---|---|
| Booking (all 4) | `{patient_name}`, `{slot_start}` (timezone-aware datetime; supports format specs like `{slot_start:%d %b %H:%M}`) |
| Service request raised | `{patient_name}`, `{service_request_title}` |
| Diagnostic report ready | `{patient_name}` |
| Encounter IP created | `{patient_name}`, `{location_name}` |
| Medication near expiry | `{product_name}`, `{expiration_date}`, `{location_name}`, `{net_content}` |
| Medication low stock | `{product_name}`, `{net_content}`, `{location_name}` |

## API

All endpoints are mounted under `/api/care_notifications/`.

**Visibility:** super admins and users with an admin role (Administrator / Admin / Facility Admin) see every user's records; everyone else sees only their own (`in_app_notifications`, `web_push_subscriptions`). `outbound_notifications` (SMS audit) is **admin-only**.

### `GET /in_app_notifications/`

Inbox feed. Ordered via `?ordering=` on `created_date` or `modified_date` (prefix with `-` for desc).

| Filter | Type | Possible values |
|---|---|---|
| `event_type` | string (iexact) | `booking_confirmation`, `booking_reminder`, `booking_cancellation`, `booking_reschedule`, `service_request_raised`, `diagnostic_report_ready`, `encounter_ip_created`, `medication_stock_near_expiry`, `medication_stock_low` |
| `resource_type` | string (iexact) | `booking`, `service_request`, `diagnostic_report`, `encounter`, `medication_stock` |
| `resource_id` | UUID | external_id of the underlying resource |
| `recipient` | UUID | external_id of the recipient user |
| `unread` | bool | `true` → only unread (`read_at IS NULL`); `false` → only read |
| `facility` | UUID | external_id of the facility — for a facility-scoped inbox (e.g. `/facility/:id/notifications`) |

### `GET /in_app_notifications/{id}/`

Retrieve a single notification (caller's own).

### `POST /in_app_notifications/mark_read/`

Marks the given notifications as read. Body: `{"ids": ["<external_id>", ...]}`. Returns `{"updated": <count>}`.

### `POST /in_app_notifications/mark_unread/`

Inverse of `mark_read` — clears `read_at` back to `null`. Same body shape.

### `GET /outbound_notifications/`

SMS audit log. Same filter params as in-app (`event_type`, `resource_type`, `resource_id`); ordering on `created_date` or `sent_at`. Possible `event_type` values currently emitted via SMS: `booking_confirmation`, `booking_reminder`, `booking_cancellation`, `booking_reschedule`. `resource_type`: `booking`.

### `GET /outbound_notifications/{id}/`

Retrieve a single outbound (SMS) record.

### `GET /web_push_subscriptions/`

List the caller's registered Web Push device subscriptions (`id`, `endpoint`, `created_date`).

### `POST /web_push_subscriptions/`

Register (upsert by `endpoint`) the current browser's subscription. Body is the browser's `PushSubscription.toJSON()` shape:

```json
{ "endpoint": "https://...", "keys": { "p256dh": "<base64url>", "auth": "<base64url>" } }
```

Returns `{id, endpoint, created_date}`. Re-registering the same `endpoint` updates the existing row (one row per device).

### `POST /web_push_subscriptions/unsubscribe/`

Opt a device out. Body: `{"endpoint": "<endpoint>"}`. Deletes the caller's matching subscription. Returns `{"deleted": <count>}`.

### `GET /web_push_subscriptions/vapid_public_key/`

Returns `{"public_key": "<WEBPUSH_VAPID_PUBLIC_KEY>"}` for the frontend service worker to call `pushManager.subscribe()`.

## Click-through routing (frontend)

Every in-app and web-push notification carries the identifiers needed to deep-link to the underlying resource. The **backend stores the semantic target; the frontend owns the route mapping** — implement one shared `resource_type → path` function and use it from **both** the inbox click handler **and** the service worker's `notificationclick`.

### Fields delivered
Both the in-app row (inbox API) and the web-push `event.data` carry the same target:

| Field | Location | Notes |
|---|---|---|
| `resource_type` | top-level | one of `encounter`, `service_request`, `diagnostic_report`, `medication_stock`, `booking` |
| `resource_id` | top-level | the resource's external_id |
| `facility_id` | top-level | facility external_id — populated for every current event (each resolves from a non-null FK); the resolver keeps a defensive null-check regardless |
| `payload.patient_id` | `payload` | present for `encounter`, `diagnostic_report`, `booking` |
| `payload.location_id` | `payload` | present for `medication_stock` (this is the route target — see note) |

(The patient booking-confirmation **SMS** has no click target; the user booking-confirmation **in-app / web-push** alert does — see `booking` below.)

### `resource_type` → route

| `resource_type` | route |
|---|---|
| `encounter` | `/facility/{facility_id}/patient/{patient_id}/encounter/{resource_id}` |
| `service_request` | `/facility/{facility_id}/service_requests/{resource_id}` |
| `diagnostic_report` | `/facility/{facility_id}/patient/{patient_id}/diagnostic_reports/{resource_id}` |
| `medication_stock` | `/facility/{facility_id}/locations/{location_id}` |
| `booking` | `/facility/{facility_id}/patient/{patient_id}/appointments/{resource_id}` |

### Reference resolver

```ts
// Shared by the inbox click handler AND the service worker's notificationclick.
type Notification = {
  resource_type: string;
  resource_id: string;
  facility_id: string;
  payload?: Record<string, string>;
};

function notificationPath(n: Notification): string | null {
  const { resource_type, resource_id, facility_id, payload = {} } = n;
  switch (resource_type) {
    case "encounter":
      return `/facility/${facility_id}/patient/${payload.patient_id}/encounter/${resource_id}`;
    case "service_request":
      return `/facility/${facility_id}/service_requests/${resource_id}`;
    case "diagnostic_report":
      return `/facility/${facility_id}/patient/${payload.patient_id}/diagnostic_reports/${resource_id}`;
    case "medication_stock":
      return `/facility/${facility_id}/locations/${payload.location_id}`; 
    default:
      return null; 
  }
}
```
