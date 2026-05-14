#!/bin/bash
# Weekly wiki update script — re-fetches public sources and pushes to GitHub
# Run by scheduled Claude agent every Sunday

set -e

WIKI_DIR="/Users/ictadmin/Library/CloudStorage/GoogleDrive-ameya.agrawal@mitwpu.edu.in/My Drive/Ameya Agrawal/Ameya WPU Claude Desktop"
SITE_DIR="$HOME/ameya-wiki"

# Sync latest wiki pages to the site repo
rsync -av --delete \
  --exclude 'raw/' \
  "$WIKI_DIR/wiki/" \
  "$SITE_DIR/wiki/"

# Commit and push if anything changed
cd "$SITE_DIR"
git add wiki/
if git diff --staged --quiet; then
  echo "No changes to commit."
else
  git commit -m "Weekly wiki update: $(date '+%Y-%m-%d')"
  git push origin main
  echo "Pushed updates to GitHub."
fi
