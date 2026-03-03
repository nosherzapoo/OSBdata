/**
 * NY Gaming Data — Cloudflare Worker
 *
 * Secure proxy between the public form and the GitHub Actions API.
 * The GitHub PAT is stored as a Cloudflare secret — never in the browser.
 *
 * DEPLOY STEPS:
 *   1. Go to https://workers.cloudflare.com → sign up free → Create a Worker
 *   2. Delete the default code and paste this entire file
 *   3. Click Save and Deploy
 *   4. Go to Settings → Variables → Add secret:
 *        Name:  GITHUB_TOKEN
 *        Value: your GitHub fine-grained PAT (Actions: Read & Write on OSBdata only)
 *   5. Click Deploy again to apply the secret
 *   6. Copy your Worker URL (e.g. https://ny-gaming.YOUR-NAME.workers.dev)
 *   7. Paste that URL into index.html where it says REPLACE_WITH_YOUR_CLOUDFLARE_WORKER_URL
 */

const GITHUB_OWNER  = 'nosherzapoo';
const GITHUB_REPO   = 'OSBdata';
const WORKFLOW_FILE = 'ny-gaming-manual.yml';
const GITHUB_REF    = 'main';

// Optional: restrict to specific email domains e.g. ['bernsteinsg.com']
// Leave as [] to allow any email address.
const ALLOWED_DOMAINS = [];

const CORS = {
  'Access-Control-Allow-Origin':  '*',
  'Access-Control-Allow-Methods': 'POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { ...CORS, 'Content-Type': 'application/json' },
  });
}

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
    if (request.method !== 'POST') return json({ error: 'Method not allowed' }, 405);

    let email;
    try {
      const body = await request.json();
      email = (body.email || '').trim().toLowerCase();
    } catch {
      return json({ error: 'Invalid request body' }, 400);
    }

    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      return json({ error: 'Invalid email address' }, 400);
    }

    if (ALLOWED_DOMAINS.length > 0) {
      const domain = email.split('@')[1];
      if (!ALLOWED_DOMAINS.includes(domain)) {
        return json({ error: 'Email domain not permitted' }, 403);
      }
    }

    const ghRes = await fetch(
      `https://api.github.com/repos/${GITHUB_OWNER}/${GITHUB_REPO}/actions/workflows/${WORKFLOW_FILE}/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${env.GITHUB_TOKEN}`,
          'Accept':        'application/vnd.github.v3+json',
          'Content-Type':  'application/json',
          'User-Agent':    'ny-gaming-worker',
        },
        body: JSON.stringify({ ref: GITHUB_REF, inputs: { recipient_email: email } }),
      }
    );

    if (ghRes.status === 204) return json({ success: true });

    const err = await ghRes.text();
    console.error('GitHub API error:', ghRes.status, err);
    return json({ error: 'Failed to trigger report. Please try again.' }, 500);
  },
};
