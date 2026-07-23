# 🏕️ Ontario Parks & Parks Canada Camping Availability Monitor

An automated tracker hosted on GitHub Actions that periodically monitors both **Ontario Parks** and **Parks Canada** reservation systems for roofed accommodations and camping openings for a party of 3.

---

## 🎯 Monitored Search Criteria

### 1. 🌲 Ontario Parks (`reservations.ontarioparks.ca`)
- **Accommodation Type:** Roofed Accommodations (`bookingCategoryId=2`)
- **Party Size:** 3 People
- **Target Regions:**
  - Southwest & Central Parks
  - Algonquin
  - Southeast Parks
- **Target Dates:** Aug 28 – Aug 30 (2 nights) & Aug 29 – Aug 31 (2 nights)

### 2. 🇨🇦 Parks Canada (`reservation.pc.gc.ca`)
- **Accommodation Type:** Parks Canada Accommodations (`bookingCategoryId=1`)
- **Party Size:** 3 People
- **Target Locations (Central Region):**
  - Georgian Bay Islands
  - Bruce Peninsula
  - Bethune Memorial House
  - Trent-Severn Waterway
- **Target Dates:** Aug 28 – Aug 30 (2 nights) & Aug 29 – Aug 31 (2 nights)

---

## 🚀 Setup Instructions for GitHub Repository

To run this tool automatically and receive email alerts, follow these steps:

### Configure GitHub Secrets for Email Notifications

Go to your repository on GitHub (`https://github.com/J7892/camping`) and navigate to:
**Settings** > **Secrets and variables** > **Actions** > **New repository secret**

Add the following secrets:

| Secret Name | Description | Example Value |
| :--- | :--- | :--- |
| `NOTIFICATION_EMAIL` | The email address where you want to receive alerts | `user@example.com` |
| `SMTP_USERNAME` | The sender email address (or SMTP username) | `your-email@gmail.com` |
| `SMTP_PASSWORD` | App-specific password or API key | `xxxx xxxx xxxx xxxx` |
| `SMTP_SERVER` | SMTP host (Default: `smtp.gmail.com`) | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (Default: `587` for TLS / `465` for SSL) | `587` |

---

## ⏰ Schedule & Automation

The GitHub Action (`.github/workflows/check_availability.yml`) is scheduled to run **every 3 hours during daytime hours (8:00 AM ET – 10:00 PM ET)**.

### Manual Trigger
You can also run the checker manually at any time:
1. Go to the **Actions** tab on GitHub.
2. Select **Ontario Parks Availability Checker** on the left.
3. Click **Run workflow** > **Run workflow**.

---

## 💻 Local Testing

To test the checker locally on your computer:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Set environment variables (optional, for email delivery)
export NOTIFICATION_EMAIL="your-email@example.com"
export SMTP_USERNAME="your-email@gmail.com"
export SMTP_PASSWORD="your-app-password"

# 3. Run the script
python check_camping.py
```
