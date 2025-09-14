# 🚀 Streamlit Deployment Guide

This guide will help you deploy your Atlan Customer Copilot application to Streamlit Cloud.

## 📋 Prerequisites

1. **GitHub Account**: Your code needs to be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io)
3. **API Keys**:
   - Claude API Key from [Anthropic Console](https://console.anthropic.com)
   - Tavily API Key from [Tavily](https://tavily.com)

## 🚀 Deployment Steps

### Step 1: Push to GitHub

1. **Initialize Git repository** (if not already done):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Atlan Customer Copilot Streamlit app"
   ```

2. **Create GitHub repository** and push:
   ```bash
   git remote add origin https://github.com/yourusername/atlan-customer-copilot.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud**: Visit [share.streamlit.io](https://share.streamlit.io)

2. **Sign in with GitHub**: Use your GitHub account to sign in

3. **Create New App**:
   - Click "New app"
   - Select your GitHub repository
   - Choose the branch (usually `main`)
   - Set the main file path to `streamlit_app.py`

4. **Configure App**:
   - **App URL**: Choose a unique URL for your app
   - **Main file**: `streamlit_app.py`
   - **Python version**: 3.11

### Step 3: Set Environment Variables

In the Streamlit Cloud dashboard, go to your app's settings and add these secrets:

```toml
CLAUDE_API_KEY = "your_actual_claude_api_key"
TAVILY_API_KEY = "your_actual_tavily_api_key"
DEBUG = "false"
```

**How to add secrets:**
1. Go to your app dashboard on Streamlit Cloud
2. Click "Settings" (gear icon)
3. Scroll down to "Secrets"
4. Add the above variables in the secrets format

### Step 4: Deploy

1. Click "Deploy!" button
2. Wait for the deployment to complete (usually 2-5 minutes)
3. Your app will be available at `https://your-app-name.streamlit.app`

## 🧪 Local Testing

Before deploying, test your app locally:

```bash
# Install Streamlit
pip install streamlit

# Run the app locally
streamlit run streamlit_app.py
```

## 🌐 Access Your Deployed App

After successful deployment:
- **App URL**: `https://your-app-name.streamlit.app`
- **Admin Dashboard**: Available in your Streamlit Cloud account

## 🔧 App Features

Your deployed Streamlit app includes:

### 💬 Interactive Chat
- Real-time AI-powered responses
- Topic classification and sentiment analysis
- Priority scoring
- Source attribution from Tavily search

### 📁 File Upload
- Support for multiple file formats (PDF, DOCX, TXT, CSV, JSON, HTML, MD, LOG, XML, YAML)
- Automatic ticket extraction from uploaded files
- Batch processing capabilities

### 📊 Analytics Dashboard
- Chat history tracking
- Sentiment distribution charts
- Topic analysis
- Priority metrics
- Export functionality

## 🛠️ Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all dependencies are in `requirements_streamlit.txt`
   - Check that file paths are correct

2. **API Key Issues**:
   - Verify secrets are set correctly in Streamlit Cloud
   - Check that API keys are valid and have sufficient credits

3. **Memory Issues**:
   - Streamlit Cloud has memory limits
   - Consider optimizing large file processing

4. **Timeout Issues**:
   - Some AI operations may take time
   - Consider adding progress indicators

### Debug Commands

```bash
# Check Streamlit version
streamlit --version

# Run with debug mode
streamlit run streamlit_app.py --logger.level debug

# Check app logs in Streamlit Cloud dashboard
```

## 📊 Monitoring

### Streamlit Cloud Dashboard
- Monitor app performance
- View usage statistics
- Check error logs
- Manage app settings

### Health Checks
Your app includes automatic health monitoring and error handling.

## 🔒 Security Best Practices

1. **API Keys**: Never commit API keys to Git
2. **Secrets**: Use Streamlit's secrets management
3. **Rate Limiting**: Consider implementing rate limiting for production use
4. **HTTPS**: Streamlit Cloud provides automatic HTTPS

## 📈 Scaling

### Free Tier Limitations
- 1 app per GitHub account
- Limited compute resources
- No custom domains

### Pro Features (Paid)
- Multiple apps
- More compute resources
- Custom domains
- Advanced monitoring

## 🆘 Support

- **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io)
- **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io)
- **GitHub Issues**: Create issues in your repository

## 🎉 Next Steps

After successful deployment:

1. **Test all features** thoroughly
2. **Share your app** with team members
3. **Monitor usage** and performance
4. **Gather feedback** and iterate
5. **Consider upgrading** to Pro for production use

---

**🎉 Congratulations! Your Atlan Customer Copilot is now live on Streamlit Cloud!**
