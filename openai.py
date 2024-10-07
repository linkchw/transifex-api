from openai import OpenAI, DefaultHttpxClient
import httpx
from config import OPENAI_API_KEY

client = OpenAI(
    api_key=OPENAI_API_KEY,
    http_client=DefaultHttpxClient(
        proxies="http://192.168.88.111:10809",
        transport=httpx.HTTPTransport(local_address="192.168.88.111"),
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
