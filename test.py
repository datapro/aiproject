# import secrets; print(secrets.token_urlsafe(48))  

from google import genai
from app.dbconfig.schemas import settings

print("API key loaded:", bool(settings.GOOGLE_API_KEY))

client = genai.Client(
    api_key=settings.GOOGLE_API_KEY
)

response = client.models.generate_content(
    model="gemini-3.8-flash",
    contents="Say hello in one sentence."
)

print(response.text)