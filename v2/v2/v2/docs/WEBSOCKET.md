# WebSocket Protocol

## Connection

```
ws://host/api/v1/ws?token=<JWT_ACCESS_TOKEN>
```

## Events

### Client -> Server

| Event | Data | Description |
|-------|------|-------------|
| subscribe.room | { room_id } | Subscribe to room updates |
| unsubscribe.room | { room_id } | Unsubscribe from room |
| ping | {} | Heartbeat ping |

### Server -> Client

| Event | Data | Description |
|-------|------|-------------|
| connection.state | { status, conn_id } | Connection state change |
| room.created | { room } | New room created |
| room.updated | { room } | Room updated |
| player.joined | { user_id, conn_id } | Player joined room |
| player.left | { user_id } | Player left room |
| card.purchased | { card_id, user_id } | Card purchased |
| countdown.started | { ends_at } | Countdown started |
| countdown.tick | { seconds_left } | Countdown tick |
| countdown.ended | {} | Countdown ended |
| ball.called | { number } | Ball called |
| mark.auto | { card_id, number } | Auto mark |
| mark.manual | { card_id, number } | Manual mark |
| winner.claimed | { user_id, card_id } | Winner claimed |
| winner.validated | { is_winner, prize_amount } | Winner validated |
| prize.distributed | { user_id, amount } | Prize distributed |
| game.completed | { game_id, winner_id } | Game completed |
| game.paused | { game_id } | Game paused |
| game.resumed | { game_id } | Game resumed |
| game.cancelled | { game_id } | Game cancelled |
| leaderboard.updated | { leaderboard } | Leaderboard updated |
| wallet.updated | { balance } | Wallet updated |
| announcement | { title, body } | Announcement |
| notification | { title, body, type } | Notification |
| user.presence | { user_id, status } | User presence |
| error | { error } | Error |

## Reconnection

Clients should reconnect with exponential backoff:
- Initial delay: 1s
- Max delay: 30s
- Max attempts: 10

## Rate Limiting

Max 120 messages per 60 seconds per connection.
