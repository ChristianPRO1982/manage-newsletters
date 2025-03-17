from utils_email import MicrosoftGraphClient
import os
import datetime


class Newsletter:
    def __init__(self, logs):
        self.logs = logs
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.content = self.head_body(today)
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
        

    def head_body(self, today: str)->str:
        prefix = "[Newsletter.head_body]"

        try:
            self.logs.logging_msg(f"{prefix} Head body", 'DEBUG')
            return f"""
<html>
    <body>
        <H1>Newsletter du {today}</H1>
        """
    
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e
        

    def foot_body(self)->str:
        prefix = "[Newsletter.foot_body]"

        try:
            self.logs.logging_msg(f"{prefix} Foot body", 'DEBUG')
            self.content += """
    </body>
</html>
        """

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e
    

    def create_email_body(self, emails)->str:
        prefix = "[Newsletter.create_email_body]"

        try:
            self.logs.logging_msg(f"{prefix} Create email body", 'DEBUG')

            for mail in emails:
                self.add_content(mail.to_html())
            
            self.foot_body()
            
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e
    

    def add_content(self, content: str)->str:
        prefix = "[Newsletter.add_content]"

        try:
            self.content += content
            self.logs.logging_msg(f"{prefix} Content added", 'DEBUG')
            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e