# OpenAI LLM summarizer
import openai
import os
import json

def summarize(timeline: list) -> str:
    prompt = (
        "Given this JSON timeline, write ≤4 sentences describing the main events and setting.\n"
        f"Timeline: {json.dumps(timeline)}"
    )
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.5,
    )
    return response.choices[0].message.content.strip()
