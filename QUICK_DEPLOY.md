# ⚡ QUICK DEPLOY - 5 Minutes to Production

## 🎯 Fastest Path: Vercel + Railway

### 1️⃣ Backend (Railway) - 2 minutes

```bash
1. Go to: https://railway.app
2. Login with GitHub
3. New Project → Deploy from GitHub → Select this repo
4. Add PostgreSQL: Click "New" → Database → PostgreSQL
5. Set variables:
   - SECRET_KEY: [generate random 32 chars]
   - CORS_ORIGINS: *
6. Done! Copy backend URL: https://xxx.railway.app
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2️⃣ Frontend (Vercel) - 2 minutes

```bash
1. Go to: https://vercel.com
2. Login with GitHub
3. Import → Select this repo
4. Root Directory: frontend
5. Add env var:
   - VITE_API_BASE_URL: [your Railway backend URL]
6. Deploy!
```

### 3️⃣ Update CORS - 30 seconds

```bash
1. Back to Railway
2. Update CORS_ORIGINS: https://your-project.vercel.app
3. Auto-redeploys
```

### 4️⃣ Test - 30 seconds

Visit: `https://your-project.vercel.app`

✅ Create account  
✅ Login  
✅ It works!

---

## 🚀 Your URLs

**Frontend:** `https://your-project.vercel.app`  
**Backend:** `https://your-project.railway.app`  
**API Docs:** `https://your-project.railway.app/docs`

---

## 🔑 Environment Variables

### Railway (Backend)

| Variable | Value | Required |
|----------|-------|----------|
| `DATABASE_URL` | Auto-set by Railway | ✅ |
| `SECRET_KEY` | Random 32+ chars | ✅ |
| `CORS_ORIGINS` | Your Vercel URL | ✅ |
| `OPENROUTER_API_KEY` | Your key | Optional |
| `SERP_API_KEY` | Your key | Optional |
| `STRIPE_SECRET_KEY` | Your key | Optional |

### Vercel (Frontend)

| Variable | Value | Required |
|----------|-------|----------|
| `VITE_API_BASE_URL` | Railway backend URL | ✅ |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Your key | Optional |

---

## 💰 Cost

**Total: $0/month**

- Vercel: Free forever
- Railway: $5 credit/month (free)

---

## 🆘 Troubleshooting

**Can't login?**
→ Check Railway logs, ensure DATABASE_URL is set

**CORS errors?**
→ Update CORS_ORIGINS in Railway to match Vercel domain

**Frontend won't build?**
→ Check Vercel logs, ensure `frontend` is root directory

**Backend won't start?**
→ Check Railway logs, ensure SECRET_KEY is 32+ chars

---

## 📚 More Info

- **Detailed Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Vercel Guide:** [VERCEL_DEPLOY.md](VERCEL_DEPLOY.md)
- **Full README:** [README.md](README.md)

---

**That's it! You're live! 🎉**
