#!/bin/bash

# Atlan Customer Copilot - Streamlit Deployment Script

echo "🚀 Atlan Customer Copilot - Streamlit Deployment"
echo "================================================"

# Check if we're in a git repository
if [ ! -d ".git" ]; then
    echo "📁 Initializing Git repository..."
    git init
    echo "✅ Git repository initialized"
fi

# Check if remote origin exists
if ! git remote get-url origin >/dev/null 2>&1; then
    echo ""
    echo "🔗 Please add your GitHub repository as origin:"
    echo "   git remote add origin https://github.com/yourusername/your-repo-name.git"
    echo ""
    read -p "Press Enter after you've added the remote origin..."
fi

# Add all files
echo "📦 Adding files to Git..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "Deploy Atlan Customer Copilot Streamlit app - $(date)"

# Push to GitHub
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ Code pushed to GitHub successfully!"
echo ""
echo "🌐 Next steps for Streamlit deployment:"
echo "1. Go to https://share.streamlit.io"
echo "2. Sign in with your GitHub account"
echo "3. Click 'New app'"
echo "4. Select your repository"
echo "5. Set main file path to: streamlit_app.py"
echo "6. Add your API keys in the secrets section:"
echo "   - CLAUDE_API_KEY=your_claude_api_key"
echo "   - TAVILY_API_KEY=your_tavily_api_key"
echo "7. Click 'Deploy!'"
echo ""
echo "🎉 Your app will be available at: https://your-app-name.streamlit.app"
echo ""
echo "📚 For detailed instructions, see STREAMLIT_DEPLOYMENT.md"
