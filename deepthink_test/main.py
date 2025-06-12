import boto3
import json
import logging
from botocore.exceptions import ClientError

# Configure le logger
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Initialisation du client boto3
boto3_client = boto3.client(
    "bedrock-runtime",
    region_name="us-west-2"
)

# Identifiant du modèle
text_model_id = "amazon.titan-text-express-v1"


def titan_text_model_request(user_prompt: str) -> str | None:
    """
    Envoie une requête au modèle texte Amazon Titan et retourne la réponse.
    """
    try:
        # Prépare le corps de la requête
        body = {
            "inputText": user_prompt,
        }

        # Appel au modèle via Bedrock
        response = boto3_client.invoke_model(
            body=json.dumps(body),
            modelId=text_model_id,
            accept="application/json",
            contentType="application/json",
        )

        # Décodage de la réponse
        response_body = json.loads(response["body"].read())
        return response_body.get("results", [{}])[0].get("outputText", "")

    except ClientError as e:
        logger.error("ClientError when invoking model: %s", e)
        return None
    except Exception as e:
        logger.error("Unhandled exception: %s", e)
        return None


prompt = """
Réfléchis étape par étape.
Combien font 267 * 23 ?
"""
# 267 * 23 = 6141
response = titan_text_model_request(prompt)

print("Response:", response)
