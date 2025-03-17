from utils_email import MicrosoftGraphClient
import os
import datetime


class Newsletter:
    def __init__(self, logs):
        self.logs = logs
        self.today = datetime.datetime.now().strftime("%Y-%m-%d")
        self.content = ""
        self.to_recipients = os.getenv("EMAILS_TARGET")
        self.subject = os.getenv("EMAIL_SUBJECT") + " - " + self.today
        self.list_emails_prossessed = []


    def connection(self)->str:
        prefix = f'[{self.__class__.__name__} | connection]'

        try:
            self.logs.logging_msg(f"{prefix} START")

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
        

    def head_body(self, today: str, email_subject: str)->str:
        prefix = f'[{self.__class__.__name__} | head_body]'

        try:
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')
            return f"""
<html>
    <body>
        <H1>{email_subject} - {today}</H1>
        """
    
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        

    def foot_body(self)->str:
        prefix = f'[{self.__class__.__name__} | foot_body]'

        try:
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')
            self.content += """
    </body>
</html>
        """

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
    

    def create_email_body(self, emails, email_subject)->str:
        prefix = f'[{self.__class__.__name__} | create_email_body]'

        try:
            self.logs.logging_msg(f"{prefix} START")

            self.head_body(self.today, email_subject)

            for email in emails:
                if not self.add_content(email.to_html()):
                    self.list_emails_prossessed.append(email.id)
            
            self.foot_body()
            
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
    

    def add_content(self, content: str)->str:
        prefix = f'[{self.__class__.__name__} | add_content]'

        try:
            self.content += content
            self.logs.logging_msg(f"{prefix} start", 'DEBUG')
            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        
    
    def send_email(self, client)->str:
        prefix = f'[{self.__class__.__name__} | send_email]'

        try:
            self.logs.logging_msg(f"{prefix} START")
            if os.getenv('DEBUG') != '0':
                self.logs.logging_msg(f"{prefix} >>>DEBUG MODE<<<: Email not sent")
                return None

            if client.send_email(self.subject, self.content, self.to_recipients):
                return None
            else:
                raise "Email not sent"

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e
        

    def move_emails(self, client, archive_folder:str)->str:
        prefix = f'[{self.__class__.__name__} | move_emails]'

        try:
            self.logs.logging_msg(f"{prefix} START")

            # print(self.list_emails_prossessed)
            print('>>>',client.folder_id_by_name(archive_folder))

            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e