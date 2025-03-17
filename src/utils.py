from utils_email import MicrosoftGraphClient
import os
import datetime


class Newsletter:
    def __init__(self, logs):
        self.logs = logs
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.content = self.head_body(today)
        self.to_recipients = os.getenv("EMAILS_TARGET")
        self.subject = os.getenv("EMAIL_SUBJECT") + " - " + today


    def connection(self)->str:
        prefix = f'[{self.__class__.__name__} | connection]'

        try:
            self.logs.logging_msg(f"{prefix} Connection")

            client = MicrosoftGraphClient()
            me = client.make_graph_request("/me")
            
            if "error" in me:
                self.logs.logging_msg(f"{prefix} Direct Authentication failed", 'WARNING')
                del client
                client = MicrosoftGraphClient("refresh_token")
                me = client.make_graph_request("/me")
                
                if "error" in me:
                    self.logs.logging_msg(f"{prefix} Refresh Authentication failed", 'ERROR')
                    raise "Authentication failed"

            return client, None
        
        except Exception as e:
            return None, e
        

    def head_body(self, today: str)->str:
        prefix = f'[{self.__class__.__name__} | head_body]'

        try:
            self.logs.logging_msg(f"{prefix} Head body", 'DEBUG')
            return f"""
<html>
    <body>
        <H1>Newsletter du {today}</H1>
        """
    
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        

    def foot_body(self)->str:
        prefix = f'[{self.__class__.__name__} | foot_body]'

        try:
            self.logs.logging_msg(f"{prefix} Foot body", 'DEBUG')
            self.content += """
    </body>
</html>
        """

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
    

    def create_email_body(self, emails)->str:
        prefix = f'[{self.__class__.__name__} | create_email_body]'

        try:
            self.logs.logging_msg(f"{prefix} Create email body")

            for mail in emails:
                self.add_content(mail.to_html())
            
            self.foot_body()
            
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
    

    def add_content(self, content: str)->str:
        prefix = f'[{self.__class__.__name__} | add_content]'

        try:
            self.content += content
            self.logs.logging_msg(f"{prefix} Content added", 'DEBUG')
            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        
    
    def send_email(self, client)->str:
        prefix = f'[{self.__class__.__name__} | send_email]'

        try:
            self.logs.logging_msg(f"{prefix} Send email")

            print(">>>>>")
            print(self.to_recipients)
            if client.send_email(self.subject, self.content, self.to_recipients):
                return None
            else:
                raise "Email not sent"

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e