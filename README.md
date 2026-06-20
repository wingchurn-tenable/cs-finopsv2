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

## Quick start

1. Open `aws-finops-waste-report.html` in any modern browser. It loads in **demo mode** immediately.
2. Click **Switch Tenant**, paste your Tenable **API bearer token**, and **Connect & Load** for live data.

The token is sent as `Authorization: Bearer <token>`. You may paste it with or without the leading `Bearer ` prefix. It lives only in the browser tab and is never stored or transmitted anywhere except to Tenable (directly or via your proxy).

## Live data & CORS

Browsers block direct `file://` → `app.tenable.com` calls (CORS). To use live data, run the included **Python proxy** and paste its URL into the report's **Proxy URL** field.

### Python proxy (standard library only — no pip, no npm)

```bash
python3 proxy_server.py            # listens on http://localhost:8787/
python3 proxy_server.py 9000       # optional custom port
```

Then set the report's **Proxy URL** to `http://localhost:8787/`. Serve the HTML over http so the browser allows the localhost call:

```bash
python3 -m http.server 8000        # then open http://localhost:8000/aws-finops-waste-report.html
```

The proxy forwards your `Authorization: Bearer` header to Tenable and adds the CORS headers the browser requires. Nothing is stored. For production, change `ALLOW_ORIGIN` in `proxy_server.py` from `*` to your page's origin.

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
