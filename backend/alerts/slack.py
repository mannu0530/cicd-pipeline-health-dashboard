
import os, json, httpx

class SlackAlerter:
    def __init__(self):
        self.webhook = os.getenv("SLACK_WEBHOOK_URL")

    def notify(self, transition: dict):
        if not self.webhook:
            return
        text = f"[{transition.get('provider')}] {transition.get('pipeline')} -> {transition.get('status_new')} (was {transition.get('status_old')})"
        payload = {
            "text": text,
            "blocks": [
                {"type":"section","text":{"type":"mrkdwn","text":f"*Build Update*\n{text}"}},
                {"type":"context","elements":[{"type":"mrkdwn","text":transition.get("web_url","")}]}
            ]
        }
        try:
            with httpx.Client(timeout=10) as c:
                c.post(self.webhook, json=payload)
        except Exception as e:
            print("Slack alert failed:", e)
