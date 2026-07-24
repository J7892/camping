import os
import sys
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==========================================
# 1. ONTARIO PARKS CONFIGURATION
# ==========================================
ONTARIO_PARKS_API_URL = "https://reservations.ontarioparks.ca/api/availability/map"
ONTARIO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://reservations.ontarioparks.ca/create-booking/results"
}

ONTARIO_TARGET_REGIONS = {
    -2147483461: "Southwest & Central Parks",
    -2147483460: "Algonquin",
    -2147483459: "Southeast Parks"
}

ONTARIO_ALL_REGIONS = {
    -2147483463: "Northern Parks",
    -2147483462: "Near North Parks",
    -2147483461: "Southwest & Central Parks",
    -2147483460: "Algonquin",
    -2147483459: "Southeast Parks"
}

ONTARIO_DATE_RANGES = [
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

# ==========================================
# 2. PARKS CANADA CONFIGURATION
# ==========================================
PARKS_CANADA_API_URL = "https://reservation.pc.gc.ca/api/availability/map"
PARKS_CANADA_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://reservation.pc.gc.ca/create-booking/results"
}

PARKS_CANADA_TARGET_LOCATIONS = {
    -2147483511: "Georgian Bay Islands",
    -2147483584: "Bruce Peninsula",
    -2147483057: "Bethune Memorial House",
    -2147483204: "Trent-Severn Waterway"
}

PARKS_CANADA_DATE_RANGES = [
    {
        "label": "Aug 28 – Aug 30 (2 nights)",
        "startDate": "2026-08-28",
        "endDate": "2026-08-30",
        "url": "https://reservation.pc.gc.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483573&searchTabGroupId=2&bookingCategoryId=1&startDate=2026-08-28&endDate=2026-08-30&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32767,null,3,null%5D%5D&view=list"
    },
    {
        "label": "Aug 29 – Aug 31 (2 nights)",
        "startDate": "2026-08-29",
        "endDate": "2026-08-31",
        "url": "https://reservation.pc.gc.ca/create-booking/results?transactionLocationId=NULL&resourceLocationId=NULL&mapId=-2147483573&searchTabGroupId=2&bookingCategoryId=1&startDate=2026-08-29&endDate=2026-08-31&nights=2&isReserving=true&peopleCapacityCategoryCounts=%5B%5B-32767,null,3,null%5D%5D&view=list"
    }
]

# Camis Status Code Mapping for UI Labels:
# 6: No Availability for Selected Booking Category
# 7: Partially Available
# 8: Available
# 1 / 0: Closed / Not Available
def get_status_text(status_codes):
    if not status_codes:
        return "Unknown"
    if 8 in status_codes:
        return "Available"
    elif 7 in status_codes:
        return "Partially Available"
    elif all(code == 6 for code in status_codes):
        return "No Availability"
    elif all(code in (0, 1) for code in status_codes):
        return "Not Available / Closed"
    else:
        return f"Status {status_codes}"

