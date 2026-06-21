# AWS FinOps — Waste & Cost Optimization Report

A single-file, portable HTML report that applies the **AWS Well-Architected Cost Optimization Pillar** to surface hidden cloud waste, and pulls **live posture data from Tenable Cloud Security** via its GraphQL API. Zero external dependencies — pure HTML/CSS/Canvas in one file.

![status](https://img.shields.io/badge/dependencies-zero-c5e700) ![type](https://img.shields.io/badge/single--file-HTML5-1d252d)

## Features

- **Six sections** with a sticky, clickable table of contents: Executive Summary, Live Environment Data, Waste Identification, Priority Matrix, Cost Implications, Remediation Plan.
- **Live data** from `https://app.tenable.com/api/graph` — findings severity (donut) and top policy violations (horizontal bar), both rendered on `<canvas>`.
- **Resource Inventory drill-down** — every finding is a clickable row; open a detail modal with resource name, type, region, account, ARN, tags, severity, policy, and remediation steps, plus **Open in Tenable** and **Copy ARN** actions.
- **Interactive filtering** — click a severity legend, a policy bar, or a waste-type row to filter the inventory; free-text search included.
- **Editable cost model** — tune quantities against 2026 AWS rates; monthly/annual savings recompute live.
- **Switch Tenant** and **Refresh Data** buttons, last-polled timestamp, and a graceful demo dataset so the report is never blank.
- **Theme** — Pantone 433C (`#1d252d`) background, white text, Pantone 395C (`#c5e700`) accents.

## Quick start (one command — recommended)

```bash
python3 proxy_server.py
```

This serves the report **and** proxies its GraphQL calls to Tenable from the same origin, then opens your browser straight to it. No CORS, no separate static server, nothing to paste. Just enter your Tenable **bearer token** and click **Connect**.

```bash
python3 proxy_server.py 9000        # custom port
python3 proxy_server.py --no-browser  # don't auto-open the browser
```

The token is sent as `Authorization: Bearer <token>` (with or without a leading `Bearer `), lives only in the browser tab, and is never stored or sent anywhere except to Tenable via the local proxy.

## How the launcher works

| Request | Handled as |
|---------|-----------|
| `GET /` | the report (`aws-finops-waste-report.html`) |
| `GET /<file>` | static files from this folder |
| `POST /api/graph` | forwarded to `https://app.tenable.com/api/graph` with your bearer header |

Because the page and the proxy share an origin, the browser makes no cross-origin request — so there is nothing for CORS to block. The launcher opens the report with `?proxy=/api/graph`, which auto-fills the report's **Proxy URL** field. For production, change `ALLOW_ORIGIN` in `proxy_server.py` from `*` to your page's origin.

## Open the file directly instead

You can also just open `aws-finops-waste-report.html` in a browser — it loads in **demo mode** immediately. For live data this way you must supply a proxy URL (browsers block direct `file://` → `app.tenable.com` calls), so the one-command launcher above is the simpler path.

### Optional: Cloudflare Worker (serverless)

`cloudflare-worker.js` is included as an optional zero-server alternative — paste it into a new Worker at [dash.cloudflare.com](https://dash.cloudflare.com) → Workers & Pages → Create Worker → Deploy (no CLI required), then use the `*.workers.dev` URL as the Proxy URL.

## Files

| File | Purpose |
|------|---------|
| `aws-finops-waste-report.html` | The complete single-file report (UI, charts, GraphQL client). |
| `proxy_server.py` | Local CORS proxy to the Tenable GraphQL API (Python stdlib, no installs). |
| `cloudflare-worker.js` | Optional serverless CORS proxy (deploy via the Cloudflare dashboard). |

## Requirements

- Python 3.7+ (standard library only) for the local proxy
- A Tenable Cloud Security API **bearer token**

## Disclaimer

Tenable Cloud Security is a security-posture platform, not a billing source. Cost figures in this report are **planning estimates** derived from 2026 AWS list prices and the editable assumptions in the report — not a bill. Cross-reference with AWS Cost Explorer / the AWS Pricing Calculator before acting on any deletion.
