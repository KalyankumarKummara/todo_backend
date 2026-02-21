import os
import resend
from jinja2 import Template
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.environ["RESEND_API_KEY"]

def _send_html_email(to_email: str, subject: str, html_content: str):
    resend.Emails.send({
        "from": "onboarding@resend.dev",   
        "to": [to_email],
        "subject": subject,
        "html": html_content
    })


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

    _send_html_email(to_email, f"Reminder: {title}", html_content)

def send_email(to_email: str, subject: str, template_path: str, context: dict):

    with open(template_path, "r", encoding="utf-8") as f:
        html_template = f.read()

    template = Template(html_template)
    html_content = template.render(**context)

    _send_html_email(to_email, subject, html_content)