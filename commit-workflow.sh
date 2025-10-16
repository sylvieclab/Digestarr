#!/bin/bash

# Script to commit and push the GitHub Actions workflow update

echo "📝 Committing GitHub Actions workflow update..."

cd "C:\Users\Administrator\Documents\Github\Digestarr"

# Check current branch
echo "Current branch:"
git branch --show-current

# Stage the workflow file
git add .github/workflows/docker-build.yml

# Commit
git commit -m "ci: Add dev branch to Docker Hub automated builds

- Dev branch pushes now trigger Docker image builds
- Creates sylviecanuck/digestarr:dev tag automatically
- Allows testing features before merging to main/latest"

# Push to dev branch
git push origin dev

echo ""
echo "✅ Workflow updated and pushed to dev branch!"
echo ""
echo "📦 Next steps:"
echo "1. GitHub Actions will automatically build sylviecanuck/digestarr:dev"
echo "2. Wait 5-10 minutes for build to complete"
echo "3. Check GitHub Actions tab: https://github.com/sylvieclab/Digestarr/actions"
echo "4. Once complete, pull new image on Unraid:"
echo "   docker pull sylviecanuck/digestarr:dev"
echo "   docker stop digestarr"
echo "   docker rm digestarr"
echo "   (recreate container with :dev tag in Unraid UI)"
echo ""
echo "🔄 Future workflow:"
echo "- Push to dev → builds :dev tag → test on Unraid"
echo "- Merge dev → main → builds :latest tag → production"
