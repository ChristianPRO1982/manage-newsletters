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

        for e, i in enumerate(all_emails):
            self.emails.append(OutlookMail(i["subject"], i["from"]["emailAddress"]["name"], i["receivedDateTime"], i["bodyPreview"]))


    def list_mail_folders(self):
        """Lists all mail folders in the mailbox."""
        endpoint = "/me/mailFolders"
        return self.make_graph_request(endpoint)
    

    def folder_id_by_name(self, folder_name):
        """Returns the ID of a mail folder by its name."""
        for folder in self.folders["value"]:
            if folder["displayName"] == folder_name:
                return folder["id"]
        return None
    

    def send_email(self, subject, content, to_recipients):
        """Sends an email using Microsoft Graph API."""

        body = f"""
<html>
    <body>
        <h2>{subject}</h2>
        <p><strong>Received:</strong> {to_recipients}</p>
        <p>{content}</p>
    </body>
</html>
        """

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

        response = requests.post(f"https://graph.microsoft.com/v1.0{endpoint}", headers=headers, json=email_msg)
        if response.status_code == 202:
            print("Email sent successfully.")
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")



class OutlookMail():
    def __init__(self, subject, name, receivedDateTime, bodyPreview):
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