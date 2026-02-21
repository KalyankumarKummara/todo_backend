import os
import requests
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def _send_html_email(to_email: str, subject: str, html_content: str):
    try:
        url = "https://api.brevo.com/v3/smtp/email"

        headers = {
            "accept": "application/json",
            "api-key": BREVO_API_KEY,
            "content-type": "application/json"
        }

        data = {
            "sender": {
                "name": "Todo App",
                "email": "todoplatform@gmail.com"
            },
            "to": [{"email": to_email}],
            "subject": subject,
            "htmlContent": html_content
        }

        response = requests.post(url, headers=headers, json=data)
        print("Brevo response:", response.status_code, response.text)

    except Exception as e:
        print("Email sending failed:", str(e))


def send_email(to_email: str, subject: str, template_path: str, context: dict):
    try:
        with open(template_path, "r", encoding="utf-8") as f:
            html_template = f.read()

        template = Template(html_template)
        html_content = template.render(**context)

        _send_html_email(to_email, subject, html_content)

    except Exception as e:
        print("Template render failed:", str(e))


def send_reminder_email(to_email, username, title, description, priority, due_date):
    try:
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

        _send_html_email(to_email, f"Reminder: {title}", html_content)

    except Exception as e:
        print("Reminder email failed:", str(e))