# Public Report Request Form — Setup Guide

This guide walks through the three one-time setup steps needed to make the public
report request form live. Once done, anyone can visit your GitHub Pages URL, enter
their email, and receive the weekly exhibit within ~2 minutes.

---

## Step 1 — Create a GitHub Personal Access Token (PAT)

The Cloudflare Worker needs a PAT to trigger GitHub Actions on your behalf.

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens**
2. Click **Generate new token**
3. Set:
   - **Token name**: `ny-gaming-worker`
   - **Expiration**: 1 year (or no expiration)
   - **Repository access**: Only select `nosherzapoo/OSBdata`
   - **Repository permissions**: set `Actions` → **Read and Write**
4. Click **Generate token** and copy it — you won't see it again

---

## Step 2 — Deploy the Cloudflare Worker

1. Go to **https://workers.cloudflare.com** and sign up for a free account
   (free tier allows 100,000 requests/day — more than enough)
2. Click **Create a Worker**
3. Delete the default code and paste the entire contents of `cloudflare_worker.js`
4. Click **Save and Deploy**
5. Go to **Settings → Variables → Secrets**
6. Add a new secret:
   - **Variable name**: `GITHUB_TOKEN`
   - **Value**: paste the PAT from Step 1
7. Click **Deploy** again to apply the secret
8. Copy your Worker URL — it will look like:
   `https://ny-gaming-worker.YOUR-SUBDOMAIN.workers.dev`

**Optional — restrict to specific email domains:**
In `cloudflare_worker.js`, edit the `ALLOWED_DOMAINS` array before deploying:
```js
const ALLOWED_DOMAINS = ['bernsteinsg.com'];  // only allow Bernstein emails
```

---

## Step 3 — Wire up the form and enable GitHub Pages

### 3a. Add your Worker URL to the form

Open `index.html` and replace the placeholder on this line:
```js
const WORKER_URL = 'REPLACE_WITH_YOUR_CLOUDFLARE_WORKER_URL';
```
with your actual Worker URL from Step 2, e.g.:
```js
const WORKER_URL = 'https://ny-gaming-worker.YOUR-SUBDOMAIN.workers.dev';
```
Commit and push this change.

### 3b. Enable GitHub Pages

1. Go to your repo on GitHub → **Settings → Pages**
2. Under **Source**, select **Deploy from a branch**
3. Choose **main** branch and **/ (root)** folder
4. Click **Save**

GitHub Pages will build and your form will be live at:
```
https://nosherzapoo.github.io/OSBdata/
```
(takes ~1 minute to go live the first time)

---

## How it works end-to-end

```
User visits https://nosherzapoo.github.io/OSBdata/
  → enters email → clicks Submit
  → index.html POSTs { email } to Cloudflare Worker
  → Worker validates email + calls GitHub API with PAT (securely)
  → GitHub Actions runner starts (ny-gaming-manual.yml)
  → Pipeline: download → extract → exhibit → compare + email
  → User receives email with Excel attachment (~2 min total)
```

## Notes

- The auto-scheduler (`ny-gaming-monitor.yml`) is completely unaffected
- When triggered via the public form, the report goes only to the requester's email
- When triggered manually from the GitHub Actions UI (no email input), it falls back
  to the default `NOTIFICATION_EMAIL1` / `NOTIFICATION_EMAIL2` secrets
- The GitHub PAT is only stored in Cloudflare's secret vault — never in the repo or browser
