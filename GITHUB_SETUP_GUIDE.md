# GitHub Setup & Afrihost Git Deployment Guide

## Part 1: Push to GitHub

### Step 1: Create GitHub Repository

1. **Go to GitHub:** https://github.com/mariuserasmus
2. **Click "New" or "+" → "New repository"**
3. **Repository settings:**
   - **Name:** `snowspoiledgifts`
   - **Description:** "Snow's Spoiled Gifts - E-commerce Flask Application"
   - **Visibility:** **Private** (recommended for production code)
   - **DO NOT** check "Initialize with README" (you already have files)
   - **DO NOT** add .gitignore or license (already have them)
4. **Click "Create repository"**

### Step 2: Push Your Code to GitHub

After creating the repository, GitHub will show commands. Use these:

```bash
# Add GitHub as remote origin
git remote add origin https://github.com/mariuserasmus/snowspoiledgifts.git

# Rename branch to main (GitHub's default)
git branch -M main

# Push all commits to GitHub
git push -u origin main
```

**You'll be prompted for credentials:**
- **Username:** `mariuserasmus`
- **Password:** Use a **Personal Access Token** (not your GitHub password)

### Step 3: Create GitHub Personal Access Token

GitHub no longer accepts passwords for Git operations. You need a token:

1. **Go to:** https://github.com/settings/tokens
2. **Click:** "Generate new token" → "Generate new token (classic)"
3. **Settings:**
   - **Note:** `Snow's Spoiled Gifts Deployment`
   - **Expiration:** 90 days (or custom)
   - **Scopes:** Check `repo` (full control of private repositories)
4. **Click:** "Generate token"
5. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
   - Example: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

**Use this token as your password when pushing to GitHub.**

### Step 4: Verify Push

After pushing, visit: https://github.com/mariuserasmus/snowspoiledgifts

You should see all your files and 8 commits!

---

## Part 2: Setup Git on Afrihost Server

Now let's configure your Afrihost server to pull updates from GitHub.

### Option A: Via SSH (Recommended)

If you have SSH access to Afrihost:

#### 1. SSH into Your Server

```bash
ssh snowsxtp@snowspoiledgifts.co.za
```

Or use the SSH access provided by Afrihost (check cPanel for details).

#### 2. Navigate to Your Application

```bash
cd /home/snowsxtp/ssg
```

#### 3. Initialize Git Repository

```bash
git init
```

#### 4. Add GitHub as Remote

```bash
git remote add origin https://github.com/mariuserasmus/snowspoiledgifts.git
```

#### 5. Configure Git User

```bash
git config user.name "Marius Erasmus"
git config user.email "mariuserasmus69@gmail.com"
```

#### 6. Create SSH Key for GitHub (Optional but Recommended)

This avoids entering passwords/tokens every time:

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "mariuserasmus69@gmail.com"

# Press Enter to accept default location
# Press Enter twice to skip passphrase (or set one)

# Display your public key
cat ~/.ssh/id_ed25519.pub
```

**Copy the entire output** (starts with `ssh-ed25519 AAAA...`)

**Add to GitHub:**
1. Go to: https://github.com/settings/keys
2. Click "New SSH key"
3. Title: `Afrihost Server - Snow's Spoiled Gifts`
4. Key: Paste the public key
5. Click "Add SSH key"

**Update remote to use SSH:**
```bash
git remote set-url origin git@github.com:mariuserasmus/snowspoiledgifts.git
```

#### 7. Pull Latest Code

```bash
git fetch origin
git checkout main
git pull origin main
```

**Important:** This will try to overwrite your server files. Make sure you have:
- Backed up your `.env` file
- Backed up your `database/` folder

**To avoid conflicts:**
```bash
# Backup .env and database
cp .env .env.backup
cp -r database database.backup

# Pull updates
git pull origin main

# Restore .env and database
cp .env.backup .env
rm -rf database
mv database.backup database

# Restart Passenger
touch tmp/restart.txt
```

---

### Option B: Via cPanel Git™ Version Control

If Afrihost cPanel has Git Version Control:

#### 1. Login to cPanel

#### 2. Find "Git™ Version Control" (under Files section)

#### 3. Click "Create"

**Settings:**
- **Clone URL:** `https://github.com/mariuserasmus/snowspoiledgifts.git`
- **Repository Path:** `/home/snowsxtp/ssg`
- **Repository Name:** `snowspoiledgifts`

**Authentication:**
- **Username:** `mariuserasmus`
- **Password:** Your GitHub Personal Access Token

#### 4. Click "Create"

cPanel will clone your repository.

#### 5. After Clone Completes:

**IMPORTANT:** Your `.env` file and `database/` won't be in Git (they're .gitignored).

