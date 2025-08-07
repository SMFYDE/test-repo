import os
import requests
from typing import Any


async def email_created_thread(email: str, thread_id: str) -> Any:
    """
    Send an email to the specified email address after a copied thread is created.
    """
    url = os.getenv("BLUEGEN_NOTIFICATION_EMAIL_ENDPOINT")
    if url is None:
        raise ValueError(
            "BLUEGEN_NOTIFICATION_EMAIL_ENDPOINT environment variable is not set"
        )

    payload = {
        "sender_fullname": "No Reply - BlueGen",
        "sender_email": "noreply-bluegen@socotec.us",
        "recipient_email": email,
        "thread_id": thread_id,
    }
    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        response.raise_for_status()

if __name__ == "__main__":
    import asyncio

    # Example usage
    try:
        result = asyncio.run(email_created_thread("yannis.defontaine@socotec.com", "12345"))
        print("Email sent successfully:", result)
    except Exception as e:
        print("Error sending email:", e)
