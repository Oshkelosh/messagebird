# MessageBird (`messagebird`)

Send SMS notifications via the MessageBird Messages API.

## Overview

| | |
|---|---|
| Addon ID | `messagebird` |
| Category | notification |
| Channels | sms |
| Version | 1.0.0 |
| Category guide | [../README.md](../README.md) |

Only **one** notification provider per channel can be active at a time.

## Enable and configure

1. Install this package under `app/addons/notifications/messagebird/`
2. Open **Admin → Notifications → MessageBird** at `/admin/notifications/messagebird`
3. Enter access key and originator
4. Enable the provider checkbox and save

## Configuration schema

| Field | Type | Description |
|-------|------|-------------|
| `access_key` | secret | MessageBird live API access key |
| `originator` | string | Sender name (11 chars max) or E.164 phone number |

Secrets are stored in `addon_configs`, not in `.env`.

## Routes

### Admin

| Method | Path | Description |
|--------|------|-------------|
| GET | `/admin/notifications/messagebird` | Config form |
| POST | `/admin/notifications/messagebird/save` | Save config |

### Public API

None — core calls `send_sms()` when applicable.

## Provider setup

1. Create a [MessageBird](https://www.messagebird.com/) account.
2. Generate a **Live API key** under **Developers → API access**.
3. Register an **originator** (virtual number or approved sender name) for your target countries.
4. Paste the access key and originator into admin config.
5. Enable the addon.

Uses `POST https://rest.messagebird.com/messages` with `Authorization: AccessKey {key}`.

Email and push are not supported.

## Package layout

```
messagebird/
├── README.md
├── addon.py
├── routes.py
└── templates/
    └── messagebird_config.html
```

## See also

- [Notification addon development](../README.md)
- [Oshkelosh addon guide](../../README.md)
