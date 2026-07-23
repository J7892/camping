# 🏕️ Ontario Parks Camping Availability Monitor

An automated tracker hosted on GitHub Actions that periodically monitors Ontario Parks' reservation system for **roofed accommodation** openings for a party of 3.

## 🎯 Target Search Criteria

- **Accommodation Type:** Roofed Accommodations (`bookingCategoryId=2`)
- **Party Size:** 3 People
- **Target Regions:**
  - Southwest & Central Parks
  - Algonquin
  - Southeast Parks
- **Target Dates:**
  - **Option 1:** August 28 – August 30 (2 nights)
  - **Option 2:** August 29 – August 31 (2 nights)

---

## 🚀 Setup Instructions for GitHub Repository

To run this tool automatically and receive email alerts, follow these steps:

### 1. Configure GitHub Secrets for Email Notifications

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

> 💡 **Tip for Gmail users:**
> Generate an **App Password** under your Google Account security settings (*Google Account > Security > 2-Step Verification > App passwords*) and use it as `SMTP_PASSWORD`.

---

## ⏰ Schedule & Automation

The GitHub Action (`.github/workflows/check_availability.yml`) is scheduled to run automatically every **6 hours**.

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

---

## 🔗 Direct Search Links

- [Aug 28 – Aug 30 Prefilled Search](https://reservations.ontarioparks.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483464&searchTabGroupId=2&bookingCategoryId=2&startDate=2026-08-28&endDate=2026-08-30&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32768,null,3,null%5D%5D&view=list)
- [Aug 29 – Aug 31 Prefilled Search](https://reservations.ontarioparks.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483464&searchTabGroupId=2&bookingCategoryId=2&startDate=2026-08-29&endDate=2026-08-31&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32768,null,3,null%5D%5D&view=list)
