
import os
import re
import pickle
import requests
from pathlib import Path
from collections import Counter

from fastapi import HTTPException

PROJECT_ROOT = Path(__file__).resolve().parent.parent
METADATA_PATH = PROJECT_ROOT / "data" / "metadata.pkl"

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


def load_chunks():
    if not METADATA_PATH.exists():
        raise RuntimeError(f"Lecture metadata not found: {METADATA_PATH}")

    with open(METADATA_PATH, "rb") as file:
        metadata = pickle.load(file)

    if isinstance(metadata, dict):
        chunks = metadata.get("chunks", [])
    else:
        chunks = metadata

    if not isinstance(chunks, list):
        raise RuntimeError("Unexpected metadata.pkl format")

    return chunks


CHUNKS = load_chunks()


def tokenize(text):
    return re.findall(r"[a-zA-Z0-9]+", text.lower())


def retrieve_chunks(question, top_k=5):
    query_words = set(tokenize(question))
    scored = []

    for chunk in CHUNKS:
        if not isinstance(chunk, dict):
            continue

        content = str(chunk.get("text", chunk.get("content", "")))
        if not content.strip():
            continue

        chunk_words = tokenize(content)
        word_counts = Counter(chunk_words)

        score = sum(
            min(word_counts[word], 3)
            for word in query_words
        )

        if score > 0:
            scored.append((score, chunk, content))

    scored.sort(key=lambda item: item[0], reverse=True)
    return scored[:top_k]


def ask_question(question):
    api_key = os.getenv("GROQ_API_KEY")
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-20b")

    if not api_key:
        raise RuntimeError("GROQ_API_KEY is not configured")

    matches = retrieve_chunks(question)

    if not matches:
        return (
            "### Explanation\n"
            "I couldn't find enough relevant information in the available MIT lecture chunks.\n\n"
            "### Intuition\nTry asking the question using terms from the lectures.\n\n"
            "### Example\nNo relevant lecture example was retrieved.\n\n"
            "### Key Takeaway\nThe answer should be based on relevant lecture material.",
            [],
        )

    context_parts = []
    sources = []

    for score, chunk, content in matches:
        lecture = str(chunk.get("lecture", chunk.get("source", "MIT lecture")))
        chunk_id = chunk.get("chunk_id", chunk.get("id", "unknown"))

        context_parts.append(
            f"Lecture: {lecture}\n"
            f"Chunk ID: {chunk_id}\n"
            f"Content:\n{content[:3500]}"
        )

        sources.append({
            "lecture": lecture,
            "chunk_id": chunk_id,
            "distance": float(score),
        })

    context = "\n\n---\n\n".join(context_parts)

    prompt = f"""
You are a beginner-friendly MIT AI Teaching Assistant.
Answer the student's question using the supplied MIT lecture excerpts.

Rules:
- Ground factual claims in the supplied excerpts.
- If the excerpts do not contain enough information, say so clearly.
- Explain technical terms in simple language.
- Do not invent lecture citations or claim unsupported details.
- Use these exact headings:
### Explanation
### Intuition
### Example
### Key Takeaway

MIT lecture excerpts:
{context}

Student question:
{question}
"""

    response = requests.post(
        GROQ_API_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
        },
        timeout=60,
    )

    if not response.ok:
        raise RuntimeError(
            f"Groq API error ({response.status_code}): {response.text[:500]}"
        )

    answer = response.json()["choices"][0]["message"]["content"]
    return answer, sources
