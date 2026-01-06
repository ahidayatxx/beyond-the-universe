#!/bin/bash

# Auto-commit script for digital-health-competency
# Run this script from within digital-health-competency directory
# It will automatically commit and push changes to GitHub

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the script's directory (digital-health-competency)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Parent is now projects/ directory
PARENT_DIR="$(dirname "$SCRIPT_DIR")"
# Git repo is two levels up
GIT_ROOT="$(dirname "$PARENT_DIR")"

echo -e "${BLUE}🔄 Auto-commit script for digital-health-competency${NC}"
echo -e "${BLUE}📁 Working directory: ${SCRIPT_DIR}${NC}"

# Change to git root directory
cd "$GIT_ROOT"

echo -e "${BLUE}🔍 Checking for changes...${NC}"

# Check if there are any changes
TARGET_PATH="projects/digital-health-competency"
if git diff --quiet --exit-code "$TARGET_PATH" 2>/dev/null; then
    # Check for untracked files
    UNTRACKED=$(git ls-files --others --exclude-standard "$TARGET_PATH")
    if [ -z "$UNTRACKED" ]; then
        echo -e "${YELLOW}✓ No changes detected in digital-health-competency${NC}"
        exit 0
    fi
fi

# Show what changed
echo -e "${BLUE}📋 Changes detected:${NC}"
git status --short "$TARGET_PATH"

# Add all changes in the target directory
git add "$TARGET_PATH/"

# Generate commit message with timestamp
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
COMMIT_MSG="🚀 Auto-update: ${TIMESTAMP}

- Updated files in projects/digital-health-competency/
- Auto-generated commit from local development"

# Create commit
echo -e "${GREEN}💾 Creating commit...${NC}"
git commit -m "$COMMIT_MSG"

# Push to remote (beyond-the-universe branch)
echo -e "${GREEN}⬆️  Pushing to GitHub...${NC}"
git push beyond-the-universe main

echo -e "${GREEN}✅ Successfully committed and pushed changes!${NC}"
echo -e "${BLUE}🔗 View at: https://github.com/ahidayatxx/beyond-the-universe/tree/main/projects/digital-health-competency${NC}"
