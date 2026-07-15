# Admin Architecture

## Access Control

- Super admins defined by `ADMIN_IDS` env var
- Additional admins via User.role field
- All admin actions logged with audit trail

## Dashboard

- Revenue today/month
- Active games
- Pending withdrawals
- House balance
- Player analytics

## User Management

- Search users by username, name, telegram ID
- Adjust wallet balances
- Freeze/unfreeze wallets
- View user history

## Transaction Management

- Approve/reject deposits
- Approve/reject withdrawals
- View transaction history
- Export reports

## Room Controls

- Pause/resume rooms
- Emergency stop
- Cancel games
- View active rooms

## Announcements

- Create announcements
- Broadcast to all users
- Priority levels
- Schedule announcements

## Feature Flags

- Toggle features on/off
- Immediate effect
- Audit logged

## Maintenance Mode

- Enable/disable maintenance
- Custom message
- Blocks user access

## Reports

- Revenue reports
- User reports
- Game reports
- Export to CSV/JSON

## Audit Logs

- All admin actions logged
- IP and user agent tracked
- Immutable audit trail
