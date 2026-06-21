---
name: "AWS FinOps Waste & Cost Optimization Report"
author: "wingchurn-tenable"
github_url: "https://github.com/wingchurn-tenable/cs-finopsv2"
description: "Single-file HTML report that turns Tenable Cloud Security findings into AWS cost-waste cleanup actions."
license: "MIT"
type: "tool"
tier: "unreviewed"
tags: [finops, aws, cost-optimization, cloud-security, tenable, cspm]
framework: "None (vanilla HTML/CSS/Canvas + Python)"
integrations: ["Tenable Cloud Security"]
date_added: 2026-06-21
---

A portable, single-file FinOps report that applies the AWS Well-Architected Cost Optimization Pillar to your cloud footprint and pulls **live posture data from Tenable Cloud Security** via its GraphQL API. Open one HTML file, paste a bearer token, and get an interactive view of waste candidates, prioritized cleanup actions, and an editable cost model — with zero external dependencies.

## What it does

- Renders six linked sections — Executive Summary, Live Environment Data, Waste Identification, Priority Matrix, Cost Implications, and a Detect → Notify → Terminate remediation plan.
- Pulls live findings from `https://app.tenable.com/api/graph` and visualizes them as a severity donut and a top-policy-violations bar chart (drawn on `<canvas>`, no chart libraries).
- Provides a clickable Resource Inventory: every finding drills into a detail view with resource name, type, region, account, ARN, tags, policy, and remediation steps, plus "Open in Tenable" and "Copy ARN" actions.
- Maps security findings to FinOps waste categories (unattached EBS, idle NAT/EC2/RDS, orphaned snapshots/ENIs, etc.) with explicit flagging criteria and a High/Medium/Low priority matrix.
- Includes an editable 2026 AWS cost model that recomputes estimated monthly and annual savings live.

## How it works

The report is one self-contained HTML file (HTML/CSS/JavaScript/Canvas) with no frameworks or CDN dependencies. It sends GraphQL queries to the Tenable Cloud Security API using an `Authorization: Bearer` token entered at runtime and held only in the browser tab. Because browsers block cross-origin calls to the Tenable API directly, the repo ships a dependency-free Python CORS proxy (`proxy_server.py`, standard library only) and an optional Cloudflare Worker; the report's Proxy URL field points at whichever you run. A built-in demo dataset lets the report render fully before any token is supplied.

## Disclaimer

Tenable Cloud Security is a security-posture platform, not a billing source. Cost figures are planning estimates derived from 2026 AWS list prices and the report's editable assumptions — cross-reference with AWS Cost Explorer before acting on any deletion.
