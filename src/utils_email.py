import os
import dotenv
import requests
from msal import PublicClientApplication
from datetime import datetime, timedelta

# Charger les variables d'environnement
dotenv.load_dotenv(override=True)

class GraphAuth:
    """Gère l'authentification OAuth2 via Device Code Flow pour Microsoft Graph API."""
    
    def __init__(self):
        self.client_id = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
        self.tenant_id = "common"  # Mettre l'ID de ton tenant si besoin
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.access_token = None
        self.authenticate()

    def authenticate(self):
        """Lance le Device Code Flow et récupère un token d'accès."""
        app = PublicClientApplication(self.client_id, authority=self.authority)
        flow = app.initiate_device_flow(scopes=self.scopes)

        if "user_code" not in flow:
            raise Exception("⚠️ Erreur lors de l'initiation du Device Code Flow.")

        print(f"🔑 Allez sur {flow['verification_uri']} et entrez le code : {flow['user_code']}")

        token_response = app.acquire_token_by_device_flow(flow)
        if "access_token" in token_response:
            self.access_token = token_response["access_token"]
        else:
            raise Exception("❌ Authentification échouée.")

    def get_headers(self):
        """Retourne les headers pour les requêtes à l'API Graph."""
        return {"Authorization": f"Bearer {self.access_token}", "Content-Type": "application/json"}


class EmailManager:
    """Gère les emails via Microsoft Graph API."""
    
    BASE_URL = "https://graph.microsoft.com/v1.0/me"

    def __init__(self, auth):
        self.auth = auth

    def list_emails(self, folder="Inbox", limit=10):
        """Récupère les emails d'un dossier spécifique."""
        url = f"{self.BASE_URL}/mailFolders/{folder}/messages?$top={limit}"
        response = requests.get(url, headers=self.auth.get_headers())

        if response.status_code == 200:
            emails = response.json().get("value", [])
            return [{"id": email["id"], "subject": email["subject"]} for email in emails]
        else:
            raise Exception(f"⚠️ Erreur lors de la récupération des emails: {response.text}")

    def send_email(self, recipient, subject, body):
        """Envoie un email à un destinataire."""
        url = f"{self.BASE_URL}/sendMail"
        email_data = {
            "message": {
                "subject": subject,
                "body": {"contentType": "Text", "content": body},
                "toRecipients": [{"emailAddress": {"address": recipient}}],
            },
            "saveToSentItems": "true",
        }
        response = requests.post(url, headers=self.auth.get_headers(), json=email_data)

        if response.status_code == 202:
            print("✅ Email envoyé avec succès !")
        else:
            raise Exception(f"⚠️ Erreur lors de l'envoi de l'email: {response.text}")

    def move_email(self, email_id, target_folder):
        """Déplace un email d’un dossier à un autre."""
        url = f"{self.BASE_URL}/messages/{email_id}/move"
        payload = {"destinationId": target_folder}
        response = requests.post(url, headers=self.auth.get_headers(), json=payload)

        if response.status_code == 201:
            print(f"✅ Email déplacé vers {target_folder}.")
        else:
            raise Exception(f"⚠️ Erreur lors du déplacement de l'email: {response.text}")

    def delete_old_emails(self, folder="Inbox", days_old=30):
        """Supprime les emails plus anciens que X jours dans un dossier donné."""
        url = f"{self.BASE_URL}/mailFolders/{folder}/messages"
        response = requests.get(url, headers=self.auth.get_headers())

        if response.status_code == 200:
            emails = response.json().get("value", [])
            cutoff_date = datetime.utcnow() - timedelta(days=days_old)

            for email in emails:
                email_date = datetime.strptime(email["receivedDateTime"], "%Y-%m-%dT%H:%M:%SZ")
                if email_date < cutoff_date:
                    delete_url = f"{self.BASE_URL}/messages/{email['id']}"
                    delete_response = requests.delete(delete_url, headers=self.auth.get_headers())

                    if delete_response.status_code == 204:
                        print(f"🗑️ Email supprimé : {email['subject']} ({email_date})")
                    else:
                        print(f"⚠️ Erreur suppression {email['subject']}: {delete_response.text}")

        else:
            raise Exception(f"⚠️ Erreur récupération emails : {response.text}")


# 📌 EXEMPLE D'UTILISATION
if __name__ == "__main__":
    print("START")

    auth = GraphAuth()  # Authentification
    email_manager = EmailManager(auth)

    # 📨 Lister les emails
    print("PJ 📨 Récupération des emails...")
    emails = email_manager.list_emails(limit=5)
    print("📩 Emails reçus :", emails)

    # ✉️ Envoyer un email
    print("PJ ✉️ Envoi d'un email...")
    EMAIL_TARGET = os.getenv("EMAIL_TARGET")
    email_manager.send_email(EMAIL_TARGET, "Test API", "Hello, ceci est un test !")

    # 📂 Déplacer un email
    # if emails:
    #     email_id = emails[0]["id"]
    #     email_manager.move_email(email_id, "Archives")

    # 🗑️ Supprimer les emails trop vieux
    # email_manager.delete_old_emails(days_old=60)

    print("END")