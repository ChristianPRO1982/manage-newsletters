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
        client, error = newsletter.connexion()
        if error:
            logs.logging_msg(f"MAIN.PY: {error}", 'ERROR')
            exit()

        # Fetch the latest emails
        logs.logging_msg("MAIN.PY: Fetching")
        client.read_mail_folder(client.folder_id_by_name("VEILLE"))

        # Create a newsletter
        logs.logging_msg("MAIN.PY: Creating newsletter")
        for mail in client.emails:
            newsletter.add_content(mail.to_html())
        print(">>>>>")
        print(newsletter.content)
        print(">>>>>")
        
        logs.logging_msg("END PROGRAM", 'WARNING')
