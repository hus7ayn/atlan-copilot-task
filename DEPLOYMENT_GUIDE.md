# 🚀 Railway Deployment Guide

## Quick Deployment Steps

### 1. **Prepare Your Repository**
Make sure your code is pushed to GitHub:
```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 2. **Deploy to Railway**

#### Option A: Deploy via Railway Dashboard (Recommended)
1. Go to [railway.app](https://railway.app)
2. Sign up/Login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `ATLAN_CUSTOMER_COPILOT` repository
5. Railway will automatically detect it's a Python/FastAPI app
6. Click "Deploy"

#### Option B: Deploy via Railway CLI
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy from your project directory
railway deploy
```

### 3. **Configure Environment Variables**

In Railway dashboard, go to your project → Variables tab and add:

```env
# Required API Keys
CLAUDE_API_KEY=your_claude_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here

# Optional Configuration
CLAUDE_MODEL=claude-3-5-sonnet-20241022
CLAUDE_TEMPERATURE=0.1
CLAUDE_MAX_TOKENS=1000
DEBUG=False
```

### 4. **Access Your Deployed App**

After deployment (usually 2-3 minutes):
- Railway will provide you with a URL like: `https://your-app-name.up.railway.app`
- Your app will be accessible at this URL
- API docs will be at: `https://your-app-name.up.railway.app/docs`

## 🎯 What Happens During Deployment

1. **Railway detects** your Python/FastAPI app
2. **Installs dependencies** from `requirements.txt`
3. **Builds React frontend** (`npm run build`)
4. **Starts FastAPI server** on the provided PORT
5. **Serves both API and React app** from the same domain

## 🔧 Custom Domain (Optional)

1. In Railway dashboard → Settings → Domains
2. Add your custom domain (e.g., `your-app.com`)
3. Railway provides SSL certificate automatically

## 📊 Monitoring & Logs

- **Logs**: Available in Railway dashboard → Deployments → View Logs
- **Metrics**: CPU, Memory, Network usage
- **Deployments**: Automatic deployments on git push

## 💰 Pricing

- **Free Tier**: $5 credit monthly (usually enough for development)
- **Pro**: $20/month for production use
- **No credit card required** for free tier

## 🛠️ Troubleshooting

### Common Issues:

1. **Build Fails**: Check logs in Railway dashboard
2. **Environment Variables**: Ensure all required vars are set
3. **API Keys**: Make sure Claude and Tavily keys are valid
4. **CORS Issues**: Already configured in your FastAPI app

### Debug Commands:
```bash
# Check Railway logs
railway logs

# Check deployment status
railway status

# Redeploy
railway redeploy
```

## 🎉 Success!

Once deployed, your Atlan Customer Copilot will be live at your Railway URL with:
- ✅ Interactive AI Agent
- ✅ Real-time documentation search
- ✅ Ticket classification
- ✅ File upload and parsing
- ✅ Full-stack functionality

## 📱 Mobile Access

Your deployed app will work on:
- Desktop browsers
- Mobile browsers
- Tablet browsers
- Progressive Web App (PWA) capabilities
