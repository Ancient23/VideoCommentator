# OpenAI LLM summarizer
import openai
import os
import json


def summarize(timeline: list) -> str:
    """Summarize the timeline using a single LLM call (default behavior)."""
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


def summarize_chunked(timeline: list, chunk_size: int = 20) -> str:
    """
    Summarize the timeline in chunks, then summarize the summaries.
    Each chunk is summarized separately, then a final summary is generated from those summaries.
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chunk_summaries = []
    for i in range(0, len(timeline), chunk_size):
        chunk = timeline[i:i+chunk_size]
        prompt = (
            "Given this JSON timeline chunk, write 1-2 sentences summarizing the main events and setting.\n"
            f"Timeline chunk: {json.dumps(chunk)}"
        )
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=128,
            temperature=0.5,
        )
        chunk_summaries.append(response.choices[0].message.content.strip())

    # Now summarize the chunk summaries
    final_prompt = (
        "Given these chunk summaries, write ≤4 sentences describing the main events and setting.\n"
        f"Chunk summaries: {json.dumps(chunk_summaries)}"
    )
    final_response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=256,
        temperature=0.5,
    )
    return final_response.choices[0].message.content.strip()