def check_ontario_parks():
    findings = []
    print("\n==========================================")
    print("🌲 CHECKING ONTARIO PARKS RESERVATION SYSTEM")
    print("==========================================")

    for date_range in ONTARIO_DATE_RANGES:
        start_date = date_range["startDate"]
        end_date = date_range["endDate"]
        label = date_range["label"]
        booking_url = date_range["url"]

        print(f"\n--- Dates: {label} ({start_date} to {end_date}) ---")

        params = {
            "mapId": -2147483464,
            "bookingCategoryId": 2,  # Roofed accommodations
            "startDate": start_date,
            "endDate": end_date,
            "isReserving": "true"
        }

        try:
            response = requests.get(ONTARIO_PARKS_API_URL, headers=ONTARIO_HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            map_availabilities = data.get("mapLinkAvailabilities", {})

            for region_id, status_list in map_availabilities.items():
                reg_id_int = int(region_id)
                region_name = ONTARIO_ALL_REGIONS.get(reg_id_int, f"Region {region_id}")
                is_target = reg_id_int in ONTARIO_TARGET_REGIONS
                status_text = get_status_text(status_list)

                target_mark = "[MONITORED]" if is_target else "           "
                print(f"  {target_mark} {region_name:30s}: {status_text} (raw: {status_list})")

                # Target region & has availability (status 8)
                if is_target and 8 in status_list:
                    findings.append({
                        "system": "Ontario Parks",
                        "date_label": label,
                        "start_date": start_date,
                        "end_date": end_date,
                        "location_name": region_name,
                        "status_text": status_text,
                        "raw_status": status_list,
                        "booking_url": booking_url
                    })

        except Exception as e:
            print(f"Error fetching Ontario Parks data for {label}: {e}")

    return findings

def check_parks_canada():
    findings = []
    print("\n==========================================")
    print("🇨🇦 CHECKING PARKS CANADA RESERVATION SYSTEM")
    print("==========================================")

    for date_range in PARKS_CANADA_DATE_RANGES:
        start_date = date_range["startDate"]
        end_date = date_range["endDate"]
        label = date_range["label"]
        booking_url = date_range["url"]

        print(f"\n--- Dates: {label} ({start_date} to {end_date}) ---")

        params = {
            "mapId": -2147483573,  # Central Region
            "bookingCategoryId": 1,  # Parks Canada Accommodations
            "startDate": start_date,
            "endDate": end_date,
            "isReserving": "true"
        }

        try:
            response = requests.get(PARKS_CANADA_API_URL, headers=PARKS_CANADA_HEADERS, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            map_availabilities = data.get("mapLinkAvailabilities", {})

            for map_id, status_list in map_availabilities.items():
                map_id_int = int(map_id)
                if map_id_int in PARKS_CANADA_TARGET_LOCATIONS:
                    loc_name = PARKS_CANADA_TARGET_LOCATIONS[map_id_int]
                    status_text = get_status_text(status_list)

                    print(f"  [MONITORED] {loc_name:30s}: {status_text} (raw: {status_list})")

                    if 8 in status_list:
                        findings.append({
                            "system": "Parks Canada",
                            "date_label": label,
                            "start_date": start_date,
                            "end_date": end_date,
                            "location_name": loc_name,
                            "status_text": status_text,
                            "raw_status": status_list,
                            "booking_url": booking_url
                        })

        except Exception as e:
            print(f"Error fetching Parks Canada data for {label}: {e}")

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
    msg["Subject"] = "🏕️ Campsite Opening Alert: Ontario Parks / Parks Canada!"
    msg["From"] = smtp_username
    msg["To"] = recipient_email

    # Plain text body
    text_lines = ["Great news! Accommodation openings have been detected in your monitored locations:\n"]
    for f in findings:
        text_lines.append(f"• [{f['system']}] {f['location_name']} ({f['date_label']})")
        text_lines.append(f"  Status: {f['status_text']}")
        text_lines.append(f"  Book here: {f['booking_url']}\n")
    text_lines.append("Act fast before the spot gets reserved!")
    text_body = "\n".join(text_lines)

    # HTML body
    html_items = ""
    for f in findings:
        badge_color = "#2e7d32" if f["system"] == "Ontario Parks" else "#0288d1"
        html_items += f"""
        <div style="margin-bottom: 20px; padding: 15px; border-left: 4px solid {badge_color}; background-color: #f9f9f9; border-radius: 4px;">
            <div style="margin-bottom: 6px;">
                <span style="background-color: {badge_color}; color: white; padding: 3px 8px; border-radius: 3px; font-size: 0.8em; font-weight: bold;">{f['system']}</span>
            </div>
            <h3 style="margin: 4px 0 8px 0; color: #222;">📍 {f['location_name']}</h3>
            <p style="margin: 4px 0;"><strong>Dates:</strong> {f['date_label']}</p>
            <p style="margin: 4px 0;"><strong>Status:</strong> <span style="color: #2e7d32; font-weight: bold;">{f['status_text']}</span></p>
            <p style="margin: 12px 0 0 0;">
                <a href="{f['booking_url']}" style="background-color: {badge_color}; color: white; padding: 8px 16px; text-decoration: none; border-radius: 4px; display: inline-block;">Book Now on {f['system']}</a>
            </p>
        </div>
        """

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333; line-height: 1.6;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e0e0e0; border-radius: 8px;">
            <h2 style="color: #2e7d32; border-bottom: 2px solid #2e7d32; padding-bottom: 10px;">🏕️ Camping Reservation Alert</h2>
            <p>New accommodation availability has been detected for your requested dates!</p>
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
    ontario_findings = check_ontario_parks()
    parks_canada_findings = check_parks_canada()
    all_findings = ontario_findings + parks_canada_findings

    print("\n==========================================")
    print(f"TOTAL FINDINGS: {len(all_findings)} OPENING(S) FOUND")
    print("==========================================")

    if all_findings:
        send_email_alert(all_findings)
    else:
        print("No open spots currently available for any monitored regions/locations.")

if __name__ == "__main__":
    main()
