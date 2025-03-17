import os
import dotenv
from utils_email import MicrosoftGraphClient
from logs import Logs


dotenv.load_dotenv(override=True)
# EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
# PASSWORD = os.getenv("PASSWORD")
# CLIENT_ID = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
# TENANT_ID = os.getenv("AZURE_APP_DIRECTORY_TENANT_ID")
# CLIENT_SECRET = os.getenv("AZURE_SECRET_VALUE")


if __name__ == "__main__":
    logs = Logs()
    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        # TENANT_ID = "common"  # 'common' for personal Outlook accounts

        # Create an instance of OutlookMailFetcher
        logs.logging_msg("MAIN.PY: Connexion")
        client = MicrosoftGraphClient()
        me = client.make_graph_request("/me")

        # Fetch the latest emails
        logs.logging_msg("MAIN.PY: Fetching")
        logs.logging_msg(client.read_mail_folder(client.folder_id_by_name("VEILLE")))
        # logs.logging_msg(emails)

        # Send an email
        # response = outlook.send_email("recipient@example.com", "Test Subject", "This is a test email.")
        # print(response)
        
        logs.logging_msg("END PROGRAM", 'WARNING')
