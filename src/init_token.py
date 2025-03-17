from msal import PublicClientApplication
import os
import dotenv

dotenv.load_dotenv(override=True)

CLIENT_ID = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
TENANT_ID = os.getenv("AZURE_APP_DIRECTORY_TENANT_ID")
TENANT_ID = "common"  # Remplace par ton tenant ID si nécessaire
AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"
SCOPES = ["https://graph.microsoft.com/.default"]

# EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
# PASSWORD = os.getenv("PASSWORD")
# CLIENT_ID = os.getenv("AZURE_APP_APPLICATION_CLIENT_ID")
# TENANT_ID = os.getenv("AZURE_APP_DIRECTORY_TENANT_ID")
# CLIENT_SECRET = os.getenv("AZURE_SECRET_VALUE")

print(f"PJ TENANT_ID: {TENANT_ID}")

app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY)

# 1️⃣ Demande un code d'authentification
flow = app.initiate_device_flow(scopes=SCOPES)
if "user_code" not in flow:
    print(f"PJ flow:{flow}")
    raise Exception("Device flow initiation failed")

print(f"Go to {flow['verification_uri']} and enter the code: {flow['user_code']}")

# 2️⃣ Attente de l'authentification de l'utilisateur
token_response = app.acquire_token_by_device_flow(flow)

if "access_token" in token_response:
    access_token = token_response["access_token"]
else:
    raise Exception(f"Authentication failed: {token_response.get('error_description', 'Unknown error')}")
