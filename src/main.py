import os
import dotenv
from utils_email import MicrosoftGraphClient
from logs import Logs
from utils import Newsletter


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    logs = Logs()
    if not logs.status:
        logs.logging_msg("START PROGRAM", 'WARNING')

        # Create an instance of OutlookMailFetcher
        logs.logging_msg("MAIN.PY: Connexion")
        client = MicrosoftGraphClient()
        me = client.make_graph_request("/me")

        # Fetch the latest emails
        logs.logging_msg("MAIN.PY: Fetching")
        client.read_mail_folder(client.folder_id_by_name("VEILLE"))

        # Create a newsletter
        logs.logging_msg("MAIN.PY: Creating newsletter")
        newsletter = Newsletter()
        for mail in client.emails:
            newsletter.add_content(mail.to_html())
        
        logs.logging_msg("END PROGRAM", 'WARNING')
