# Network Access Troubleshooting Guide

## Current Status
- **Server IP:** 192.168.0.248
- **Port:** 5000
- **URL:** http://192.168.0.248:5000
- **Server Status:** ✅ Running and listening on 0.0.0.0:5000

## Issue: Can't Access from Mobile Device

### Step 1: Add Windows Firewall Rule (REQUIRED)

You need to run this command **as Administrator**:

1. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Run this command:**
   ```powershell
   netsh advfirewall firewall add rule name="Flask Snow Spoiled Gifts" dir=in action=allow protocol=TCP localport=5000
   ```

3. **Verify the rule was added:**
   ```powershell
   netsh advfirewall firewall show rule name="Flask Snow Spoiled Gifts"
   ```

### Step 2: Alternative - Use Windows Firewall GUI

If you prefer the GUI:

1. Press `Win + R`, type `wf.msc`, press Enter
2. Click "Inbound Rules" on the left
3. Click "New Rule..." on the right
4. Select "Port" → Next
5. Select "TCP" and enter "5000" in Specific local ports → Next
6. Select "Allow the connection" → Next
7. Check all boxes (Domain, Private, Public) → Next
8. Name it "Flask Snow Spoiled Gifts" → Finish

### Step 3: Verify Both Devices Are on Same Network

**On your PC:**
```bash
ipconfig
```
Look for your WiFi adapter's IPv4 address: `192.168.0.248`

**On your mobile:**
- Go to WiFi settings
- Check the IP address (should be 192.168.0.xxx)
- Make sure it's connected to the same WiFi network

### Step 4: Test Connectivity

**From your mobile:**
1. Open browser
2. Try: `http://192.168.0.248:5000`

**If still not working, try from PC first:**
1. Open browser on PC
2. Try: `http://192.168.0.248:5000`
3. If this works but mobile doesn't, it's definitely a firewall issue

### Step 5: Check if Server is Running

Make sure Flask is running and you see output like:
```
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://192.168.0.248:5000
```

**Key:** It must say `Running on all addresses (0.0.0.0)` - this confirms network access is enabled.

### Step 6: Restart Flask Server

Sometimes you need to restart after firewall changes:
1. Stop Flask (Ctrl+C in terminal)
2. Start again: `python app.py`

### Common Issues

#### Issue: "This site can't be reached" on mobile
**Solution:** Windows Firewall is blocking. Follow Step 1 or Step 2 above.

**⚠️ IMPORTANT - Check for Python Blocking Rules:**
Some systems have blanket blocking rules for `python.exe`. Check for these:

1. Open Windows Firewall: `Win + R` → `wf.msc`
2. Click "Inbound Rules"
3. Look for rules named exactly "python.exe" with Action: Block
4. If you find any, you have 2 options:
   - **Disable them** (quick fix - allows all Python network access)
   - **Delete them** (permanent fix)

**These blocking rules are often created by:**
- Antivirus software (overly cautious security)
- Corporate IT policies
- Windows Defender / Security software
- Previous user/admin manually blocking Python

**Note:** These rules block ALL Python network traffic, not just Flask. If you use other Python apps that need network access (API requests, web scraping, etc.), they'll also be blocked by these rules.

#### Issue: Works on PC but not mobile
**Solution:**
- Confirm both devices on same WiFi
- Add firewall rule (Step 1)

#### Issue: "Connection refused"
**Solution:** Flask server not running. Check Step 5.

#### Issue: Wrong network
**Solution:**
- Mobile might be on cellular data - switch to WiFi
- PC might be on Ethernet, mobile on different WiFi network

### Quick Checklist

- [ ] Flask server is running (`python app.py`)
- [ ] Server shows "Running on all addresses (0.0.0.0)"
- [ ] Windows Firewall rule added for port 5000
- [ ] PC IP is 192.168.0.248 (verify with `ipconfig`)
- [ ] Mobile is on same WiFi network
- [ ] Mobile browser tries: `http://192.168.0.248:5000`
- [ ] Can access from PC browser at `http://192.168.0.248:5000`

### Testing Order

1. ✅ Test from PC: `http://localhost:5000` (should work)
2. ✅ Test from PC: `http://192.168.0.248:5000` (should work)
3. ⚠️ Add firewall rule (Step 1 or Step 2)
4. ✅ Test from mobile: `http://192.168.0.248:5000` (should now work)

## After It's Working

Once you can access from mobile, you can test the entire site:
- Browse products
- Fill out quote request form
- Upload images
- Submit requests
- Check if email notifications arrive (if configured)

**Note:** This only works on your local network. To access from internet, you'd need:
- Port forwarding on router
- Dynamic DNS service
- Or deploy to cloud hosting
