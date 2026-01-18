# 📋 Deployment Quick Reference Card

Print this or keep it handy during deployment!

---

## 🎯 Platform Choice

| Platform | Best For | Cost |
|----------|----------|------|
| **Vercel + Railway** | Recommended | FREE |
| **Render** | All-in-one | FREE |
| **Netlify + Railway** | Alternative | FREE |

---

## ⚡ Quick Commands

### Generate Secret Key
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Test Frontend Build
```bash
cd frontend && npm install && npm run build
```

### Test Backend Health
```bash
curl https://your-backend.railway.app/health
# Should return: {"status":"ok"}
```

### Run Deploy Script
```bash
bash deploy.sh
```

---

## 🔧 Required Environment Variables

### Backend (Railway)

```bash
# Auto-set by Railway
DATABASE_URL=<auto>

# Must set manually
SECRET_KEY=<generate-32-chars>
CORS_ORIGINS=https://your-project.vercel.app

# Optional (for features)
OPENROUTER_API_KEY=sk-or-v1-...
SERP_API_KEY=...
STRIPE_SECRET_KEY=sk_test_...
```

### Frontend (Vercel)

```bash
# Must set
VITE_API_BASE_URL=https://your-project.railway.app

# Optional
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

---

## 📍 Important URLs

### Accounts Signup
- Vercel: https://vercel.com/signup
- Railway: https://railway.app/login
- Render: https://render.com/register
- Netlify: https://app.netlify.com/signup

### Documentation
- Vercel Docs: https://vercel.com/docs
- Railway Docs: https://docs.railway.app
- Render Docs: https://render.com/docs

### Status Pages
- Vercel Status: https://vercel-status.com
- Railway Status: https://status.railway.app

---

## 🎓 Deployment Steps

### Option 1: Vercel + Railway (Recommended)

#### Backend (Railway)
1. Go to https://railway.app
2. New Project → Deploy from GitHub
3. Add PostgreSQL database
4. Set environment variables
5. Copy backend URL

#### Frontend (Vercel)
1. Go to https://vercel.com
2. Import project from GitHub
3. Root: `frontend`
4. Add `VITE_API_BASE_URL`
5. Deploy

#### Update CORS
1. Railway → Update `CORS_ORIGINS`
2. Auto-redeploys

---

## 🧪 Test Credentials

### Stripe Test Card
```
Card: 4242 4242 4242 4242
Expiry: 12/25 (any future date)
CVC: 123 (any 3 digits)
ZIP: 12345 (any 5 digits)
```

### Test User
```
Email: test@example.com
Password: test123456
```

---

## 📊 Free Tier Limits

### Vercel
- Bandwidth: 100GB/month
- Builds: Unlimited
- Deployments: Unlimited

### Railway
- Credit: $5/month
- Runtime: ~500 hours
- PostgreSQL: 5GB

### Good for:
- 0-10,000 users
- ~50,000 requests/month
- MVP and early stage

---

## 🔍 Troubleshooting

### Issue: Frontend won't build
**Solution:** Check Vercel logs, verify `frontend` root directory

### Issue: Backend won't start
**Solution:** Check Railway logs, verify `DATABASE_URL` and `SECRET_KEY`

### Issue: CORS errors
**Solution:** Update `CORS_ORIGINS` in Railway, include Vercel domain

### Issue: Database connection failed
**Solution:** Verify PostgreSQL service running in Railway

### Issue: Environment variables not working
**Solution:** Redeploy after setting env vars

---

## 📚 Documentation Map

| Guide | Use Case | Time |
|-------|----------|------|
| **DEPLOY_NOW.md** | Ultra-quick start | 2 min read |
| **QUICK_DEPLOY.md** | 5-min deployment | 5 min read |
| **VERCEL_DEPLOY.md** | Step-by-step Vercel | 10 min read |
| **DEPLOYMENT_GUIDE.md** | Comprehensive guide | 30 min read |
| **DEPLOYMENT_CHECKLIST.md** | Verification | Use during deploy |
| **ARCHITECTURE.md** | System design | Reference |

---

## ✅ Success Checklist

Deployment is complete when:

- [ ] Frontend loads at Vercel URL
- [ ] Backend responds at Railway URL
- [ ] Health check returns `{"status":"ok"}`
- [ ] Can create account
- [ ] Can login
- [ ] No CORS errors in console
- [ ] Database connected
- [ ] HTTPS working

---

## 🆘 Need Help?

1. **Check docs:** Start with QUICK_DEPLOY.md
2. **Platform status:** Check if Vercel/Railway is down
3. **Logs:** Check deployment logs in dashboards
4. **Reset:** Redeploy from scratch if needed

---

## 🎉 Post-Deployment

After successful deployment:

1. ✅ Test all features
2. ✅ Share with users
3. ✅ Monitor logs for 24h
4. ✅ Set up analytics (optional)
5. ✅ Configure custom domain (optional)

---

## 💡 Pro Tips

- Use preview deployments (Vercel PRs)
- Monitor usage to avoid exceeding free tier
- Set up alerts for downtime
- Keep environment variables backed up
- Rotate secrets regularly
- Use test Stripe keys until ready for production

---

## 🔗 Quick Links

- **Deploy Now:** [DEPLOY_NOW.md](DEPLOY_NOW.md)
- **Full Guide:** [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Architecture:** [ARCHITECTURE.md](ARCHITECTURE.md)
- **Checklist:** [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)

---

**Last Updated:** 2024-01-18  
**Version:** 1.0.0  
**Status:** Production Ready ✅

---

**Happy Deploying! 🚀**

Print this card or save it for quick reference during deployment!
