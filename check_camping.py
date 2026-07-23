import os
import sys
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Configuration
ONTARIO_PARKS_API_URL = "https://reservations.ontarioparks.ca/api/availability/map"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://reservations.ontarioparks.ca/create-booking/results"
}

# Regions of interest mapping (Map ID -> Display Name)
TARGET_REGIONS = {
    -2147483461: "Southwest & Central Parks",
    -2147483460: "Algonquin",
    -2147483459: "Southeast Parks"
}

ALL_REGIONS = {
    -2147483463: "Northern Parks",
    -2147483462: "Near North Parks",
    -2147483461: "Southwest & Central Parks",
    -2147483460: "Algonquin",
    -2147483459: "Southeast Parks"
}

DATE_RANGES = [
    {
        "label": "Aug 28 – Aug 30 (2 nights)",
        "startDate": "2026-08-28",
        "endDate": "2026-08-30",
        "url": "https://reservations.ontarioparks.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483464&searchTabGroupId=2&bookingCategoryId=2&startDate=2026-08-28&endDate=2026-08-30&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32768,null,3,null%5D%5D&view=list"
    },
    {
        "label": "Aug 29 – Aug 31 (2 nights)",
        "startDate": "2026-08-29",
        "endDate": "2026-08-31",
        "url": "https://reservations.ontarioparks.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483464&searchTabGroupId=2&bookingCategoryId=2&startDate=2026-08-29&endDate=2026-08-31&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32768,null,3,null%5D%5D&view=list"
    }
]

# Camis Availability Status Code Mapping:
# 6: No Availability
# 7 or others: Available / Partially Available
def get_status_text(status_codes):
    if not status_codes:
        return "Unknown"
    # If any code in the status list is not 6, there is availability or partial availability
    if any(code in (7, 8, 4, 5) for code in status_codes):
        return "Available / Partially Available"
    elif all(code == 6 for code in status_codes):
        return "No Availability"
    else:
        return f"Status {status_codes}"

def check_availability():
    findings = []
    print("Checking Ontario Parks reservation system for roofed accommodations...")

    for date_range in DATE_RANGES:
        start_date = date_range["startDate"]
        end_date = date_range["endDate"]
        label = date_range["label"]
        booking_url = date_range["url"]

        print(f"\n--- Checking Date Range: {label} ({start_date} to {end_date}) ---")

        params = {
            "mapId": -2147483464,
            "bookingCategoryId": 2,  # Roofed accommodations
            "startDate": start_date,
            "endDate": end_date,
            "isReserving": "true"
        }

        try:
            response = requests.get(ONTARIO_PARKS_API_URL, headers=HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            map_availabilities = data.get("mapLinkAvailabilities", {})

            for region_id, status_list in map_availabilities.items():
                reg_id_int = int(region_id)
                region_name = ALL_REGIONS.get(reg_id_int, f"Region {region_id}")
                is_target = reg_id_int in TARGET_REGIONS
                status_text = get_status_text(status_list)

                target_mark = "[MONITORED]" if is_target else "           "
                print(f"  {target_mark} {region_name:30s}: {status_text} (raw: {status_list})")

                # If this is one of our target regions AND it is available (status not 6)
                if is_target and any(code != 6 for code in status_list):
                    findings.append({
                        "date_label": label,
                        "start_date": start_date,
                        "end_date": end_date,
                        "region_name": region_name,
                        "status_text": status_text,
                        "raw_status": status_list,
                        "booking_url": booking_url
                    })

        except Exception as e:
            print(f"Error fetching data for {label}: {e}")

    return findings

def send_email_alert(findings):
    smtp_server = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", 587))
    smtp_username = os.environ.get("SMTP_USERNAME")
    smtp_password = os.environ.get("SMTP_PASSWORD")
    recipient_email = os.environ.get("NOTIFICATION_EMAIL")

    if not smtp_username or not smtp_password or not recipient_email:
        print("\n[WARNING] Email credentials not fully configured in environment variables.")
        print("Skipping email dispatch. Set SMTP_USERNAME, SMTP_PASSWORD, and NOTIFICATION_EMAIL to enable alerts.")
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "🏕️ Ontario Parks Alert: Campsite Opening Found!"
    msg["From"] = smtp_username
    msg["To"] = recipient_email

    # Build text body
    text_lines = ["Great news! Roofed accommodations are currently AVAILABLE in your monitored regions:\n"]
    for f in findings:
        text_lines.append(f"• {f['region_name']} ({f['date_label']})")
        text_lines.append(f"  Status: {f['status_text']}")
        text_lines.append(f"  Book here: {f['booking_url']}\n")
    text_lines.append("Act fast before the spot gets reserved!")
    text_body = "\n".join(text_lines)

    # Build HTML body
    html_items = ""
    for f in findings:
        html_items += f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid #2e7d32; background-color: #f1f8e9; border-radius: 4px;">
            <h3 style="margin: 0 0 8px 0; color: #1b5e20;">📍 {f['region_name']}</h3>
            <p style="margin: 4px 0;"><strong>Dates:</strong> {f['date_label']}</p>
            <p style="margin: 4px 0;"><strong>Status:</strong> <span style="color: #2e7d32; font-weight: bold;">{f['status_text']}</span></p>
            <p style="margin: 12px 0 0 0;">
                <a href="{f['booking_url']}" style="background-color: #2e7d32; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">Book Now on Ontario Parks</a>
            </p>
        </div>
        """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #1b5e20; border-bottom: 2px solid #2e7d32; padding-bottom: 10px;">🏕️ Ontario Parks Reservation Alert</h2>
            <p>Roofed accommodation availability has been detected for your requested dates!</p>
            {html_items}
            <p style="font-size: 0.9em; color: #666;">This alert was automatically generated by your GitHub Actions camping tracker.</p>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(text_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    try:
        print(f"\nSending email notification to {recipient_email} via {smtp_server}:{smtp_port}...")
        if smtp_port == 465:
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_username, smtp_password)
                server.send_message(msg)
        print("Email sent successfully!")
        return True
    except Exception as e:
        print(f"Failed to send email alert: {e}")
        return False

def main():
    findings = check_availability()
    if findings:
        print(f"\n🎉 FOUND {len(findings)} MATCHING OPENING(S)!")
        send_email_alert(findings)
    else:
        print("\nNo open spots currently available for the monitored regions.")

if __name__ == "__main__":
    main()
