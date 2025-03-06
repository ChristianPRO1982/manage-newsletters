from imapclient import IMAPClient
import email
from email.policy import default


class OutlookEmailFetcher:
    def __init__(self, server, email_account, password, folder="INBOX"):
        self.server = server
        self.email_account = email_account
        self.password = password
        self.folder = folder

    def fetch_emails(self):
        try:
            with IMAPClient(self.server) as client:
                client.login(self.email_account, self.password)
                print("[INFO] Connexion au serveur réussie.")

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
            print(f"[ERREUR] Problème lors de la récupération des emails : {e}")