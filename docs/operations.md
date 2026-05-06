# Operations Reference

How to run, monitor, and troubleshoot phonebooth on joi (the OptiPlex).

## Architecture (running)

Two systemd services, both auto-start on boot:

| Service | Purpose | Port |
|---------|---------|------|
| `cloudflared-phonebooth.service` | Cloudflare Tunnel from joi to phonebooth.vfxbuddy.com | (outbound QUIC) |
| `phonebooth.service` | Laravel app (`php artisan serve`) | 8000 |

Public URL: **https://phonebooth.vfxbuddy.com**
Local URL: **http://localhost:8000**

## Daily commands

### Status
```bash
sudo systemctl status phonebooth
sudo systemctl status cloudflared-phonebooth
```

### Restart (after code changes)
```bash
sudo systemctl restart phonebooth
```

Note: Laravel doesn't hot-reload PHP. Restart the service after editing controllers, models, views, etc. Vite-built assets (CSS, JS) reload without a service restart since they're static files served from `public/build/`.

### Live tail logs
```bash
# Laravel + systemd events
sudo journalctl -u phonebooth -f

# Cloudflare tunnel
sudo journalctl -u cloudflared-phonebooth -f

# Laravel app log (separate from systemd)
tail -f storage/logs/laravel.log

# Phonebooth-specific channels
tail -f storage/logs/phonebooth_calls-*.log
tail -f storage/logs/phonebooth_webhooks-*.log
```

### Stop / start
```bash
sudo systemctl stop phonebooth
sudo systemctl start phonebooth
```

### Disable auto-start (if you want to take it offline)
```bash
sudo systemctl disable phonebooth cloudflared-phonebooth
sudo systemctl stop phonebooth cloudflared-phonebooth
```

To re-enable: replace `disable` with `enable` and `stop` with `start`.

## Service file locations

These are NOT in the repo (system files):
- `/etc/systemd/system/cloudflared-phonebooth.service`
- `/etc/systemd/system/phonebooth.service`

If you need to recreate them on a fresh machine, see "Recreating the services" below.

## Common operations

### Update the app from a fresh git pull
```bash
cd /home/sean/phonebooth
git pull
composer install --no-dev --optimize-autoloader  # if composer.lock changed
npm install                                       # if package-lock.json changed
npm run build                                     # if any JS or CSS changed
php artisan migrate                               # if there are new migrations
sudo systemctl restart phonebooth
```

### Database backup (SQLite)
```bash
cp /home/sean/phonebooth/database/database.sqlite /mnt/deepstorage/phonebooth-backup-$(date +%Y%m%d).sqlite
```

Worth running once a week or before any risky migration.

### Tinker (interactive PHP REPL)
```bash
cd /home/sean/phonebooth
php artisan tinker
```

Useful for ad-hoc queries:
```php
App\Models\Lead::where('status', 'new')->count();
App\Models\Event::where('event_type', 'call_completed')->whereDate('created_at', today())->get();
```

### Check what's listening on port 8000
```bash
sudo lsof -i:8000
```

If a stale process is holding the port and the service can't start, kill it manually:
```bash
sudo kill <PID>
sudo systemctl restart phonebooth
```

## Troubleshooting

### "Phonebooth is down" — public URL returns 530
Cloudflare can reach Cloudflare's network, but the tunnel can't reach the local app. Check both services:
```bash
sudo systemctl status cloudflared-phonebooth
sudo systemctl status phonebooth
```

If `phonebooth.service` is dead, check journal:
```bash
sudo journalctl -u phonebooth -n 50 --no-pager
```

### "Phonebooth is down" — public URL won't resolve
Tunnel itself is down. Check cloudflared:
```bash
sudo systemctl status cloudflared-phonebooth
sudo journalctl -u cloudflared-phonebooth -n 50 --no-pager
```

If joi has no internet, neither service will recover until network is back.

### Laravel error after deploying changes
Pull logs from systemd OR Laravel:
```bash
sudo journalctl -u phonebooth -n 100 --no-pager
tail -100 storage/logs/laravel.log
```

Most likely causes after a deploy:
- Missed `composer install` (vendor/ out of date)
- Missed `php artisan migrate` (schema mismatch)
- Missed `npm run build` (manifest.json out of date — pages render but assets 404)
- File permission issue on `storage/` or `bootstrap/cache/`

### Twilio webhooks failing
1. Verify the tunnel is up (curl from outside or check Cloudflare dashboard)
2. Check phonebooth_webhooks log for what Twilio actually sent:
   ```bash
   tail -f storage/logs/phonebooth_webhooks-*.log
   ```
3. In Twilio Console, the call's debugger shows webhook attempts and error codes

### Cockpit page shows "Phone initialization failed"
Browser console (F12) will show the actual error. Common causes:
- `.env` Twilio vars empty or wrong (token endpoint returns 503)
- Mic permission denied (browser blocked or wrong device selected)
- Twilio account suspended / billing issue

## Recreating the services on a fresh machine

If you ever rebuild joi from scratch, the systemd unit files need to be recreated.

### `/etc/systemd/system/cloudflared-phonebooth.service`
```ini
[Unit]
Description=Cloudflare Tunnel for phonebooth.vfxbuddy.com
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=sean
ExecStart=/usr/local/bin/cloudflared tunnel --config /home/sean/.cloudflared/config.yml run phonebooth
Restart=on-failure
RestartSec=10
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

### `/etc/systemd/system/phonebooth.service`
```ini
[Unit]
Description=Phonebooth Laravel App
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=sean
WorkingDirectory=/home/sean/phonebooth
ExecStart=/usr/bin/php artisan serve --host=0.0.0.0 --port=8000
Restart=on-failure
RestartSec=10
StandardOutput=append:/home/sean/phonebooth/storage/logs/phonebooth-systemd.log
StandardError=append:/home/sean/phonebooth/storage/logs/phonebooth-systemd.log

[Install]
WantedBy=multi-user.target
```

### Install commands
```bash
sudo cp cloudflared-phonebooth.service /etc/systemd/system/
sudo cp phonebooth.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cloudflared-phonebooth.service phonebooth.service
sudo systemctl start cloudflared-phonebooth.service phonebooth.service
```

You also need:
- `cloudflared` installed and authenticated (`cloudflared tunnel login`)
- The tunnel created (`cloudflared tunnel create phonebooth`) — credentials at `~/.cloudflared/<tunnel-id>.json`
- DNS routed (`cloudflared tunnel route dns phonebooth phonebooth.vfxbuddy.com`)
- `~/.cloudflared/config.yml` pointing at the tunnel and credentials file
- Laravel installed at `/home/sean/phonebooth` with `.env` populated

## Notes for Phase 2 / Stage 3 migration

When phonebooth migrates to a VPS (per spec 12), `php artisan serve` should be replaced with **nginx + php-fpm**. The artisan dev server is fine for one user but not designed for production traffic.

The migration would also drop the cloudflared tunnel (the VPS has a public IP) — DNS would point directly at the VPS and Let's Encrypt would handle TLS.
