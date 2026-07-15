# Socket Events

## Subscription

Clients subscribe to rooms via WebSocket:

```json
{
  "event": "subscribe.room",
  "data": { "room_id": "uuid" }
}
```

## Unsubscription

```json
{
  "event": "unsubscribe.room",
  "data": { "room_id": "uuid" }
}
```

## Heartbeat

Server sends ping every 30s. Client must respond within 90s.

## Presence

Server broadcasts user presence:

```json
{
  "event": "user.presence",
  "data": { "user_id": "uuid", "status": "online|offline" }
}
```

## Connection State

```json
{
  "event": "connection.state",
  "data": { "status": "connected|disconnected", "conn_id": "uuid" }
}
```
