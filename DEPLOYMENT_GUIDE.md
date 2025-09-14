# 🚀 Atlan Customer Copilot Deployment Guide

This guide will help you deploy your Atlan Customer Copilot application to production using Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **API Keys**:
   - Claude API Key from [Anthropic Console](https://console.anthropic.com)
   - Tavily API Key from [Tavily](https://tavily.com)

## 🚀 Quick Deployment (Recommended)

### Option 1: Automated Deployment

```bash
# Run the deployment script
./deploy.sh
```

### Option 2: Manual Deployment

#### Step 1: Install Railway CLI
```bash
npm install -g @railway/cli
```

#### Step 2: Login to Railway
```bash
railway login
```

#### Step 3: Initialize Project
```bash
railway init
```

#### Step 4: Set Environment Variables
Go to your Railway project dashboard → Variables tab and add:

```env
CLAUDE_API_KEY=your_actual_claude_api_key
TAVILY_API_KEY=your_actual_tavily_api_key
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

#### Step 5: Deploy
```bash
railway up
```

## 🌐 Access Your Deployed Application

After deployment, you'll get a URL like: `https://your-app-name.railway.app`

- **API Endpoint**: `https://your-app-name.railway.app/api/`
- **Health Check**: `https://your-app-name.railway.app/api/health`
- **API Docs**: `https://your-app-name.railway.app/docs`

## 🔧 Frontend Deployment (Optional)

If you want to deploy the React frontend separately:

### Using Vercel (Recommended)
1. Go to [vercel.com](https://vercel.com)
2. Connect your GitHub repository
3. Set build command: `cd client && npm run build`
4. Set output directory: `client/build`
5. Add environment variable: `REACT_APP_API_URL=https://your-app-name.railway.app`

### Using Netlify
1. Go to [netlify.com](https://netlify.com)
2. Connect your GitHub repository
3. Set build command: `cd client && npm run build`
4. Set publish directory: `client/build`
5. Add environment variable: `REACT_APP_API_URL=https://your-app-name.railway.app`

## 🔍 Monitoring & Debugging

### Railway Dashboard
- Monitor logs: Railway Dashboard → Your Project → Deployments
- View metrics: Railway Dashboard → Your Project → Metrics
- Manage environment variables: Railway Dashboard → Your Project → Variables

### Health Checks
Your app includes automatic health checks at `/api/health`

### Logs
```bash
# View live logs
railway logs

# View specific deployment logs
railway logs --deployment your-deployment-id
```

## 🛠️ Troubleshooting

### Common Issues

1. **API Keys Not Working**
   - Verify keys are correctly set in Railway Variables
   - Check that keys don't have extra spaces or quotes

2. **CORS Issues**
   - Update `CLIENT_URL` environment variable with your frontend URL
   - Ensure `DEBUG=False` in production

3. **Build Failures**
   - Check Railway logs for specific error messages
   - Verify all dependencies are in `requirements.txt`

4. **App Not Starting**
   - Check that port is set to `$PORT` (Railway requirement)
   - Verify health check endpoint is working

### Debug Commands
```bash
# Check Railway status
railway status

# View current environment variables
railway variables

# Connect to Railway shell
railway connect

# Restart deployment
railway redeploy
```

## 📊 Performance Optimization

### Production Settings
- Set `DEBUG=False` for better performance
- Use production-grade API keys
- Monitor API usage and costs

### Scaling
Railway automatically scales your application based on traffic. For high-traffic applications, consider:
- Upgrading Railway plan
- Implementing caching strategies
- Using CDN for static assets

## 🔒 Security Best Practices

1. **Environment Variables**: Never commit API keys to Git
2. **CORS**: Restrict origins in production
3. **HTTPS**: Railway provides automatic HTTPS
4. **Rate Limiting**: Consider implementing rate limiting for API endpoints

## 📈 Next Steps

After successful deployment:
1. Test all endpoints using the API documentation
2. Set up monitoring and alerting
3. Configure custom domain (optional)
4. Set up CI/CD for automatic deployments

## 🆘 Support

- Railway Documentation: [docs.railway.app](https://docs.railway.app)
- Railway Discord: [discord.gg/railway](https://discord.gg/railway)
- Project Issues: Create an issue in your GitHub repository

---

**🎉 Congratulations! Your Atlan Customer Copilot is now live in production!**
