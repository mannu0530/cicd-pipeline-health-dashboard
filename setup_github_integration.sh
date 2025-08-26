#!/bin/bash

# CI/CD Dashboard - GitHub Actions Integration Setup Script
# This script helps you set up GitHub Actions monitoring

set -e

echo "🚀 CI/CD Dashboard - GitHub Actions Integration Setup"
echo "======================================================"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    if [ -f env.example ]; then
        cp env.example .env
        echo "✅ Created .env file from env.example"
    else
        echo "❌ env.example not found. Please create .env file manually."
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🔑 GitHub Configuration Required:"
echo ""

# Check if GITHUB_TOKEN is set
if grep -q "GITHUB_TOKEN=ghp_your_github_token_here" .env || ! grep -q "GITHUB_TOKEN=" .env; then
    echo "❌ GITHUB_TOKEN not configured"
    echo ""
    echo "📋 Steps to get your GitHub token:"
    echo "1. Go to: https://github.com/settings/tokens"
    echo "2. Click 'Generate new token (classic)'"
    echo "3. Select scopes: repo, workflow, read:org"
    echo "4. Copy the generated token"
    echo ""
    read -p "Enter your GitHub Personal Access Token: " github_token
    
    if [ -n "$github_token" ]; then
        # Update .env file
        if grep -q "GITHUB_TOKEN=" .env; then
            sed -i "s/GITHUB_TOKEN=.*/GITHUB_TOKEN=$github_token/" .env
        else
            echo "GITHUB_TOKEN=$github_token" >> .env
        fi
        echo "✅ GITHUB_TOKEN configured"
    else
        echo "❌ No token provided. Please configure manually in .env file"
    fi
else
    echo "✅ GITHUB_TOKEN already configured"
fi

echo ""
echo "📚 Repository Configuration:"
echo ""

# Check if GITHUB_REPOS is set
if grep -q "GITHUB_REPOS=$" .env || ! grep -q "GITHUB_REPOS=" .env; then
    echo "❌ GITHUB_REPOS not configured"
    echo ""
    echo "📋 Repository format examples:"
    echo "- Single repo: username/repository-name"
    echo "- Multiple repos: owner/repo1,owner/repo2"
    echo "- Org repos: org-name/project-name"
    echo ""
    read -p "Enter repositories to monitor (comma-separated): " github_repos
    
    if [ -n "$github_repos" ]; then
        # Update .env file
        if grep -q "GITHUB_REPOS=" .env; then
            sed -i "s/GITHUB_REPOS=.*/GITHUB_REPOS=$github_repos/" .env
        else
            echo "GITHUB_REPOS=$github_repos" >> .env
        fi
        echo "✅ GITHUB_REPOS configured: $github_repos"
    else
        echo "❌ No repositories provided. Please configure manually in .env file"
    fi
else
    echo "✅ GITHUB_REPOS already configured"
fi

echo ""
echo "🔐 Webhook Configuration (Optional):"
echo ""

# Check if WEBHOOK_SECRET is set
if grep -q "WEBHOOK_SECRET=your_webhook_secret_here" .env || ! grep -q "WEBHOOK_SECRET=" .env; then
    echo "❌ WEBHOOK_SECRET not configured"
    echo ""
    echo "📋 Webhook secret is required for real-time updates"
    echo "Generate a strong, random string for security"
    echo ""
    read -p "Enter webhook secret (or press Enter to skip): " webhook_secret
    
    if [ -n "$webhook_secret" ]; then
        # Update .env file
        if grep -q "WEBHOOK_SECRET=" .env; then
            sed -i "s/WEBHOOK_SECRET=.*/WEBHOOK_SECRET=$webhook_secret/" .env
        else
            echo "WEBHOOK_SECRET=$webhook_secret" >> .env
        fi
        echo "✅ WEBHOOK_SECRET configured"
    else
        echo "⚠️  Webhook secret not set. Real-time updates will be disabled."
    fi
else
    echo "✅ WEBHOOK_SECRET already configured"
fi

echo ""
echo "⚙️  Provider Configuration:"
echo ""

# Ensure GitHub is enabled in providers
if grep -q "PROVIDERS=" .env; then
    current_providers=$(grep "PROVIDERS=" .env | cut -d'=' -f2)
    if [[ ! "$current_providers" =~ "github" ]]; then
        new_providers="$current_providers,github"
        sed -i "s/PROVIDERS=.*/PROVIDERS=$new_providers/" .env
        echo "✅ Added GitHub to PROVIDERS: $new_providers"
    else
        echo "✅ GitHub already enabled in PROVIDERS: $current_providers"
    fi
else
    echo "PROVIDERS=github" >> .env
    echo "✅ Set PROVIDERS=github"
fi

echo ""
echo "🔍 Current Configuration Summary:"
echo "=================================="
echo ""

# Display current configuration
echo "GitHub Token: $(grep "GITHUB_TOKEN=" .env | cut -d'=' -f2 | sed 's/ghp_/ghp_***/' | sed 's/gho_/gho_***/')"
echo "Repositories: $(grep "GITHUB_REPOS=" .env | cut -d'=' -f2)"
echo "Webhook Secret: $(grep "WEBHOOK_SECRET=" .env | cut -d'=' -f2 | sed 's/^./*/' | sed 's/.$/*/')"
echo "Providers: $(grep "PROVIDERS=" .env | cut -d'=' -f2)"
echo "Polling Interval: $(grep "COLLECTOR_POLL_SECONDS=" .env | cut -d'=' -f2 || echo '30') seconds"

echo ""
echo "🚀 Next Steps:"
echo "==============="
echo ""

if grep -q "WEBHOOK_SECRET=" .env && [ "$(grep "WEBHOOK_SECRET=" .env | cut -d'=' -f2)" != "your_webhook_secret_here" ]; then
    echo "1. ✅ Start the dashboard: docker compose up --build"
    echo "2. 🔗 Configure GitHub webhooks for real-time updates:"
    echo "   - Go to each repository's Settings → Webhooks"
    echo "   - Add webhook: https://your-domain.com/api/webhooks/github"
    echo "   - Secret: $(grep "WEBHOOK_SECRET=" .env | cut -d'=' -f2)"
    echo "   - Events: Workflow runs"
    echo "3. 📊 View dashboard: http://localhost:5173"
    echo "4. 📚 API docs: http://localhost:8000/docs"
else
    echo "1. ✅ Start the dashboard: docker compose up --build"
    echo "2. 📊 View dashboard: http://localhost:5173 (updates every 30 seconds)"
    echo "3. 📚 API docs: http://localhost:8000/docs"
    echo "4. 🔗 Optional: Configure webhooks for real-time updates"
fi

echo ""
echo "📖 For detailed instructions, see: GITHUB_ACTIONS_INTEGRATION.md"
echo "🐛 For troubleshooting, see the troubleshooting section in the integration guide"
echo ""
echo "🎉 Setup complete! Happy monitoring! 🎉"
