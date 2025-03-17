import os
import datetime


class Newsletter:
    def __init__(self):
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.content = f"<H1>Newsletter du {today}</H1>"
        self.emails = os.getenv("EMAILS_TARGET")
        self.subject = os.getenv("EMAIL_SUBJECT") + " - " + today
    

    def add_content(self, content: str)->str:
        try:
            self.content += content
            return None
        except Exception as e:
            return e