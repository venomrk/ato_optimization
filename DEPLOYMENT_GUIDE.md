# 🚀 FREE DEPLOYMENT GUIDE - RKO Research Chemistry Platform

Deploy the complete Multi-Agent Research Chemistry Platform to **100% FREE** hosting with a **FREE domain** in under 30 minutes!

## 🎯 Quick Start - Recommended Setup

**Frontend:** Vercel (FREE)  
**Backend:** Railway.app (FREE $5/month credit)  
**Database:** Railway PostgreSQL (FREE)  
**Domain:** rko-research.vercel.app (FREE)  
**Cost:** $0/month

---

## 📋 Prerequisites

- GitHub account (free)
- Vercel account (free, sign up with GitHub)
- Railway account (free, sign up with GitHub)
- Git installed locally

---

## 🌟 OPTION 1: Vercel + Railway (Recommended)

### Step 1: Deploy Backend to Railway

1. **Sign up for Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "Login with GitHub"
   - Authorize Railway

2. **Create New Project:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Connect your repository
   - Select this repository

3. **Configure Backend Service:**
   - Railway will auto-detect the Dockerfile
   - Add environment variables:
     ```
     DATABASE_URL=<auto-filled by Railway PostgreSQL>
     SECRET_KEY=<generate-random-32-char-string>
     CORS_ORIGINS=*
     OPENROUTER_API_KEY=<your-key>
     STRIPE_SECRET_KEY=<your-stripe-key>
     ```

4. **Add PostgreSQL Database:**
   - In Railway dashboard, click "New"
   - Select "Database" → "PostgreSQL"
   - Railway automatically connects it to your service
   - `DATABASE_URL` is auto-configured

5. **Deploy:**
   - Railway automatically deploys
   - Copy your backend URL: `https://rko-research-production.up.railway.app`
   - Test: `https://your-backend.railway.app/health`

### Step 2: Deploy Frontend to Vercel

1. **Sign up for Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Sign Up with GitHub"
   - Authorize Vercel

2. **Import Project:**
   - Click "Add New" → "Project"
   - Import your GitHub repository
   - Vercel auto-detects Vite configuration

3. **Configure Build Settings:**
   - Framework Preset: `Vite`
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`

4. **Add Environment Variables:**
   - In Vercel project settings → Environment Variables:
     ```
     VITE_API_URL=https://your-backend.railway.app
     VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_stripe_key
     ```

5. **Deploy:**
   - Click "Deploy"
   - Your site will be live at: `https://rko-research.vercel.app`
   - Auto-deploys on every Git push!

### Step 3: Update CORS Settings

1. Go back to Railway dashboard
2. Update `CORS_ORIGINS` environment variable:
   ```
   CORS_ORIGINS=https://rko-research.vercel.app,https://rko-research-git-*.vercel.app
   ```
3. Railway will auto-redeploy

### Step 4: Test Your Deployment

Visit your Vercel URL: `https://rko-research.vercel.app`

✅ Frontend loads  
✅ Can create account  
✅ Can login  
✅ Research agents respond  
✅ Chemistry interface works  
✅ Stripe payments work (test mode)

---

## 🎨 OPTION 2: Render (All-in-One)

**Easiest option - Everything in one place!**

