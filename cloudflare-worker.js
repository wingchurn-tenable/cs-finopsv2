/**
 * Tenable GraphQL CORS proxy — Cloudflare Worker
 * --------------------------------------------------
 * Deploy (free tier is fine):
 *   1. https://dash.cloudflare.com  ->  Workers & Pages  ->  Create Worker
 *   2. Paste this file, click Deploy.
 *   3. Copy the *.workers.dev URL into the report's "Proxy URL" field.
 *
 * Or via Wrangler CLI:
 *   npm i -g wrangler
 *   wrangler deploy cloudflare-worker.js --name tenable-graph-proxy
 *
 * The browser sends the X-ApiKeys / Authorization header to this worker;
 * the worker forwards it verbatim to Tenable and adds the CORS headers the
 * browser requires. No credentials are stored or logged.
 */

const TENABLE_ENDPOINT = "https://app.tenable.com/api/graph";

// Lock this down to your own page origin in production instead of "*".
const ALLOW_ORIGIN = "*";

function corsHeaders() {
  return {
    "Access-Control-Allow-Origin": ALLOW_ORIGIN,
    "Access-Control-Allow-Methods": "POST, OPTIONS",
    "Access-Control-Allow-Headers": "Content-Type, X-ApiKeys, Authorization",
    "Access-Control-Max-Age": "86400",
  };
}

export default {
  async fetch(request) {
    // Preflight
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: corsHeaders() });
    }
    if (request.method !== "POST") {
      return new Response("Only POST is supported.", {
        status: 405,
        headers: corsHeaders(),
      });
    }

    // Forward the auth headers the browser supplied.
    const fwd = new Headers({ "Content-Type": "application/json" });
    const apiKeys = request.headers.get("X-ApiKeys");
    const auth = request.headers.get("Authorization");
    if (apiKeys) fwd.set("X-ApiKeys", apiKeys);
    if (auth) fwd.set("Authorization", auth);

    const body = await request.text();

    const upstream = await fetch(TENABLE_ENDPOINT, {
      method: "POST",
      headers: fwd,
      body,
    });

    const out = new Headers(corsHeaders());
    out.set("Content-Type", upstream.headers.get("Content-Type") || "application/json");

    return new Response(upstream.body, { status: upstream.status, headers: out });
  },
};
