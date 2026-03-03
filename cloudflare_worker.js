/**
 * NY Gaming Data — Cloudflare Worker
 *
 * This worker acts as a secure proxy between the public form (index.html)
 * and the GitHub Actions API. It holds the GitHub PAT as a secret so it
 * is never exposed to the browser.
 *
 * DEPLOY STEPS:
 *   1. Go to https://workers.cloudflare.com and create a free account
 *   2. Create a new Worker and paste this entire file as the worker code
 *   3. Go to Settings > Variables > Add the following secret:
 *        GITHUB_TOKEN  →  your GitHub Personal Access Token
 *        (PAT needs: Actions: Read & Write  scope — see setup_public_form.md)
 *   4. Save and deploy. Copy the worker URL (e.g. https://ny-gaming.yourname.workers.dev)
 *   5. Paste that URL into index.html where it says REPLACE_WITH_YOUR_CLOUDFLARE_WORKER_URL
 */

const GITHUB_OWNER   = 'nosherzapoo';
const GITHUB_REPO    = 'OSBdata';
const WORKFLOW_FILE  = 'ny-gaming-manual.yml';
const GITHUB_REF     = 'main';

/**
 * Optional: restrict which email domains are allowed to request a report.
 * Set to an empty array [] to allow any email address.
 * Example: ['bernsteinsg.com', 'gmail.com']
 */
const ALLOWED_DOMAINS = [];

const CORS_HEADERS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS_HEADERS, 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    // Handle CORS preflight
    if (request.method === 'OPTIONS') {
      return new Response(null, { headers: CORS_HEADERS });
    }

    if (request.method !== 'POST') {
      return json({ error: 'Method not allowed' }, 405);
    }

    // Parse body
    let email;
    try {
      const body = await request.json();
      email = (body.email || '').trim().toLowerCase();
    } catch {
      return json({ error: 'Invalid request body' }, 400);
    }

    // Validate email format
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'Invalid email address' }, 400);
    }

    // Optional domain restriction
    if (ALLOWED_DOMAINS.length > 0) {
      const domain = email.split('@')[1];
      if (!ALLOWED_DOMAINS.includes(domain)) {
        return json({ error: 'Email domain not permitted' }, 403);
      }
    }

    // Trigger GitHub Actions workflow_dispatch
    const githubRes = await fetch(
      `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
          'Accept':        'application/vnd.github.v3+json',
          'Content-Type':  'application/json',
          'User-Agent':    'ny-gaming-worker',
        },
        body: JSON.stringify({
          ref:    GITHUB_REF,
          inputs: { recipient_email: email },
        }),
      }
    );

    // GitHub returns 204 No Content on success
    if (githubRes.status === 204) {
      return json({ success: true });
    }

    const errorText = await githubRes.text();
    console.error('GitHub API error:', githubRes.status, errorText);
    return json({ error: 'Failed to trigger report. Please try again later.' }, 500);
  },
};
