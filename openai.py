from openai import OpenAI, DefaultHttpxClient
import httpx
from dotenv import load_dotenv, dotenv_values
import os


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    http_client=DefaultHttpxClient(
        proxies=os.getenv("PROXY"),
        transport=httpx.HTTPTransport(local_address=os.getenv("HOST")),
        timeout=20.0,
    ),
)

# client.files.create(
#     file=open("translations_data.jsonl", "rb"),
#     purpose="fine-tune"
# )


def chat_gpt(message):

    try:
        response = client.chat.completions.create(
            prompt=f'Translate the following text to Persion : {message}',
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        print(response.choices[0].message.content.strip())
    except Exception as e:
        print(e)
