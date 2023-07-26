from requests import post,Response
from fake_useragent import UserAgent

def send_discord_webhook(url: str, data: dict, headers: dict = {'Content-Type': 'application/json','User-Agent': UserAgent().random}) -> Response:
    """
    Sends a webhook to a Discord channel using the provided URL, data, and headers.

    Args:
        url (str): The URL of the Discord webhook.
        data (dict): The data to send in the webhook.
        headers (dict, optional): The headers to include in the webhook request. Defaults to {'Content-Type': 'application/json','User-Agent': UserAgent().random}.

    Returns:
        Response: The response from the webhook request.
    """
    response = post(
        url, 
        json=data, 
        headers=headers
    )
    return response