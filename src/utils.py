from utils_email import MicrosoftGraphClient
import os
from datetime import datetime, timedelta



class Newsletter:
    def __init__(self, logs):
        self.logs = logs
        self.today = datetime.now().strftime("%Y-%m-%d")
        self.content = ""
        self.to_recipients = os.getenv("EMAILS_TARGET")
        self.subject = os.getenv("EMAIL_SUBJECT") + " - " + self.today
        self.list_emails_id_prossessed = []


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
        

    def fetch_emails(self, client, folder_scanned:str)->str:
        prefix = f'[{self.__class__.__name__} | fetch_emails]'

        try:
            self.logs.logging_msg(f"{prefix} START")
            client.read_mail_folder(client.folder_id_by_name(folder_scanned))

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'ERROR')
            return e
        

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
                    self.list_emails_id_prossessed.append(email.id)
            
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

            if os.getenv('DEBUG') != '0':
                self.logs.logging_msg(f"{prefix} >>>DEBUG MODE<<<: target folder: '{archive_folder}' > '" + os.getenv('ARCHIVE_FOLDER_TEST') + "'")
                archive_folder = os.getenv('ARCHIVE_FOLDER_TEST')
            
            for email_id in self.list_emails_id_prossessed:
                if client.move_email(email_id, client.folder_id_by_name(archive_folder)):
                    self.logs.logging_msg(f"{prefix} Email {email_id} moved to {archive_folder}", 'DEBUG')
                else:
                    self.logs.logging_msg(f"{prefix} Email {email_id} not moved to {archive_folder}", 'WARNING')

            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        

    def delete_old_emails(self, client, archive_folder:str, emails_retention_days:str)->str:
        prefix = f'[{self.__class__.__name__} | move_emails]'

        try:
            self.logs.logging_msg(f"{prefix} START")

            if os.getenv('DEBUG') == '0':
                deleting = True
            else:
                deleting = False
                self.logs.logging_msg(f"{prefix} >>>DEBUG MODE<<<: Emails not deleted but logged")
            
            client.read_mail_folder(client.folder_id_by_name(archive_folder))
            
            for email in client.emails:
                if self.is_date_expired(email.receivedDateTime, int(emails_retention_days)):
                    if deleting:
                        if client.delete_email(email.id):
                            self.logs.logging_msg(f"{prefix} Email '{email.subject}' deleted", 'DEBUG')
                        else:
                            self.logs.logging_msg(f"{prefix} Email '{email.subject}' not deleted", 'WARNING')
                    else:
                        self.logs.logging_msg(f"{prefix} Email [{email.receivedDateTime}] '{email.subject}' would be deleted", 'DEBUG')

            return None
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return e
        

    def is_date_expired(self, date_str: str, days_threshold: int) -> bool:
        prefix = f'[{self.__class__.__name__} | is_date_expired]'

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
            threshold_date = datetime.utcnow() - timedelta(days=days_threshold)

            return date_obj < threshold_date
        
        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')
            return False