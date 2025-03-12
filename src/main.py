import os
import dotenv
from utils_email import OutlookEmailFetcher
from logs import Logs


dotenv.load_dotenv(override=True)
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
PASSWORD = os.getenv("PASSWORD")


if __name__ == "__main__":
    logs = Logs()
    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        fetcher = OutlookEmailFetcher(
            logs,
            server="imap-mail.outlook.com",
            email_account=EMAIL_ACCOUNT,
            password=PASSWORD,
            folder="Newsletter"
        )
        fetcher.fetch_emails()
        
        logs.logging_msg("END PROGRAM", 'WARNING')