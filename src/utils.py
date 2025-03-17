from utils_email import MicrosoftGraphClient
import os
import datetime


class Newsletter:
    def __init__(self, logs):
        self.logs = logs
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.content = f"<H1>Newsletter du {today}</H1>"
        self.emails = os.getenv("EMAILS_TARGET")
        self.subject = os.getenv("EMAIL_SUBJECT") + " - " + today


    def connection(self)->str:
        prefix = "[Newsletter.connection]"
        try:
            self.logs.logging_msg(f"{Newsletter} Connection")
            client = MicrosoftGraphClient()
            me = client.make_graph_request("/me")
            if "error" in me:
                self.logs.logging_msg(f"{Newsletter} Direct Authentication failed", 'WARNING')
                del client
                client = MicrosoftGraphClient("refresh_token")
                me = client.make_graph_request("/me")
                if "error" in me:
                    self.logs.logging_msg(f"{Newsletter} Refresh Authentication failed", 'ERROR')
                    raise "Authentication failed"

            return client, None
        
        except Exception as e:
            return None, e
    

    def add_content(self, content: str)->str:
        try:
            self.content += content
            return None
        
        except Exception as e:
            return e