1. **Sign up for Render:**
   - Go to [render.com](https://render.com)
   - Sign up with GitHub

2. **Deploy with Blueprint:**
   - Click "New" → "Blueprint"
   - Connect your repository
   - Render will use `render.yaml`
   - Auto-creates:
     - Backend API service
     - Frontend static site
     - PostgreSQL database
     - Redis cache

3. **Configure Environment Variables:**
   - Render auto-fills most variables
   - Add your API keys:
     ```
     OPENROUTER_API_KEY=your-key
     STRIPE_SECRET_KEY=your-key
     STRIPE_PUBLISHABLE_KEY=your-key
     ```

4. **Deploy:**
   - Click "Apply"
   - Services deploy automatically
   - Frontend: `https://rko-research.onrender.com`
   - Backend: `https://rko-research-api.onrender.com`

**Note:** Render free tier spins down after 15 min of inactivity (takes ~30s to wake up).

---

## 🚂 OPTION 3: Railway (All-in-One)

1. **Deploy via Railway:**
   - Go to [railway.app](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository

2. **Railway Auto-Configuration:**
   - Detects `railway.toml`
   - Creates backend service
   - Add PostgreSQL database
   - Add Redis (optional)

3. **Manual Frontend:**
   - Use Vercel or Netlify for frontend (recommended)
   - Or add static file serving to FastAPI

4. **Environment Variables:**
   - Add all required env vars in Railway dashboard
   - Database URL auto-configured

5. **Deploy:**
   - Backend: `https://rko-research.up.railway.app`
   - Use Vercel for frontend (see Option 1)

---

## 🌐 OPTION 4: Netlify (Frontend + Serverless Functions)

1. **Sign up for Netlify:**
   - Go to [netlify.com](https://netlify.com)
   - Sign up with GitHub

2. **Import Project:**
   - Click "Add new site" → "Import from Git"
   - Select your repository
   - Netlify detects `netlify.toml`

3. **Configure:**
   - Build command: `cd frontend && npm install && npm run build`
   - Publish directory: `frontend/dist`

4. **Backend Options:**
   - Use Railway for backend (recommended)
   - Or convert FastAPI routes to Netlify Functions (advanced)

5. **Deploy:**
   - Frontend: `https://rko-research.netlify.app`

---

## 🗄️ Database Options (FREE Tier)

### Railway PostgreSQL (Recommended)
- **Storage:** 500MB
- **Always on**
- **Auto-backups**
- **Setup:** Automatic with Railway

### Neon.tech PostgreSQL
- **Storage:** 3GB free
- **Serverless:** Auto-scales to zero
- **Setup:**
  1. Go to [neon.tech](https://neon.tech)
  2. Create database
  3. Copy connection string
  4. Add to `DATABASE_URL`

### Supabase PostgreSQL
- **Storage:** 500MB
- **Features:** Auth, Storage, Realtime
- **Setup:**
  1. Go to [supabase.com](https://supabase.com)
  2. Create project
  3. Copy connection string
  4. Add to `DATABASE_URL`

### MongoDB Atlas
- **Storage:** 512MB
- **Setup:**
  1. Go to [mongodb.com/atlas](https://mongodb.com/atlas)
  2. Create free cluster
  3. Get connection string
  4. Update backend to use MongoDB (requires code changes)

---

## 🔴 Redis Cache Options (FREE Tier)

### Upstash Redis (Recommended)
- **Requests:** 10,000/day free
- **Storage:** 256MB
- **Setup:**
  1. Go to [upstash.com](https://upstash.com)
  2. Create Redis database
  3. Copy Redis URL
  4. Add to `REDIS_URL` env var

### Railway Redis
- **Included** with Railway backend
- **Storage:** Limited on free tier
- **Setup:** One-click add in Railway dashboard

---

## 🔑 Environment Variables Setup

### Backend Environment Variables

Required for all deployments:

```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Security
SECRET_KEY=random-32-character-string-generate-this

# CORS (Update with your frontend URL)
CORS_ORIGINS=https://rko-research.vercel.app

# APIs
OPENROUTER_API_KEY=sk-or-v1-your-key
SERP_API_KEY=your-serp-key

# Stripe
STRIPE_SECRET_KEY=sk_test_your_key
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret

# Optional
REDIS_URL=redis://default:pass@host:6379
```

### Frontend Environment Variables

Required for Vercel/Netlify:

```bash
# API Endpoint (Your Railway/Render backend URL)
VITE_API_URL=https://your-backend.railway.app

# Stripe
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_your_key
```

---

## 📊 Monitoring & Logs

### Vercel Dashboard
- Real-time deployment logs
- Analytics (page views, performance)
- Function logs (if using Vercel Functions)
- Domain management

### Railway Dashboard
- Application logs (live tail)
- Metrics (CPU, memory, network)
- Database metrics
- Deployments history

### Render Dashboard
- Service logs
- Performance metrics
- Deploy history
- Custom domains

---

## 🔄 Continuous Deployment

All platforms support **automatic deployments**:

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update feature"
   git push origin main
   ```

2. **Auto-Deploy:**
   - Vercel: Deploys frontend automatically
   - Railway: Deploys backend automatically
   - Render: Deploys both automatically

3. **Preview Deployments:**
   - Vercel creates preview URL for each PR
   - Test before merging to production

---

## 🎯 Custom Domain (Optional)

### Free Subdomains (Included)
- Vercel: `rko-research.vercel.app`
- Netlify: `rko-research.netlify.app`
- Railway: `rko-research.up.railway.app`
- Render: `rko-research.onrender.com`

### Custom Domain (Free with Domain Provider)
1. Buy domain (e.g., Namecheap, Google Domains)
2. In Vercel/Netlify:
   - Go to Domains
   - Add your domain
   - Update DNS records (provided by platform)
3. HTTPS automatically configured!

---

## 🧪 Stripe Test Mode

Use Stripe test keys for development:

### Test Cards
```
Card: 4242 4242 4242 4242
Expiry: Any future date
CVC: Any 3 digits
ZIP: Any 5 digits
```

### Webhook Testing
1. Install Stripe CLI: `stripe login`
2. Forward webhooks:
   ```bash
   stripe listen --forward-to https://your-backend.railway.app/api/billing/webhook
   ```
3. Get webhook secret and add to env vars

---

## 📈 Scaling (When You Grow)

### Free Tier Limits

**Vercel:**
- 100GB bandwidth/month
- Unlimited requests
- Perfect for MVP

**Railway:**
- $5 credit/month (free)
- ~500 hours runtime
- Upgradeable to $5/month

**Render:**
- 750 hours/month free
- Spins down after 15min inactivity
- $7/month for always-on

**Databases:**
- PostgreSQL: 500MB - 3GB free
- Upgrade when needed: $5-15/month

### When to Upgrade
- Traffic > 100k requests/month
- Database > 500MB
- Need 99.9% uptime
- Multiple environments (staging/prod)

---

## 🔍 Troubleshooting

### Frontend won't build
```bash
cd frontend
npm install
npm run build
```
Check for errors in console.

### Backend won't start
- Check `DATABASE_URL` is set
- Check `SECRET_KEY` is at least 32 characters
- View logs in Railway/Render dashboard

### CORS errors
- Update `CORS_ORIGINS` in backend env vars
- Include your Vercel domain
- Restart backend service

### Database connection failed
- Check `DATABASE_URL` format
- Ensure database is running (Railway/Render)
- Check database credentials

### API requests failing
- Check `VITE_API_URL` in frontend env vars
- Ensure backend is deployed and running
- Check API endpoint: `https://your-backend.railway.app/health`

---

## ✅ Deployment Checklist

- [ ] Backend deployed to Railway/Render
- [ ] PostgreSQL database created and connected
- [ ] Backend environment variables configured
- [ ] Backend health check passes: `/health`
- [ ] Frontend deployed to Vercel/Netlify
- [ ] Frontend environment variables configured
- [ ] Frontend can reach backend API
- [ ] CORS configured correctly
- [ ] User registration works
- [ ] User login works
- [ ] Research agents respond
- [ ] Chemistry interface loads
- [ ] Stripe test payments work (optional)
- [ ] Custom domain configured (optional)
- [ ] Auto-deployment on Git push enabled

---

## 🎉 You're Live!

Your RKO Multi-Agent Research Chemistry Platform is now deployed on **100% FREE** infrastructure!

**Frontend URL:** `https://rko-research.vercel.app`  
**Backend API:** `https://rko-research.up.railway.app`  
**Total Cost:** $0/month

### Next Steps:
1. Test all features thoroughly
2. Share with beta users
3. Gather feedback
4. Add monitoring (Sentry, LogRocket)
5. Set up error tracking
6. Plan for scaling when traffic grows

---

## 📚 Additional Resources

- [Vercel Documentation](https://vercel.com/docs)
- [Railway Documentation](https://docs.railway.app)
- [Render Documentation](https://render.com/docs)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)
- [Vite Deployment](https://vitejs.dev/guide/static-deploy.html)

---

## 🆘 Support

- **GitHub Issues:** Report bugs and request features
- **Community Discord:** Join for help and discussions
- **Documentation:** Check README and code comments

---

**Happy Deploying! 🚀**

*Built with ❤️ by the RKO Research Team*
