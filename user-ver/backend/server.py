from http.server import BaseHTTPRequestHandler, HTTPServer
import urllib.parse
import os
import random

from send_mail import send_otp_email, send_success_email, save_verified_email
import db_config

otp_store = {}  # email -> otp

class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.path = '/index.html'
        elif self.path.startswith('/verify'):
            self.path = '/verify.html'

        try:
            if self.path.endswith(".html") or self.path.endswith(".css"):
                filepath = os.path.join('../frontend', self.path.lstrip('/'))
                with open(filepath, 'rb') as file:
                    content = file.read()

                self.send_response(200)
                if self.path.endswith(".css"):
                    self.send_header("Content-type", "text/css")
                else:
                    self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(content)
            else:
                self.send_error(404, "File Not Found")
        except Exception as e:
            self.send_error(500, str(e))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode()
        data = urllib.parse.parse_qs(post_data)

        if self.path == '/send-otp':
            email = data.get('email', [None])[0]
            if email:
                otp = str(random.randint(100000, 999999))
                otp_store[email] = otp
                print(f"[DEBUG] Generated OTP for {email}: {otp}")
                if send_otp_email(email, otp):
                    self.redirect_to_verify(email)
                else:
                    self.respond_html("<h3 style='color:red;'>Failed to send OTP email.</h3>")
            else:
                self.send_error(400, "No email provided.")

        elif self.path == '/verify-otp':
            email = data.get('email', [None])[0]
            entered_otp = data.get('otp', [None])[0]

            if email and entered_otp:
                expected_otp = otp_store.get(email)
                print(f"[DEBUG] Entered OTP: {entered_otp}, Expected OTP: {expected_otp}")
                if expected_otp and entered_otp.strip() == expected_otp.strip():
                    try:
                        conn = db_config.get_connection()
                        save_verified_email(email, conn)
                        send_success_email(email)
                        del otp_store[email]
                        message = f"<h3 style='color:green;'> Congrats! Your email {email} has been verified. A confirmation email has been sent.</h3>"
                    except Exception as db_err:
                        message = f"<h3 style='color:red;'> OTP verified, but failed to store in database: {db_err}</h3>"
                else:
                    message = "<h3 style='color:red;'>Incorrect OTP. Please try again.</h3>"
                self.respond_html(message)
            else:
                self.send_error(400, "Email or OTP missing.")

    def redirect_to_verify(self, email):
        self.send_response(302)
        self.send_header('Location', f'/verify?email={urllib.parse.quote(email)}')
        self.end_headers()

    def respond_html(self, content):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(content.encode())

# Start the server
if __name__ == "__main__":
    server_address = ('', 8000)
    print("Server started on http://localhost:8000")
    httpd = HTTPServer(server_address, SimpleHandler)
    httpd.serve_forever()
