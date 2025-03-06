from utils_email import OutlookEmailFetcher
import dotenv


dotenv.load_dotenv(override=True)


if __name__ == "__main__":
    fetcher = OutlookEmailFetcher(
        server="imap-mail.outlook.com",
        email_account="email@outlook.com",
        password="votre_mot_de_passe_application",
        folder="Newsletter"
    )
    fetcher.fetch_emails()