
import os
import smtplib
import time
from datetime import datetime 
from datetime import time as dtime
import subprocess
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email Configuration
GMAIL_USER = 'cartalkcanada@gmail.com'
GMAIL_PASSWORD = 'ohrr qftd ziep kzqg'
TO_EMAIL = 'cartalkcanada@gmail.com'

# IP addresses to ping
IPs = [ "10.0.70.40",  "10.0.70.50",   "10.0.70.80",   "10.0.70.90", "10.0.70.100", "10.0.70.140", "10.0.70.150", "10.0.70.120"]

# Function to ping IP address
def ping_ip(ip):
    response = subprocess.run(['ping', '-c', '1', ip], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return response.returncode == 0

# Function to send an email
def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(GMAIL_USER, GMAIL_PASSWORD)
            text = msg.as_string()
            server.sendmail(GMAIL_USER, TO_EMAIL, text)
    except Exception as e:
        print(f"Failed to send email: {str(e)}")


def is_within_daytime(check_time=None):
    # Use current time if none provided
    if check_time is None:
        check_time = datetime.now().time()
    
    start = dtime(8, 0)   # 8:00 AM
    end = dtime(19, 0)    # 7:00 PM
    
    return start <= check_time <= end


# Main logic to ping every hour and send 1 email if there are failures
def monitor_ips():
    while True:
        failed_ips = []
        for ip in IPs:
            if not ping_ip(ip):
                failed_ips.append(ip)
        if failed_ips and is_within_daytime():
            # Only send 1 email if there are failures
            subject = "Ping Failed for One or More IPs"
            body = f"The following IP(s) did not respond to ping:\n" + "\n".join(failed_ips)
            print(f"Sending email for failed IP(s): {', '.join(failed_ips)}")
            print(body)
            send_email(subject, body)
    

        # Wait for an hour before the next check
        time.sleep(3600)
        

# Run the script
if __name__ == "__main__":
    monitor_ips()

