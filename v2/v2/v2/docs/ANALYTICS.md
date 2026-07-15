# Analytics Flow

## Real-time Metrics

- Players online (WebSocket connections)
- Concurrent rooms (active games)
- Games running
- Cards sold
- Revenue (deposits)
- Deposits/withdrawals

## Aggregated Metrics

- Average session length
- Player retention
- Daily active users (DAU)
- Monthly active users (MAU)
- House profit
- Prize distribution
- Average cards per player
- Average room fill
- Average game duration

## Data Sources

- PostgreSQL for transactional data
- Redis for real-time counters
- WebSocket manager for online users

## Refresh Intervals

- Real-time: 5s
- Hourly aggregation: 30m
- Daily aggregation: 24h

## Export

- CSV export for reports
- Date range filtering
- Admin-only access
