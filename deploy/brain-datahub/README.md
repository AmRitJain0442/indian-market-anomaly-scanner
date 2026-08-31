# brain-datahub deployment

The static research site is hosted by Nginx on the `brain-datahub` Compute Engine VM in the `tribe-v2-host` project.

The document root is `/srv/market-anomalies/current`. Each deployment is extracted into a commit-specific directory under `/srv/market-anomalies/releases`, then the `current` symbolic link is changed after validation.

The deployed URL structure mirrors the local `results` directory:

- `/stock_gallery/` contains the 252-session study
- `/ten_year/stock_gallery/` contains the 10-year study
- `/` redirects to the 252-session study

The checked-in Nginx configuration is installed at `/etc/nginx/sites-available/market-anomalies` and linked from `/etc/nginx/sites-enabled/market-anomalies`.

`install-release.sh` downloads both GitHub release archives, verifies their SHA-256 checksums, validates the expected entry points, installs the Nginx configuration, and changes the active release link.

The current deployment is available at `http://34.180.21.105/`.

Public HTTP access is limited to TCP port 80 by the `market-anomalies-http` firewall rule. The rule targets only instances with the `market-anomalies-web` network tag. Add a domain name before enabling a managed TLS certificate.

## Temporary Cloudflare HTTPS

`cloudflared-quick.service` exposes Nginx through a Cloudflare Quick Tunnel. This provides an automatically encrypted `trycloudflare.com` address without storing Cloudflare credentials on the VM.

Quick Tunnel hostnames can change whenever the service restarts and Cloudflare does not provide a production uptime commitment for them. Replace this service with a named tunnel after selecting a hostname in a Cloudflare-managed DNS zone.
