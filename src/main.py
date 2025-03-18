import os
import dotenv
from logs import Logs
from utils import Newsletter


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logs = Logs()
    FOLDER_SCANNED = os.getenv('FOLDER_SCANNED')
    ARCHIVE_FOLDER = os.getenv('ARCHIVE_FOLDER')
    EMAILS_RETENTION_DAYS = os.getenv('EMAILS_RETENTION_DAYS')
    EMAIL_SUBJECT = os.getenv('EMAIL_SUBJECT')

    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        newsletter = Newsletter(logs)

        # 01 CONNECTION
        client, error = newsletter.connection()
        if error:
            logs.logging_msg(f"MAIN.PY: {error}", 'ERROR')
            exit()

        # 02 FETCH EMAILS
        if newsletter.fetch_emails(client, FOLDER_SCANNED): exit()

        # 03 CREATE A NEWSLETTER
        if newsletter.create_email_body(client.emails, EMAIL_SUBJECT): exit()

        # 04 SEND EMAIL
        if newsletter.send_email(client): exit()

        # 05 MOVED EMAIL
        # newsletter.move_emails(client, ARCHIVE_FOLDER)

        # 06 DELETE EMAILS
        newsletter.delete_old_emails(client, ARCHIVE_FOLDER, EMAILS_RETENTION_DAYS)
        
        logs.logging_msg("END PROGRAM", 'WARNING')
