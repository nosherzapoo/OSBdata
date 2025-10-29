# GitHub Secrets Setup for NY Gaming Data Monitor

## Required GitHub Secrets

To enable email notifications, you need to configure the following secrets in your GitHub repository:

### 1. Go to Repository Settings
- Navigate to your GitHub repository
- Click on "Settings" tab
- Click on "Secrets and variables" → "Actions"

### 2. Add the following secrets:

#### Email Configuration
- **`EMAIL_USER`**: Your email address (e.g., `your-email@gmail.com`)
- **`EMAIL_PASS`**: Your email app password (see instructions below)
- **`SMTP_SERVER`**: SMTP server (default: `smtp.gmail.com`)
- **`SMTP_PORT`**: SMTP port (default: `587`)

## Email Setup Instructions

### For Gmail:
1. Enable 2-Factor Authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate a new app password for "Mail"
   - Use this password as `EMAIL_PASS`

### For Other Email Providers:
- **Outlook/Hotmail**: `smtp-mail.outlook.com`, port `587`
- **Yahoo**: `smtp.mail.yahoo.com`, port `587`
- **Custom SMTP**: Use your organization's SMTP settings

## Testing the Setup

After configuring the secrets, you can test the workflow by:

1. Going to the "Actions" tab in your repository
2. Clicking on "NY Gaming Data Monitor"
3. Clicking "Run workflow" to trigger manually

## Notification Email

The system will send notifications to: `nosher-ali.khan@bernsteinsg.com`

## Schedule Summary

- **Thursday**: Every 2 hours (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22)
- **Friday 4AM-Noon**: Every 15 minutes
- **Friday 1PM-11PM**: Every hour

## Data Storage

- Current data: `ny_gaming_data.csv`
- Archived data: `data_archive/YYYYMMDD_HHMMSS/`
- Change log: `data_changes.json`
