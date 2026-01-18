#!/bin/bash

# 🚀 Quick Deploy Script for RKO Research Platform
# Deploys to FREE hosting platforms

set -e

echo "🚀 RKO Research Chemistry Platform - Free Deployment"
echo "======================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if git is installed
if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git is not installed. Please install git first.${NC}"
    exit 1
fi

# Check if we're in a git repo
if [ ! -d .git ]; then
    echo -e "${YELLOW}⚠️  Not a git repository. Initializing...${NC}"
    git init
    git add .
    git commit -m "Initial commit - RKO Research Platform"
fi

echo "Select deployment platform:"
echo ""
echo "1) Vercel (Frontend) + Railway (Backend) - RECOMMENDED"
echo "2) Render (All-in-One)"
echo "3) Netlify (Frontend) + Railway (Backend)"
echo "4) Manual setup"
echo ""
read -p "Enter choice [1-4]: " choice

case $choice in
    1)
        echo -e "${GREEN}📦 Deploying to Vercel + Railway${NC}"
        echo ""
        echo "Step 1: Deploy Backend to Railway"
        echo "  1. Go to https://railway.app"
        echo "  2. Click 'New Project' → 'Deploy from GitHub'"
        echo "  3. Connect this repository"
        echo "  4. Add PostgreSQL database"
        echo "  5. Set environment variables (see .env.production.example)"
        echo ""
        echo "Step 2: Deploy Frontend to Vercel"
        echo "  1. Go to https://vercel.com"
        echo "  2. Click 'New Project' → Import Git Repository"
        echo "  3. Framework: Vite, Root: frontend"
        echo "  4. Set VITE_API_URL to your Railway backend URL"
        echo "  5. Deploy!"
        echo ""
        echo "✅ Your site will be live at: https://[your-project].vercel.app"
        ;;
    2)
        echo -e "${GREEN}📦 Deploying to Render${NC}"
        echo ""
        echo "1. Go to https://render.com"
        echo "2. Click 'New' → 'Blueprint'"
        echo "3. Connect this repository"
        echo "4. Render will use render.yaml to deploy everything"
        echo "5. Add your API keys in environment variables"
        echo ""
        echo "✅ Your site will be live at: https://[your-project].onrender.com"
        ;;
    3)
        echo -e "${GREEN}📦 Deploying to Netlify + Railway${NC}"
        echo ""
        echo "Step 1: Deploy Backend to Railway (same as option 1)"
        echo ""
        echo "Step 2: Deploy Frontend to Netlify"
        echo "  1. Go to https://netlify.com"
        echo "  2. Click 'Add new site' → 'Import from Git'"
        echo "  3. Select this repository"
        echo "  4. Netlify will use netlify.toml configuration"
        echo "  5. Set VITE_API_URL to your Railway backend URL"
        echo "  6. Deploy!"
        echo ""
        echo "✅ Your site will be live at: https://[your-project].netlify.app"
        ;;
    4)
        echo -e "${YELLOW}📖 Manual Setup${NC}"
        echo ""
        echo "Please follow DEPLOYMENT_GUIDE.md for detailed instructions"
        echo ""
        ;;
    *)
        echo -e "${RED}❌ Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}🎉 Deployment setup complete!${NC}"
echo ""
echo "📚 For detailed instructions, see: DEPLOYMENT_GUIDE.md"
echo "🔧 Environment variables example: .env.production.example"
echo ""
echo "Next steps:"
echo "  1. Push this code to GitHub"
echo "  2. Follow the platform-specific instructions above"
echo "  3. Configure environment variables"
echo "  4. Test your deployment"
echo ""
echo "Need help? Check DEPLOYMENT_GUIDE.md or open an issue on GitHub"
echo ""
