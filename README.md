# NY State Gaming Data Tracker

Automated monitoring system for NY State Gaming weekly reports with change detection and email notifications.

## Features

- 🚀 **Automated Data Collection**: Downloads all 9 operator reports in parallel
- 📊 **Data Extraction**: Converts Excel files to structured CSV
- 🔍 **Change Detection**: Compares new data with previous data
- 📧 **Email Notifications**: Alerts when changes are detected
- ⏰ **Scheduled Monitoring**: Runs on custom schedule
- 📁 **Data Archiving**: Maintains historical data

## Schedule

- **Thursday**: Every 2 hours
- **Friday 4AM-Noon**: Every 15 minutes  
- **Friday 1PM-11PM**: Every hour

## Core Files

- `download_reports.py` - Downloads all Excel reports (async/parallel)
- `extract_to_csv_v2.py` - Extracts data to CSV
- `compare_data.py` - Compares data and sends notifications
- `.github/workflows/ny-gaming-monitor.yml` - GitHub Actions workflow

## Setup

1. **Configure GitHub Secrets** (see `setup_github_secrets.md`)
2. **Push to GitHub repository**
3. **Enable GitHub Actions**

## Data Structure

```csv
Date,Handle,GGR,Brand
2022-04-03,36879411,733061.16,BetMGM
2022-04-03,48873594,4254072.17,Caesars Sport Book
...
```

## Change Detection

- New weekly data
- Significant GGR changes (>20%)
- New/removed brands
- Record count changes

## Excel Report Generation

When changes are detected, the system automatically creates `ny_gaming_analysis.xlsx` with 5 workbooks:

1. **Handle** - Betting handle by brand and date
2. **GGR** - Gross Gaming Revenue by brand and date  
3. **Hold** - Hold percentage (GGR/Handle) by brand and date (formatted as %)
4. **Handle (YoY)** - Year-over-year handle change percentage (364 days, formatted as %)
5. **GGR (YoY)** - Year-over-year GGR change percentage (364 days, formatted as %)

**Note**: Blank cells indicate N/A values or calculation errors. Hold and YoY values are formatted as percentages in Excel.

Each workbook includes:
- **Date column** (most recent first)
- **Individual sportsbook columns** (9 brands)
- **Statewide column** (sum of all sportsbooks)

## Email Notifications

Notifications sent to: `nosher-ali.khan@bernsteinsg.com` with Excel attachment

## Local Testing

```bash
pip install -r requirements.txt
python download_reports.py
python extract_to_csv_v2.py
python compare_data.py
```
