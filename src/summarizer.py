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

def generate_voiceover_script(timeline: list, style: str = "Sports Commentator") -> str:
    """
    Generate a short voiceover script in the style of the given narrator. Only narration is included.
    """
    prompt = (
        f"Given this JSON timeline, create a short voiceover script in the style of {style}. Include only the narration.\n"
        f"Timeline: {json.dumps(timeline)}"
    )
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=256,
        temperature=0.7,
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

def generate_voiceover_script_chunked(timeline: list, style: str = "David Attenborough", chunk_size: int = 20) -> str:
    """
    Generate a voiceover script in the given style using chunked summarization for long timelines.
    """
    client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    chunk_scripts = []
    for i in range(0, len(timeline), chunk_size):
        chunk = timeline[i:i+chunk_size]
        prompt = (
            f"Given this JSON timeline chunk, create a short voiceover script in the style of {style}. Include only the narration.\n"
            f"Timeline chunk: {json.dumps(chunk)}"
        )
        response = client.chat.completions.create(
            model="gpt-4.1-nano",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=128,
            temperature=0.7,
        )
        chunk_scripts.append(response.choices[0].message.content.strip())

    # Now combine the chunk scripts into a final script
    final_prompt = (
        f"Given these chunked voiceover scripts, combine them into a single short voiceover script in the style of {style}. Include only the narration.\n"
        f"Chunked scripts: {json.dumps(chunk_scripts)}"
    )
    final_response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=[{"role": "user", "content": final_prompt}],
        max_tokens=256,
        temperature=0.7,
    )
    return final_response.choices[0].message.content.strip()
