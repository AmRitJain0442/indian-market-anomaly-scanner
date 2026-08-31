# brain-datahub deployment

The static research site is hosted by Nginx on the `brain-datahub` Compute Engine VM in the `tribe-v2-host` project.

The document root is `/srv/market-anomalies/current`. Each deployment is extracted into a commit-specific directory under `/srv/market-anomalies/releases`, then the `current` symbolic link is changed after validation.

The deployed URL structure mirrors the local `results` directory:

- `/stock_gallery/` contains the 252-session study
- `/ten_year/stock_gallery/` contains the 10-year study
- `/` redirects to the 252-session study

The checked-in Nginx configuration is installed at `/etc/nginx/sites-available/market-anomalies` and linked from `/etc/nginx/sites-enabled/market-anomalies`.

The current deployment is available over HTTP at the VM public IP. Add a domain name before enabling a managed TLS certificate.
