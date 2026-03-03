/**
 * NY Gaming Data — Cloudflare Worker
 *
 * Paste this code into the Cloudflare Worker editor and deploy.
 * Then go to Settings → Variables → add a secret:
 *   Name:  GITHUB_TOKEN
 *   Value: your GitHub fine-grained PAT (Actions: Read & Write on OSBdata)
 *
 * NOTE: This uses the classic Service Worker format which works with the
 * default Cloudflare dashboard editor. GITHUB_TOKEN is exposed as a global
 * variable when set under Settings → Variables.
 */

addEventListener('fetch', event => {
  event.respondWith(handleRequest(event.request));
});

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function jsonResponse(body, status) {
  return new Response(JSON.stringify(body), {
    status: status || 200,
    headers: Object.assign({}, CORS, { 'Content-Type': 'application/json' }),
  });
}

async function handleRequest(request) {
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: CORS });
  }

  if (request.method !== 'POST') {
    return jsonResponse({ error: 'Method not allowed' }, 405);
  }

  var email;
  try {
    var body = await request.json();
    email = (body.email || '').trim().toLowerCase();
  } catch (e) {
    return jsonResponse({ error: 'Invalid request body' }, 400);
  }

  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return jsonResponse({ error: 'Invalid email address' }, 400);
  }

  // GITHUB_TOKEN is available as a global variable from Settings → Variables
  var ghRes = await fetch(
    'https://api.github.com/repos/nosherzapoo/OSBdata/actions/workflows/ny-gaming-manual.yml/dispatches',
    {
      method: 'POST',
      headers: {
        'Authorization': 'Bearer ' + GITHUB_TOKEN,
        'Accept':        'application/vnd.github.v3+json',
        'Content-Type':  'application/json',
        'User-Agent':    'ny-gaming-worker',
      },
      body: JSON.stringify({ ref: 'main', inputs: { recipient_email: email } }),
    }
  );

  if (ghRes.status === 204) {
    return jsonResponse({ success: true }, 200);
  }

  return jsonResponse({ error: 'Failed to trigger report. Please try again.' }, 500);
}
