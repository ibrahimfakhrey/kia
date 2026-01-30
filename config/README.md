# Config Directory

This directory contains configuration files for the KIA backend.

## Firebase Credentials

**IMPORTANT:** You need to manually upload the Firebase service account credentials file to this directory.

### File Required:
- `firebase-credentials.json` - Firebase Admin SDK service account credentials

### How to Upload to PythonAnywhere:

1. Go to PythonAnywhere Dashboard
2. Navigate to "Files" tab
3. Go to your project directory: `/home/YOUR_USERNAME/kia/config/`
4. Click "Upload a file"
5. Upload the `firebase-credentials.json` file from your local machine

The file is located locally at:
`/Users/ibrahim/Desktop/my projects/kia/config/firebase-credentials.json`

### Security Note:
This file contains sensitive credentials and should NEVER be committed to git.
It's added to `.gitignore` for security.
