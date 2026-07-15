# Background Workers

## Workers

| Worker | Schedule | Description |
|--------|----------|-------------|
| NotificationWorker | Every 5s | Processes notification queue |
| ReminderWorker | Every 60s | Sends reminders (daily rewards, referrals) |
| GameSchedulerWorker | Every 30s | Schedules pending rooms |
| CleanupWorker | Every 1h | Cleans expired sessions and rooms |
| LeaderboardRefreshWorker | Every 1h | Refreshes leaderboards |
| StatisticsAggregationWorker | Every 30m | Aggregates statistics |
| AuditArchivingWorker | Daily | Archives old audit logs |
| RetryQueueWorker | Every 10s | Retries failed notifications |
| HealthMonitorWorker | Every 30s | Monitors system health |

## Configuration

Workers are started in `app.main.lifespan` and stopped on shutdown.

## Failure Handling

- Workers catch and log exceptions
- Retry queue retries failed notifications
- Health monitor alerts on anomalies
