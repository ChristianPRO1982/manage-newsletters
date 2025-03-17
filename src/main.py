import os
import dotenv
from utils_email import OutlookMailFetcher
from logs import Logs


dotenv.load_dotenv(override=True)
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
PASSWORD = os.getenv("PASSWORD")
CLIENT_ID = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_APP_DIRECTORY_TENANT_ID")
CLIENT_SECRET = os.getenv("AZURE_SECRET_VALUE")


if __name__ == "__main__":
    logs = Logs()
    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        TENANT_ID = "common"  # 'common' for personal Outlook accounts

        # Create an instance of OutlookMailFetcher
        logs.logging_msg("MAIN.PY: Create instance", 'DEBUG')
        logs.logging_msg(f"MAIN.PY: TENANT_ID: {TENANT_ID}", 'DEBUG')
        outlook = OutlookMailFetcher(CLIENT_ID, TENANT_ID, CLIENT_SECRET)
        logs.logging_msg(f"outlook: {outlook.access_token}")

        # Fetch the latest 5 emails
        # logs.logging_msg("MAIN.PY: Fetching", 'DEBUG')
        # emails = outlook.get_emails(count=2)
        # logs.logging_msg(emails)

        # Send an email
        # response = outlook.send_email("recipient@example.com", "Test Subject", "This is a test email.")
        # print(response)
        
        logs.logging_msg("END PROGRAM", 'WARNING')
