import os
import requests
from msal import ConfidentialClientApplication
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_RECIPIENT = "yannis.defontaine@socotec.com"

# Obtenir un token d'accès avec MSAL (Microsoft Authentication Library)
authority = f"https://login.microsoftonline.com/{TENANT_ID}"
app = ConfidentialClientApplication(
    CLIENT_ID, authority=authority, client_credential=CLIENT_SECRET
)

scope = ["https://graph.microsoft.com/.default"]

result = app.acquire_token_for_client(scopes=scope)

if "access_token" in result:
    access_token = result["access_token"]
    # Préparer l'e-mail à envoyer
    endpoint = f"https://graph.microsoft.com/v1.0/users/{EMAIL_USER}/sendMail"
    message = {
        "message": {
            "subject": "Test Microsoft Graph Python",
            "body": {
                "contentType": "Text",
                "content": "Yes im a simp"
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": EMAIL_RECIPIENT
                    }
                }
            ]
        }
    }

    # Appeler l'API Graph pour envoyer le mail
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    response = requests.post(endpoint, json=message, headers=headers)
    if response.status_code == 202:
        print("E-mail envoyé avec succès !")
    else:
        print("Erreur :", response.status_code, response.text)
else:
    print("Erreur pour obtenir le token :", result.get("error_description"))
