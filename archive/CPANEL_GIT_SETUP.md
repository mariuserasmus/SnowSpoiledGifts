# cPanel Git™ Version Control Setup Guide

## What is .cpanel.yml?

The `.cpanel.yml` file tells cPanel what to do when you deploy code from Git. It automatically:
- Installs Python dependencies
- Creates necessary folders
- Sets file permissions
- Restarts your application

---

## Step 1: Push .cpanel.yml to GitHub

First, commit and push the `.cpanel.yml` file:

```bash
git add .cpanel.yml
git commit -m "Add cPanel deployment configuration"
git push origin main
```

---

## Step 2: Setup Git in cPanel

### 1. Login to cPanel
- URL provided by Afrihost
- Username: `snowsxtp`

### 2. Find "Git™ Version Control"
- Look in the **Files** section
- Click on "Git™ Version Control"

### 3. Click "Create"

### 4. Fill in Repository Details:

**Repository Information:**
- **Clone URL:** `https://github.com/mariuserasmus/snowspoiledgifts.git`
- **Repository Path:** `/home/snowsxtp/ssg`
- **Repository Name:** `snowspoiledgifts`

**Credentials:**
- **Authentication Method:** HTTPS
- **Username:** `mariuserasmus`
- **Password/Token:** Your GitHub Personal Access Token (starts with `ghp_...`)

### 5. Click "Create"

cPanel will:
- Clone your repository
- Detect `.cpanel.yml`
- Ask if you want to enable deployment tasks
- **Click "Enable" when prompted!**

---

## Step 3: After Initial Clone

### Important: Restore Critical Files

The `.env` file and `database/` folder are NOT in Git (intentionally).

**Via cPanel File Manager:**

1. Navigate to `/home/snowsxtp/ssg/`
2. Create `.env` file:
   - Click "New File" → Name it `.env`
   - Right-click → Edit
   - Paste contents from `PRODUCTION_ENV_TEMPLATE.md`
   - Save
   - Right-click → Permissions → Set to `600`

3. Verify folders exist:
   - `database/` (should be created by .cpanel.yml)
   - `tmp/` (should be created by .cpanel.yml)
   - `static/uploads/` (should be created by .cpanel.yml)

---

## Step 4: Manual Deployment (First Time)

After Git clone, trigger the first deployment:

1. In "Git™ Version Control", click **"Manage"** next to your repo
2. Click **"Pull or Deploy"** tab
3. Click **"Update from Remote"**
4. Check **"Run deployment tasks"**
5. Click **"Update from Remote"**

You'll see the output of your `.cpanel.yml` tasks running!

---

## Step 5: Verify Deployment

Check that everything worked:

1. **Check if packages installed:**
   - Look for success messages in deployment log
   - Should see: "Successfully installed Flask..."

2. **Check folders created:**
   - Go to File Manager
   - Navigate to `/home/snowsxtp/ssg/`
   - Verify `database/`, `tmp/`, `static/uploads/` exist

3. **Check application restarted:**
   - Visit: https://www.snowspoiledgifts.co.za
   - Site should load

---

## Deploying Future Updates

### Workflow:

#### 1. On Your Local Machine:
```bash
# Make your code changes
# Then commit and push

git add .
git commit -m "Description of changes"
git push origin main
```

#### 2. In cPanel Git:
1. Go to "Git™ Version Control"
2. Click **"Manage"** on your repository
3. Click **"Pull or Deploy"** tab
4. Click **"Update from Remote"**
5. Ensure **"Run deployment tasks"** is checked ✅
6. Click **"Update from Remote"**

**That's it!** The `.cpanel.yml` file automatically:
- Installs new dependencies
- Creates any new folders needed
- Sets permissions
- Restarts Passenger

---

## What .cpanel.yml Does

Here's what happens when you deploy:

```yaml
deployment:
  tasks:
    # 1. Install Python packages from requirements.txt
    - /bin/python3 -m pip install --user -r requirements.txt

    # 2. Create necessary directories
    - /bin/mkdir -p database
    - /bin/mkdir -p tmp
    - /bin/mkdir -p static/uploads

    # 3. Set proper permissions
    - /bin/chmod 755 database
    - /bin/chmod 755 static/uploads
    - /bin/chmod 644 passenger_wsgi.py

    # 4. Restart application
    - /bin/touch tmp/restart.txt
```

---

## Protecting Your .env and Database

### .env File Protection

The `.env` file is **NOT** in Git and will **NOT** be overwritten during deployments.

**After initial clone, you must:**
1. Create `.env` manually (one time only)
2. It stays on the server forever
3. Git updates won't touch it

### Database Protection

The `database/` folder is **NOT** in Git.

**Your data is safe:**
- Git won't delete it
- Git won't overwrite it
- It persists across deployments

---

## Customizing .cpanel.yml

If you need to add more deployment tasks:

```yaml
deployment:
  tasks:
    # Existing tasks...

    # Add custom tasks here:
    - /bin/echo "Deployment complete!"

    # Run database migrations (if you add them later)
    # - /bin/python3 $DEPLOYPATH/migrate.py

    # Clear cache (if needed)
    # - /bin/rm -rf $DEPLOYPATH/__pycache__
```

Commit and push after editing:
```bash
git add .cpanel.yml
git commit -m "Update deployment tasks"
git push origin main
```

---

## Troubleshooting

### Error: "Deployment tasks failed"

**View the error:**
- In Git Manage screen, check the deployment log
- Look for specific error messages

**Common issues:**

1. **Python package installation failed**
   ```
   ERROR: Could not install packages...
   ```
   **Solution:** Check `requirements.txt` syntax, ensure all packages exist

2. **Permission denied**
   ```
   chmod: cannot access...
   ```
   **Solution:** Check file paths in `.cpanel.yml`, ensure files exist

3. **Command not found**
   ```
   /bin/python3: not found
   ```
   **Solution:** Verify Python path, may need to use full path like `/usr/bin/python3`

### Error: ".env file not found"

This is **normal** after first clone!

**Solution:** Create `.env` file manually (see Step 3 above)

### Error: "Database not found"

Also **normal** - database will be created on first run.

**Solution:**
1. Ensure `database/` folder exists (`.cpanel.yml` creates it)
2. Visit your site - Flask will auto-create the database file

---

## Advantages of cPanel Git

✅ **Easy Deployment** - Click button to update
✅ **Automatic Tasks** - `.cpanel.yml` runs tasks automatically
✅ **Version Control** - Roll back to previous versions easily
✅ **No SSH Needed** - Everything via cPanel interface
✅ **Deployment History** - See log of all deployments

---

## Deployment Checklist

Before deploying updates:

- [ ] Test changes locally
- [ ] Commit changes to Git
- [ ] Push to GitHub
- [ ] Go to cPanel Git
- [ ] Click "Update from Remote"
- [ ] Check deployment log for errors
- [ ] Test site: https://www.snowspoiledgifts.co.za
- [ ] Check admin panel works
- [ ] Verify database still intact

---

## Alternative: Manual SSH Deployment

If cPanel Git doesn't work well, you can still use SSH:

```bash
ssh snowsxtp@snowspoiledgifts.co.za
cd /home/snowsxtp/ssg
git pull origin main
python3 -m pip install --user -r requirements.txt
touch tmp/restart.txt
```

---

## Quick Reference

**Local:**
```bash
git add .
git commit -m "Changes"
git push origin main
```

**cPanel:**
1. Git™ Version Control
2. Manage → Pull or Deploy
3. Update from Remote ✅
4. Done!

---

**Your deployment workflow is now streamlined! 🚀**
