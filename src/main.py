import os
import dotenv
from logs import Logs
from utils import Newsletter


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logs = Logs()
    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        newsletter = Newsletter(logs)

        # 01 CONNECTION
        client, error = newsletter.connection()
        if error:
            logs.logging_msg(f"MAIN.PY: {error}", 'ERROR')
            exit()

        # 02 FETCH EMAILS
        logs.logging_msg("MAIN.PY: Fetching")
        client.read_mail_folder(client.folder_id_by_name("VEILLE"))

        # 03 CREATE A NEWSLETTER
        newsletter.create_email_body(client.emails)
        
        logs.logging_msg("END PROGRAM", 'WARNING')
