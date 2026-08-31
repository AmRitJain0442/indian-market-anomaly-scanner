#!/usr/bin/env bash
set -euo pipefail

release_id="${1:?usage: install-release.sh RELEASE_ID}"
release_root="/srv/market-anomalies/releases/${release_id}"
current_link="/srv/market-anomalies/current"

atlas_url="https://github.com/AmRitJain0442/indian-market-anomaly-scanner/releases/download/forecast-2026-08-27/NSE-anomaly-atlas-forecasts-2026-08-27.zip"
atlas_sha="c722a84529715b71dae8dba66ee86c96083321d3fe454597fd117eefa05cf70a"
decade_url="https://github.com/AmRitJain0442/indian-market-anomaly-scanner/releases/download/forecast-2026-08-27/NSE-anomaly-decade-forecasts-2016-2026.zip"
decade_sha="30f27d4775cdef2e44cb51389a513a79eed7e64ce12889908558a141403f14ee"

if [[ -e "${current_link}" && ! -L "${current_link}" ]]; then
    echo "Refusing to replace non-link path at ${current_link}" >&2
    exit 1
fi

sudo install -d -o "$(id -u)" -g "$(id -g)" "${release_root}"
cd "${release_root}"

echo "Downloading the 252-session archive"
curl -fsSL --retry 3 -o atlas.zip "${atlas_url}"
echo "${atlas_sha}  atlas.zip" | sha256sum -c -

echo "Downloading the 10-year archive"
curl -fsSL --retry 3 -o decade.zip "${decade_url}"
echo "${decade_sha}  decade.zip" | sha256sum -c -

echo "Extracting verified archives"
unzip -q -o atlas.zip
unzip -q -o decade.zip

test -f results/stock_gallery/index.html
test -f results/stock_gallery/guide.html
test -f results/ten_year/stock_gallery/index.html
test -f results/ten_year/stock_gallery/guide.html
test -f results/forecasts/forecast_metadata.json
test -f results/ten_year/forecasts/forecast_metadata.json

sudo install -m 0644 /tmp/market-anomalies.conf /etc/nginx/sites-available/market-anomalies
sudo ln -sfn /etc/nginx/sites-available/market-anomalies /etc/nginx/sites-enabled/market-anomalies
if [[ -L /etc/nginx/sites-enabled/default ]]; then
    sudo unlink /etc/nginx/sites-enabled/default
fi

sudo ln -sfn "${release_root}/results" "${current_link}"
sudo nginx -t
sudo systemctl reload nginx

echo "Deployment active at ${current_link}"
du -sh "${release_root}/results"
