from imapclient import IMAPClient
import email
from email.policy import default


class OutlookEmailFetcher:
    def __init__(self, logs, server, email_account, password, folder="INBOX"):
        self.logs = logs
        self.server = server
        self.email_account = email_account
        self.password = password
        self.folder = folder

    def fetch_emails(self):
        prefix = f'[{self.__class__.__name__} | fetch_emails]'

        try:
            self.logs.logging_msg(f"{prefix} START", 'DEBUG')

            with IMAPClient(self.server) as client:
                self.logs.logging_msg(f"{prefix} 1", 'DEBUG')

                client.login(self.email_account, self.password)
                self.logs.logging_msg(f"{prefix} 2", 'DEBUG')

                client.select_folder(self.folder)
                messages = client.search(["ALL"])

                for msg_id in messages:
                    msg_data = client.fetch([msg_id], ["RFC822"])
                    msg_bytes = msg_data[msg_id][b'RFC822']
                    msg = email.message_from_bytes(msg_bytes, policy=default)

                    print(f"Sujet : {msg['Subject']}")
                    print(f"De : {msg['From']}")

                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            print(f"Contenu : {part.get_content()}")
                        elif part.get_content_type() == "text/html":
                            print(f"HTML : {part.get_content()[:500]}...")
                print("[INFO] Emails récupérés avec succès.")

        except Exception as e:
            self.logs.logging_msg(f"{prefix} Error: {e}", 'WARNING')