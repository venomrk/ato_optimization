# 🚀 Deploy to Vercel in 5 Minutes

This guide will help you deploy the **RKO Research Platform** to Vercel with a **FREE domain** (e.g., `rko-research.vercel.app`).

## Prerequisites

- GitHub account
- Vercel account (sign up free at [vercel.com](https://vercel.com))
- Railway account for backend (sign up free at [railway.app](https://railway.app))

---

## Step 1: Deploy Backend to Railway (2 minutes)

### Why Railway?
- ✅ Free $5 credit/month
- ✅ PostgreSQL database included
- ✅ Perfect for FastAPI
- ✅ Auto-deploys from GitHub

### Instructions

1. **Sign up for Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Login with GitHub"
   - Authorize Railway

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your repositories
   - Select your repository

3. **Add PostgreSQL Database:**
   - In your Railway project dashboard
   - Click "New"
   - Select "Database" → "PostgreSQL"
   - Railway automatically creates and connects the database

4. **Configure Environment Variables:**
   
   Click on your backend service, then go to "Variables" tab:
   
   ```bash
   # Required
   SECRET_KEY=generate-a-random-32-character-string-here
   CORS_ORIGINS=https://your-project.vercel.app
   
   # Optional (add your API keys)
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   SERP_API_KEY=your-serp-api-key
   STRIPE_SECRET_KEY=sk_test_your-stripe-key
   STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret
   ```
   
   **Note:** `DATABASE_URL` is automatically set by Railway when you add PostgreSQL.
   
   To generate `SECRET_KEY`:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

5. **Deploy:**
   - Railway detects `railway.toml` and deploys automatically
   - Wait for deployment to complete (1-2 minutes)
   - Copy your backend URL (looks like: `https://your-project.up.railway.app`)
   - Test it: Visit `https://your-backend-url.railway.app/health`

---

## Step 2: Deploy Frontend to Vercel (3 minutes)

### Why Vercel?
- ✅ 100% FREE
- ✅ Fast global CDN
- ✅ Auto-deploys on Git push
- ✅ Free SSL certificate
- ✅ Free subdomain (.vercel.app)

### Instructions

1. **Sign up for Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign Up"
   - Choose "Continue with GitHub"
   - Authorize Vercel

2. **Import Project:**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Find your repository and click "Import"

3. **Configure Build Settings:**
   
   Vercel should auto-detect the settings, but verify:
   
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend`
   - **Build Command:** `npm run build`
   - **Output Directory:** `dist`
   - **Install Command:** `npm install`

4. **Add Environment Variables:**
   
   Before deploying, click "Environment Variables" and add:
   
   ```bash
   VITE_API_BASE_URL=https://your-backend.railway.app
   ```
   
   Replace `your-backend.railway.app` with your actual Railway backend URL from Step 1.
   
   Optional (if using Stripe):
   ```bash
   VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your-stripe-publishable-key
   ```

5. **Deploy:**
   - Click "Deploy"
   - Vercel builds and deploys your frontend (1-2 minutes)
   - You'll get a URL like: `https://your-project.vercel.app`

---

## Step 3: Update CORS Settings

Now that you have your Vercel domain, update Railway backend CORS:

1. Go back to Railway dashboard
2. Click on your backend service
3. Go to "Variables" tab
4. Update `CORS_ORIGINS`:
   ```bash
   CORS_ORIGINS=https://your-project.vercel.app,https://your-project-git-*.vercel.app
   ```
   
   The wildcard allows Vercel preview deployments to work too!

5. Railway will automatically redeploy with new settings

---

## Step 4: Test Your Deployment

Visit your Vercel URL: `https://your-project.vercel.app`

### Test Checklist:
- [ ] Frontend loads without errors
- [ ] Can navigate to different pages
- [ ] Can create a new account
- [ ] Can log in
- [ ] Dashboard displays
- [ ] Can search for papers (if API keys configured)
- [ ] Can chat with AI agents (if OpenRouter key configured)

### Troubleshooting:

**Frontend won't load:**
- Check Vercel deployment logs
- Ensure build completed successfully

**Can't create account:**
- Check Railway backend logs
- Ensure `DATABASE_URL` is set
- Verify backend is running: visit `/health` endpoint

**CORS errors in browser console:**
- Update `CORS_ORIGINS` in Railway
- Make sure it matches your Vercel domain exactly
- Redeploy Railway service

**API requests fail:**
- Check `VITE_API_BASE_URL` in Vercel env vars
- Ensure it points to your Railway backend URL
- Redeploy Vercel

---

## Automatic Deployments

Both Vercel and Railway are now set up for **automatic deployments**!

### How it works:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Add new feature"
   git push origin main
   ```

2. **Auto-deploy:**
   - Vercel deploys your frontend automatically
   - Railway deploys your backend automatically
   - No manual intervention needed!

3. **Preview Deployments (Vercel):**
   - Create a new branch
   - Open a Pull Request
   - Vercel creates a preview URL automatically
   - Test changes before merging

---

## Custom Domain (Optional)

### Use Vercel's Free Domain

Vercel gives you a free `.vercel.app` domain. To customize it:

1. Go to your Vercel project
2. Click "Settings" → "Domains"
3. Your default domain is: `your-project.vercel.app`
4. You can change the project name to get a different subdomain

### Use Your Own Domain

If you have a custom domain:

1. In Vercel project, go to "Settings" → "Domains"
2. Click "Add"
3. Enter your domain (e.g., `research.yourdomain.com`)
4. Follow Vercel's DNS instructions
5. HTTPS is automatically configured!

**Update Railway CORS:**
```bash
CORS_ORIGINS=https://your-custom-domain.com,https://your-project.vercel.app
```

---

## Environment Variables Reference

### Vercel (Frontend)

| Variable | Required | Example |
|----------|----------|---------|
| `VITE_API_BASE_URL` | ✅ Yes | `https://your-backend.railway.app` |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Optional | `pk_test_...` |

### Railway (Backend)

| Variable | Required | Example |
|----------|----------|---------|
| `DATABASE_URL` | ✅ Yes (auto-set) | `postgresql://...` |
| `SECRET_KEY` | ✅ Yes | `random-32-char-string` |
| `CORS_ORIGINS` | ✅ Yes | `https://your-project.vercel.app` |
| `OPENROUTER_API_KEY` | Optional | `sk-or-v1-...` |
| `SERP_API_KEY` | Optional | `your-key` |
| `STRIPE_SECRET_KEY` | Optional | `sk_test_...` |
| `STRIPE_WEBHOOK_SECRET` | Optional | `whsec_...` |
| `REDIS_URL` | Optional | `redis://...` |

---

## Monitoring & Logs

### Vercel Dashboard

**View Logs:**
1. Go to your Vercel project
2. Click "Deployments"
3. Click on any deployment
4. View build logs and runtime logs

**Analytics:**
- Vercel provides free analytics
- See page views, performance metrics
- Go to "Analytics" tab in your project

### Railway Dashboard

**View Logs:**
1. Go to your Railway project
2. Click on backend service
3. Click "Logs" tab
4. View real-time application logs

**Metrics:**
- CPU usage
- Memory usage
- Network traffic
- Database connections

---

## Costs & Limits

### Vercel Free Tier
- ✅ **Bandwidth:** 100GB/month
- ✅ **Build Time:** 6000 minutes/month
- ✅ **Serverless Function Execution:** 100GB-hours
- ✅ **Deployments:** Unlimited
- ✅ **Team Members:** 1
- ✅ **Custom Domains:** Yes

**Perfect for:**
- MVP and prototypes
- Small to medium traffic sites
- Personal projects

**Upgrade when:**
- Traffic exceeds 100GB/month
- Need team collaboration
- Need advanced features

### Railway Free Tier
- ✅ **Credit:** $5/month
- ✅ **Runtime:** ~500 hours/month (about 3 small services)
- ✅ **Storage:** 5GB per service
- ✅ **PostgreSQL:** Included free

**Perfect for:**
- Development and testing
- Small production apps
- MVP launches

**Upgrade when:**
- Need more runtime hours
- Need more storage
- Traffic increases significantly

---

## Next Steps

After successful deployment:

1. **🔒 Security:**
   - Rotate `SECRET_KEY` regularly
   - Use environment-specific API keys
   - Enable Stripe webhook signing

2. **📊 Monitoring:**
   - Set up error tracking (Sentry)
   - Add analytics (Google Analytics, Plausible)
   - Monitor API performance

3. **🚀 Features:**
   - Configure all API integrations
   - Test Stripe payments thoroughly
   - Add more research agents
   - Enhance UI/UX

4. **📈 Scale:**
   - Monitor usage and costs
   - Optimize database queries
   - Add caching (Redis)
   - Consider CDN for assets

---

## Support

**Issues?**
- Check [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed troubleshooting
- View platform status:
  - [Vercel Status](https://vercel-status.com)
  - [Railway Status](https://status.railway.app)

**Resources:**
- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [GitHub Issues](https://github.com/yourusername/repo/issues)

---

## ✅ Success!

Your RKO Research Platform is now live!

- **Frontend:** `https://your-project.vercel.app` ✨
- **Backend:** `https://your-backend.railway.app` 🚀
- **Cost:** $0/month 💰

**Share with the world!** 🌍

---

*Happy researching! 🔬🧪*
