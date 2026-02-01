# Keep PythonAnywhere Warm - Setup Guide

## What I Did

I added a health check endpoint to your Flask backend that monitoring services can ping to keep your server awake.

**File Changed:** `app/api/auth.py`
- Added `/api/health` endpoint (no authentication required)
- Returns: `{"status": "healthy", "timestamp": "...", "service": "KIA API"}`

---

## Step 1: Deploy Changes to PythonAnywhere

### Option A: Using Git (Recommended)

1. **Commit and push your changes** (from your local machine):
   ```bash
   cd /Users/ibrahim/Desktop/my\ projects/kia
   git add app/api/auth.py
   git commit -m "Add health check endpoint to keep server warm"
   git push
   ```

2. **SSH into PythonAnywhere** or use their web console:
   - Go to https://www.pythonanywhere.com
   - Click on "Consoles" tab
   - Open a Bash console

3. **Pull the changes**:
   ```bash
   cd ~/your-project-directory
   git pull origin main
   ```

4. **Reload your web app**:
   - Go to the "Web" tab in PythonAnywhere
   - Click the green "Reload" button for your app

### Option B: Manual Upload

1. Go to PythonAnywhere dashboard
2. Click "Files" tab
3. Navigate to `app/api/auth.py`
4. Edit the file and paste the new code
5. Go to "Web" tab and click "Reload"

---

## Step 2: Test the Health Check Endpoint

Once deployed, test it:

```bash
curl https://kiaacdemy.pythonanywhere.com/api/health
```

You should see:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-30T12:34:56.789123",
  "service": "KIA API"
}
```

Or test in your browser by visiting:
https://kiaacdemy.pythonanywhere.com/api/health

---

## Step 3: Set Up UptimeRobot (Free Monitoring)

### Create UptimeRobot Account

1. Go to https://uptimerobot.com
2. Click "Register" (free account)
3. Verify your email

### Add Your Monitor

1. **Log in to UptimeRobot**
2. Click **"+ Add New Monitor"**

3. **Fill in the form**:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** KIA Academy API
   - **URL:** `https://kiaacdemy.pythonanywhere.com/api/health`
   - **Monitoring Interval:** 5 minutes (free tier default)
   - **Monitor Timeout:** 30 seconds
   - **HTTP Method:** GET (default)

4. **Click "Create Monitor"**

### Configure Alerts (Optional)

1. Go to "My Settings" → "Alert Contacts"
2. Add your email to get notified if the server goes down
3. You can also add:
   - SMS alerts
   - Slack notifications
   - Discord webhooks

---

## Step 4: Alternative - Cron-job.org

If you prefer Cron-job.org instead:

1. Go to https://cron-job.org
2. Register for free account
3. Click "Create cronjob"
4. Fill in:
   - **Title:** KIA API Health Check
   - **URL:** `https://kiaacdemy.pythonanywhere.com/api/health`
   - **Schedule:** Every 5 minutes
5. Save

---

## How It Works

### The Problem
- PythonAnywhere free/basic tier puts apps to sleep after inactivity
- First request after sleep takes 10-30+ seconds (cold start)
- This causes your app's splash screen to hang

### The Solution
- UptimeRobot pings your `/api/health` endpoint every 5 minutes
- This keeps your app "warm" and active
- Users experience fast load times (1-2 seconds instead of 10-30)
- The health check endpoint is lightweight and doesn't use database

### Important Notes
- **Free tier limit:** UptimeRobot checks every 5 minutes minimum
- **PythonAnywhere rules:** Check their terms - keeping apps warm is generally allowed
- **Battery usage:** No impact on mobile app battery (pings happen on UptimeRobot's servers)
- **Cost:** Completely free for both services

---

## Verify It's Working

After 1-2 hours, check:

1. **UptimeRobot Dashboard:**
   - Should show "Up" status
   - Response time should be ~500-1000ms after warm

2. **Test your mobile app:**
   - Close and reopen the app several times
   - Splash screen should be fast (2-5 seconds max)

3. **Monitor logs:**
   - In PythonAnywhere, check "Web" → "Log files" → "Access log"
   - You should see GET requests to `/api/health` every 5 minutes

---

## Troubleshooting

### Health check returns 404
- Make sure you deployed the changes to PythonAnywhere
- Check that you reloaded the web app
- Verify the URL is correct: `/api/health` not `/health`

### UptimeRobot shows "Down"
- Check if your PythonAnywhere app is running
- Test the URL manually in a browser
- Check PythonAnywhere error logs

### App still slow sometimes
- UptimeRobot pings every 5 minutes
- If 6+ minutes pass without activity, app may sleep
- Consider reducing retry logic timeout in the mobile app
- Or upgrade to PythonAnywhere paid tier for better performance

---

## Cost Comparison

### Free Option (Current)
- PythonAnywhere: Free tier
- UptimeRobot: Free (50 monitors, 5-minute intervals)
- Total: **$0/month**

### Paid Option (Better Performance)
- PythonAnywhere Hacker: **$5/month**
  - No sleep
  - Better CPU
  - Faster response times
- Railway.app: **Free tier** or $5/month
- Render.com: **Free tier** or $7/month

---

## Next Steps

1. ✅ Deploy the health check endpoint
2. ✅ Test it works
3. ✅ Set up UptimeRobot
4. ✅ Wait 1 hour and test your mobile app
5. ✅ Check UptimeRobot dashboard

**Questions?** Let me know if you need help with any step!
