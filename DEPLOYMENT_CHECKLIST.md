# ✅ Deployment Checklist

Use this checklist to ensure a smooth deployment of the RKO Research Platform.

## Pre-Deployment

### Code Preparation

- [ ] All code committed to Git
- [ ] `.env` files not committed (in `.gitignore`)
- [ ] Dependencies up to date
  - [ ] `backend/requirements.txt` updated
  - [ ] `frontend/package.json` updated
- [ ] No console.log() statements in production code
- [ ] No hardcoded API keys or secrets
- [ ] All TODO comments addressed or documented

### Testing

- [ ] Frontend builds successfully (`cd frontend && npm run build`)
- [ ] Backend starts without errors (`cd backend && uvicorn app.main:app`)
- [ ] Can create user account
- [ ] Can log in
- [ ] Can log out
- [ ] API endpoints respond correctly
- [ ] Database migrations work
- [ ] CORS settings allow frontend domain

### Documentation

- [ ] README.md updated
- [ ] Environment variables documented
- [ ] API endpoints documented
- [ ] Deployment instructions reviewed

---

## Backend Deployment (Railway)

### Account Setup

- [ ] Railway account created (https://railway.app)
- [ ] GitHub account connected
- [ ] Repository access granted

### Project Creation

- [ ] New Railway project created
- [ ] Repository connected
- [ ] Correct branch selected (usually `main`)

### Database Setup

- [ ] PostgreSQL database added
- [ ] Database connected to backend service
- [ ] `DATABASE_URL` automatically set
- [ ] Database accessible from backend

### Environment Variables

Set these in Railway dashboard → Variables:

- [ ] `SECRET_KEY` (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`)
- [ ] `CORS_ORIGINS` (your Vercel domain, e.g., `https://your-project.vercel.app`)
- [ ] `OPENROUTER_API_KEY` (optional, for AI chat)
- [ ] `SERP_API_KEY` (optional, for research)
- [ ] `STRIPE_SECRET_KEY` (optional, for payments)
- [ ] `STRIPE_WEBHOOK_SECRET` (optional, for Stripe webhooks)

### Deployment

- [ ] Initial deployment completed
- [ ] Build logs checked for errors
- [ ] Service running (green status)
- [ ] Health check passing: `/health` endpoint returns `{"status":"ok"}`
- [ ] Backend URL copied (e.g., `https://your-project.railway.app`)

### Post-Deployment Verification

- [ ] Can access API docs: `https://your-backend.railway.app/docs`
- [ ] Health endpoint works: `https://your-backend.railway.app/health`
- [ ] Database connection successful
- [ ] Environment variables loaded correctly

---

## Frontend Deployment (Vercel)

### Account Setup

- [ ] Vercel account created (https://vercel.com)
- [ ] GitHub account connected
- [ ] Repository access granted

### Project Import

- [ ] Repository imported to Vercel
- [ ] Correct framework detected (Vite)
- [ ] Root directory set to: `frontend`
- [ ] Build command: `npm run build`
- [ ] Output directory: `dist`

### Environment Variables

Set these in Vercel dashboard → Settings → Environment Variables:

- [ ] `VITE_API_BASE_URL` (Railway backend URL from previous step)
- [ ] `VITE_STRIPE_PUBLISHABLE_KEY` (optional, for payments)

### Deployment

- [ ] Initial deployment triggered
- [ ] Build logs checked for errors
- [ ] Deployment successful (green status)
- [ ] Frontend URL received (e.g., `https://your-project.vercel.app`)

### Post-Deployment Verification

- [ ] Website loads without errors
- [ ] Can navigate between pages
- [ ] API calls reach backend successfully
- [ ] No CORS errors in browser console
- [ ] Images and assets load correctly
- [ ] Mobile responsive design works

---

## CORS Configuration Update

After getting your Vercel domain:

- [ ] Update `CORS_ORIGINS` in Railway backend
- [ ] Include both production and preview URLs:
  ```
  CORS_ORIGINS=https://your-project.vercel.app,https://your-project-git-*.vercel.app
  ```
- [ ] Railway service redeployed automatically
- [ ] CORS errors resolved

---

## Feature Testing

### Authentication

- [ ] Can create new account
- [ ] Email validation works
- [ ] Password validation works (min length, etc.)
- [ ] Receives 100 free credits on signup
- [ ] Can log in with credentials
- [ ] JWT token stored correctly
- [ ] Can log out
- [ ] Protected routes redirect to login

### Research Features

- [ ] Can search for papers (if SerpAPI key configured)
- [ ] Search results display correctly
- [ ] Credits deducted for searches
- [ ] Search history saved
- [ ] Can view paper details

### AI Chat

- [ ] Can send messages (if OpenRouter key configured)
- [ ] AI responds correctly
- [ ] Credits deducted for chat (5 per message)
- [ ] Chat history saved
- [ ] Can view previous conversations

### Billing (if Stripe configured)

- [ ] Can view current credit balance
- [ ] Can initiate checkout session
- [ ] Redirected to Stripe checkout
- [ ] Test payment works (card: 4242 4242 4242 4242)
- [ ] Credits added after successful payment
- [ ] Webhook receives payment confirmation

### User Profile

- [ ] Can view profile information
- [ ] Can update profile (name, etc.)
- [ ] Profile changes saved
- [ ] Can view subscription status (if applicable)

---

## Monitoring Setup

### Vercel

- [ ] Analytics enabled
- [ ] Deployment notifications configured
- [ ] Error alerts set up (optional)
- [ ] Performance monitoring active

### Railway

- [ ] Metrics dashboard reviewed
- [ ] Log retention configured
- [ ] Resource usage monitored
- [ ] Alerts configured for downtime (optional)

### External Monitoring (Optional)

- [ ] UptimeRobot configured for uptime monitoring
- [ ] Sentry configured for error tracking
- [ ] Google Analytics added (if needed)

---

## Security Checklist

### Environment Variables

- [ ] No secrets in code or commits
- [ ] All sensitive data in environment variables
- [ ] Different keys for dev/staging/production
- [ ] Stripe test keys for development
- [ ] Stripe live keys for production (when ready)

### API Security

- [ ] CORS properly configured
- [ ] JWT tokens expire correctly (30 min default)
- [ ] Password hashing enabled (bcrypt)
- [ ] SQL injection prevention (SQLAlchemy ORM)
- [ ] Input validation (Pydantic schemas)
- [ ] Rate limiting considered (future)

### HTTPS/SSL

- [ ] Frontend served over HTTPS (Vercel automatic)
- [ ] Backend served over HTTPS (Railway automatic)
- [ ] No mixed content warnings
- [ ] SSL certificates valid

---

## Performance Optimization

### Frontend

- [ ] Bundle size optimized
- [ ] Images optimized
- [ ] Lazy loading implemented where appropriate
- [ ] Service worker configured (optional)
- [ ] Caching strategy defined

### Backend

- [ ] Database queries optimized
- [ ] Indexes created for frequent queries
- [ ] Connection pooling configured
- [ ] Response compression enabled
- [ ] API response caching considered (Redis, future)

### Database

- [ ] Proper indexes created
- [ ] Query performance monitored
- [ ] Backup strategy defined
- [ ] Storage limits monitored

---

## Continuous Deployment

### Automatic Deployments

- [ ] Git push triggers Vercel deployment (frontend)
- [ ] Git push triggers Railway deployment (backend)
- [ ] Preview deployments work for PRs (Vercel)
- [ ] Deployment notifications enabled

### Rollback Plan

- [ ] Know how to rollback Vercel deployment
- [ ] Know how to rollback Railway deployment
- [ ] Database backup available
- [ ] Incident response plan documented

---

## DNS and Domain (Optional)

### Custom Domain

- [ ] Domain purchased (if using custom domain)
- [ ] DNS configured in domain registrar
- [ ] Domain added to Vercel
- [ ] HTTPS configured for custom domain
- [ ] CORS updated to include custom domain

---

## Documentation

### User Documentation

- [ ] README.md complete and accurate
- [ ] API documentation updated
- [ ] User guide created (optional)
- [ ] FAQ prepared (optional)

### Developer Documentation

- [ ] DEPLOYMENT_GUIDE.md reviewed
- [ ] ARCHITECTURE.md reviewed
- [ ] Environment variables documented
- [ ] Setup instructions tested

---

## Post-Deployment

### Communication

- [ ] Stakeholders notified of deployment
- [ ] Users informed (if applicable)
- [ ] Social media announcement (optional)
- [ ] Landing page updated with live URL

### Monitoring

- [ ] Monitor for 24 hours after deployment
- [ ] Check error rates
- [ ] Review performance metrics
- [ ] User feedback collected

### Optimization

- [ ] Identify bottlenecks
- [ ] Plan optimizations
- [ ] Schedule updates
- [ ] Document lessons learned

---

## Maintenance Plan

### Regular Tasks

- [ ] Weekly: Check error logs
- [ ] Weekly: Monitor resource usage
- [ ] Monthly: Review and rotate secrets
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Review costs and scaling needs

### Backup Strategy

- [ ] Database backups automated (Railway automatic)
- [ ] Environment variables backed up securely
- [ ] Code in version control (Git)
- [ ] Recovery plan documented

---

## Troubleshooting

### Common Issues

#### Frontend won't load
1. Check Vercel deployment logs
2. Verify build completed successfully
3. Check browser console for errors
4. Verify environment variables set

#### Backend API errors
1. Check Railway logs
2. Verify DATABASE_URL is set
3. Check CORS_ORIGINS includes frontend domain
4. Test health endpoint: `/health`

#### Database connection failed
1. Verify PostgreSQL service running
2. Check DATABASE_URL format
3. Review Railway database logs
4. Check connection limits

#### CORS errors
1. Update CORS_ORIGINS in Railway
2. Include Vercel domain exactly as shown in browser
3. Redeploy Railway service
4. Clear browser cache

---

## Success Criteria

Before marking deployment as complete:

- [x] ✅ Frontend accessible at Vercel URL
- [x] ✅ Backend accessible at Railway URL
- [x] ✅ Database connected and migrations run
- [x] ✅ User can create account
- [x] ✅ User can log in
- [x] ✅ API calls work without CORS errors
- [x] ✅ Health check returns OK
- [x] ✅ All environment variables set correctly
- [x] ✅ HTTPS working on all endpoints
- [x] ✅ No errors in production logs
- [x] ✅ Performance acceptable (< 2s page load)
- [x] ✅ Mobile responsive
- [x] ✅ Documentation complete

---

## Emergency Contacts

**Platform Status Pages:**
- Vercel: https://vercel-status.com
- Railway: https://status.railway.app

**Support:**
- Vercel: support@vercel.com
- Railway: team@railway.app

**Documentation:**
- Vercel: https://vercel.com/docs
- Railway: https://docs.railway.app

---

## Deployment Complete! 🎉

Once all items are checked:

1. Mark deployment as successful
2. Update DEPLOYMENT_STATUS.md
3. Notify team/stakeholders
4. Celebrate! 🎊

**Your RKO Research Platform is now LIVE!**

---

*Last Updated: [Date]*  
*Deployed By: [Name]*  
*Deployment Environment: Production*
