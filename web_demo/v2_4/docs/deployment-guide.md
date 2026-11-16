# Independent Execution & Deployment Guide

## 1. Installing Dependencies
**None required.** Eco-Route Live V2.4 has no `package.json`, `node_modules`, or build pipeline. Internet access is required on first load to fetch Tailwind CSS (`https://cdn.tailwindcss.com`) and Google Fonts (`Inter` and `JetBrains Mono`).

## 2. Running Locally
- **Direct Browser Open:** Double-click `index.html` to open it in Chrome, Edge, Firefox, or Safari.
- **Local Static HTTP Server:**
  ```bash
  python3 -m http.server 8080
  ```
  Then navigate to `http://localhost:8080`.

## 3. Building for Production
No compilation or bundling step is required; `index.html` is already production-ready static markup.

## 4. Hosting as a Static Website
Upload `index.html`, `README.md`, and `docs/` to any static web host (GitHub Pages, Cloudflare Pages, Netlify, Vercel, or AWS S3). No server-side routing or environment variables are needed.

## 5. Deploying with GitHub Pages
1. Push `index.html` to the root of your GitHub repository on the `main` branch.
2. Open your repository on GitHub and navigate to **Settings → Pages**.
3. Under **Build and deployment → Source**, select **Deploy from a branch**.
4. Select branch **`main`** and folder **`/ (root)`**, then click **Save**.
5. Once built (~60 seconds), the live simulator will be accessible at `https://<username>.github.io/<repository-name>/`.

## 6. Environment Variables & Configuration
**None.** All simulation parameters (`INITIAL_RACKS`, `THROTTLE_TEMP = 80.0`, `CRITICAL_TEMP = 85.0`, and the `800 ms` tick interval) are configured directly inside the `<script>` block of `index.html`.
