import smtplib
from email.message import EmailMessage
from datetime import datetime

def send_otp_email(email, otp):
    try:
        # Prepare the OTP email
        msg = EmailMessage()
        msg.set_content(f"Your OTP for email verification is: {otp}")
        msg["Subject"] = "Your OTP Verification Code"
        msg["From"] = "sayalarohith947@gmail.com"
        msg["To"] = email

        # Set up Gmail SMTP
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("sayalarohith947@gmail.com", "kvrn sfla pzrb rtak")  # App password
        server.send_message(msg)
        server.quit()

        print(f"[INFO] OTP sent to {email}")
        return True

    except Exception as e:
        print(f"[ERROR] Sending OTP failed: {e}")
        return False

def send_success_email(email):
    try:
        msg = EmailMessage()
        msg.set_content("🎉 Congrats! Your mail has been successfully verified.")
        msg["Subject"] = "Verification Successful"
        msg["From"] = "sayalarohith947@gmail.com"
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("sayalarohith947@gmail.com", "kvrn sfla pzrb rtak")  # App password
        server.send_message(msg)
        server.quit()

        print(f"[INFO] Success email sent to {email}")
        return True

    except Exception as e:
        print(f"[ERROR] Sending success message failed: {e}")
        return False

def save_verified_email(email, db_connection):
    try:
        cursor = db_connection.cursor()
        # Create table if it doesn't exist
        cursor.execute("""
             CREATE TABLE IF NOT EXISTS VERIFICATION (
                id INT AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(255) NOT NULL UNIQUE,
                status VARCHAR(100),
                timestamp DATETIME
            )
        """)
        # Insert verification record
        cursor.execute(
            "INSERT INTO VERIFICATION (email, status, timestamp) VALUES (%s, %s, %s)",
            (email, "Verified", datetime.now())
        )
        db_connection.commit()
        print(f"[INFO] Saved verified email to DB: {email}")

    except Exception as e:
        print(f"[ERROR] Database error: {e}")
