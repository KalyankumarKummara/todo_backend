import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jinja2 import Template
from dotenv import load_dotenv
import os
load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def send_reminder_email(to_email, username, title, description, priority, due_date):
    with open("utils/templates/reminder_template.html.j2", "r", encoding="utf-8") as f:
        html_template = f.read()

    priority_colors = {"high": "red", "medium": "orange", "low": "green"}
    priority_color = priority_colors.get(priority.lower(), "black")

    template = Template(html_template)
    html_content = template.render(
        username=username,
        title=title,
        description=description or "No description provided",
        priority=priority,
        priority_color=priority_color,
        due_date=due_date if due_date else "Not set"
    )

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = f"Reminder: {title}"

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())

def send_email(to_email: str, subject: str, template_path: str, context: dict):
    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    template = Template(html_template)
    html_content = template.render(**context)

    msg = MIMEMultipart("alternative")
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, to_email, msg.as_string())
