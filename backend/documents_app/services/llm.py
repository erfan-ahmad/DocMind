import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

_client = None


def get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY تعریف نشده است.")
        _client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1",
        )
    return _client


def generate(prompt):
    client = get_client()
    completion = client.chat.completions.create(
        model="openrouter/free",
        messages=[
            {
                "role": "system",
                "content": (
                    "تو یک دستیار حقوقی هستی. فقط بر اساس context داده‌شده جواب بده. "
                    "اگر جواب در context نبود، بگو «در اسناد موجود پاسخی یافت نشد». "
                    "هیچ اطلاعاتی از خودت اضافه نکن."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.1,
    )
    return completion.choices[0].message.content


def build_prompt(query, chunks):
    context = "\n\n".join([c.text for c in chunks])
    return f"""بر اساس اسناد زیر به سؤال پاسخ بده.

سؤال: {query}

اسناد:
{context}

پاسخ:"""