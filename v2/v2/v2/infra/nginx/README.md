# Nginx

Reverse proxy configuration.

## Purpose

Routes traffic to backend and frontend services.

## Configs

- `default.conf` - Main server block

## Routes

- `/api/` → backend:8000
- `/` → frontend:5173

## Future

- SSL/TLS termination
- Rate limiting
- Caching headers
- Gzip/Brotli compression
