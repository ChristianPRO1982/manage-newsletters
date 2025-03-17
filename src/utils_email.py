import requests
import json
import os
from msal import PublicClientApplication


class MicrosoftGraphClient:
    def __init__(self, access_token="access_token"):
        self.access_token = access_token
        self.client_id = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
        self.tenant_id = "common"  # Replace with your tenant ID if necessary
        self.authority = f"https://login.microsoftonline.com/{self.tenant_id}"
        self.scopes = ["https://graph.microsoft.com/.default"]
        self.token_file = "token.json"
        self.app = PublicClientApplication(self.client_id, authority=self.authority)
        self.access_token = self.load_token()
        self.folders = self.list_mail_folders()
        self.emails = []


    def load_token(self):
        """Loads a valid token or requests authentication if necessary."""
        if os.path.exists(self.token_file):
            with open(self.token_file, "r") as f:
                token_data = json.load(f)
            
            if "access_token" in self.access_token:
                return token_data["access_token"]

            if "refresh_token" in self.access_token:
                new_token = self.app.acquire_token_by_refresh_token(token_data["refresh_token"], self.scopes)
                if "access_token" in new_token:
                    self.save_token(new_token)
                    return new_token["access_token"]
                else:
                    print("🔴 Refresh token expired. Reauthentication required.")

        return self.authenticate_user()


    def authenticate_user(self):
        """Requests interactive authentication if necessary."""
        flow = self.app.initiate_device_flow(scopes=self.scopes)
        if "user_code" not in flow:
            raise Exception("Failed to initialize Device Flow")

        print(f"👉 Open {flow['verification_uri']} and use the code : {flow['user_code']}")

        token_response = self.app.acquire_token_by_device_flow(flow)
        if "access_token" in token_response:
            self.save_token(token_response)
            return token_response["access_token"]
        else:
            raise Exception(f"Authentication failed: {token_response.get('error_description', 'Unknown error')}")


    def save_token(self, token_data):
        """Saves the token locally to avoid reconnecting each time."""
        with open(self.token_file, "w") as f:
            json.dump(token_data, f)


    def make_graph_request(self, endpoint):
        """Executes a request to Microsoft Graph."""
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        response = requests.get(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers)
        return response.json()
    

    def make_graph_request_pages(self, endpoint):
        """Executes a request to the Microsoft Graph API with pagination handling."""

        headers = {"Authorization": f"Bearer {self.access_token}"}
        url = f"https://graph.microsoft.com/v1.0{endpoint}"
        results = []

        while url:
            response = requests.get(url, headers=headers)
            data = response.json()

            if "value" in data:
                results.extend(data["value"])

            url = data.get("@odata.nextLink")

        return results
    
    
    def read_mail_folder(self, folder_id):
        """Reads emails from a specified folder."""
        
        self.emails = []
        
        endpoint = f"/me/mailFolders/{folder_id}/messages"
        all_emails = self.make_graph_request_pages(endpoint)

        for e, email in enumerate(all_emails):
            self.emails.append(OutlookMail(
                email["id"],
                email["subject"],
                email["from"]["emailAddress"]["name"],
                email["receivedDateTime"],
                email["bodyPreview"])
                )


    def list_mail_folders(self, folder_id=""):
        """Lists all mail folders in the mailbox."""

        if folder_id:
            endpoint = f"/me/mailFolders/{folder_id}/childFolders"
        else:
            endpoint = f"/me/mailFolders"
        
        folders = self.make_graph_request(endpoint)
        for folder in folders['value']:
            print("Folder:", folder['displayName'])
            if folder['childFolderCount'] > 0:
                folders['value'].extend(self.list_mail_folders(folder['id'])['value'])

        return self.make_graph_request(endpoint)
    

    def folder_id_by_name(self, folder_name):
        """Returns the ID of a mail folder by its name."""
        print(folder_name, self.folders)
        for folder in self.folders["value"]:
            if folder["displayName"] == folder_name:
                return folder["id"]
        return None
    

    def send_email(self, subject, body, to_recipients)->bool:
        """Sends an email using Microsoft Graph API."""

        if isinstance(to_recipients, str):
            to_recipients = [to_recipients]  # Convert to list if it's a single string
        if not to_recipients or not all(isinstance(email, str) and "@" in email for email in to_recipients):
            raise ValueError(f"Invalid recipients: {to_recipients}")

        endpoint = "/me/sendMail"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        email_msg = {
            "message": {
                "subject": subject,
                "body": {
                    "contentType": "HTML",
                    "content": body
                },
                "toRecipients": [{"emailAddress": {"address": recipient}} for recipient in to_recipients]
            },
            "saveToSentItems": "true"
        }

        # print(f"[DEBUG] Payload envoyé : {json.dumps(email_msg, indent=2)}")  # Vérification


        response = requests.post(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers, json=email_msg)
        if response.status_code == 202 or response.status_code == 200:
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
        

    def move_email(self, email_id, destination_folder_id):
        """Moves an email to a specified folder."""
        
        endpoint = f"/me/messages/{email_id}/move"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
        payload = {
            "destinationId": destination_folder_id
        }

        response = requests.post(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers, json=payload)
        if response.status_code == 201:
            return True
        else:
            print(f"Failed to move email: {response.status_code} - {response.text}")
            return False



class OutlookMail():
    def __init__(self, id, subject, name, receivedDateTime, bodyPreview):
        self.id = id
        self.name = name
        self.subject = subject
        self.receivedDateTime = receivedDateTime
        self.bodyPreview = bodyPreview

    
    def to_html(self):
        """Creates an HTML formatted text with all the email information."""

        html_content = f"""
        <div>
            <h2>{self.subject}</h2>
            <p><strong>From:</strong> {self.name}</p>
            <p><strong>Received:</strong> {self.receivedDateTime}</p>
            <p>{self.bodyPreview}</p>
        </div>
        """

        return html_content