You need to:
- Restore your `.env` file
- Restore your `database/` folder

---

## Part 3: Deploying Updates (Future Workflow)

### Workflow After Making Changes Locally:

#### 1. On Your Local Machine:

```bash
# Make your changes to code
# Then commit and push

git add .
git commit -m "Description of changes"
git push origin main
```

#### 2. On Afrihost Server (SSH):

```bash
cd /home/snowsxtp/ssg

# Backup critical files
cp .env .env.backup
cp -r database database.backup

# Pull latest changes
git pull origin main

# Restore critical files (if overwritten)
cp .env.backup .env
mv database.backup database

# Install any new dependencies
python3 -m pip install --user -r requirements.txt

# Restart Passenger
touch tmp/restart.txt
```

#### 3. Via cPanel Git Version Control:

1. Go to "Git™ Version Control"
2. Find your repository
3. Click "Manage"
4. Click "Pull or Deploy" → "Update from Remote"
5. Restart Passenger in "Setup Python App"

---

## Part 4: Protecting Critical Files

### Create Deploy Script (Optional)

Create a deployment script on the server to make updates safer:

**File:** `/home/snowsxtp/ssg/deploy.sh`

```bash
#!/bin/bash

# Snow's Spoiled Gifts Deployment Script
echo "Starting deployment..."

# Backup critical files
echo "Backing up .env and database..."
cp .env .env.backup
cp -r database database.backup

# Pull latest code
echo "Pulling latest code from GitHub..."
git pull origin main

# Restore critical files
echo "Restoring .env and database..."
cp .env.backup .env
rm -rf database
mv database.backup database

# Install/update dependencies
echo "Installing Python dependencies..."
python3 -m pip install --user -r requirements.txt

# Restart Passenger
echo "Restarting application..."
mkdir -p tmp
touch tmp/restart.txt

echo "Deployment complete!"
echo "Visit: https://www.snowspoiledgifts.co.za"
```

**Make it executable:**
```bash
chmod +x /home/snowsxtp/ssg/deploy.sh
```

**Usage:**
```bash
cd /home/snowsxtp/ssg
./deploy.sh
```

---

## Part 5: Best Practices

### What to Commit to Git:
✅ All code files (.py, .html, .css, .js)
✅ Documentation (.md files)
✅ Configuration templates (.env.example)
✅ Requirements (requirements.txt)
✅ Static assets (images, fonts)

### What NOT to Commit:
❌ `.env` file (contains secrets)
❌ `database/` folder (contains production data)
❌ `venv/` folder (virtual environment)
❌ `__pycache__/` folders
❌ User uploaded files (in `static/uploads/`)

These are already in your `.gitignore` file!

---

## Part 6: Handling .env Updates

If you need to update `.env` on the server:

**Option 1: Edit directly via SSH**
```bash
nano /home/snowsxtp/ssg/.env
```

**Option 2: Edit via cPanel File Manager**
1. Navigate to `/home/snowsxtp/ssg/`
2. Right-click `.env` → Edit
3. Make changes
4. Save

**Option 3: Keep .env in Git (NOT RECOMMENDED for production)**
If you really need to version `.env`:
1. Remove `.env` from `.gitignore`
2. Use a **Private** GitHub repository only
3. **NEVER** make the repo public with `.env` in it!

---

## Part 7: Troubleshooting

### Error: "Permission denied (publickey)"
- You need to add SSH key to GitHub (see Step 6 in Option A)

### Error: "Authentication failed"
- GitHub password authentication is disabled
- Use Personal Access Token or SSH key

### Error: "Updates were rejected because the remote contains work"
```bash
# See what's different
git fetch origin
git diff main origin/main

# Force local to match remote (CAREFUL!)
git reset --hard origin/main
```

### Error: ".env file disappeared after pull"
- `.env` is gitignored (correct!)
- Restore from backup: `cp .env.backup .env`

---

## Summary

### Initial Setup:
1. ✅ Push to GitHub from local machine
2. ✅ Setup Git on Afrihost server
3. ✅ Configure authentication (SSH key or token)

### Daily Workflow:
1. Make changes locally
2. Commit and push to GitHub
3. Pull changes on server
4. Restart Passenger

### Safety:
- Always backup `.env` and `database/` before pulling
- Test locally before pushing
- Keep GitHub repo private

---

## Quick Reference Commands

**Local (Your Computer):**
```bash
git add .
git commit -m "Your changes"
git push origin main
```

**Server (Afrihost):**
```bash
cd /home/snowsxtp/ssg
git pull origin main
touch tmp/restart.txt
```

---

**You're now set up for easy deployments! 🚀**
