from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from scripts.rag import ask_question


app = FastAPI(title="MIT AI Teaching Assistant")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def parse_answer(answer: str):
    sections = {
        "explanation": "",
        "intuition": "",
        "example": "",
        "takeaway": "",
    }

    current = None

    for line in answer.splitlines():
        line_clean = line.strip()

        if line_clean.lower().startswith("### explanation"):
            current = "explanation"
            continue

        if line_clean.lower().startswith("### intuition"):
            current = "intuition"
            continue

        if line_clean.lower().startswith("### example"):
            current = "example"
            continue

        if line_clean.lower().startswith("### key takeaway"):
            current = "takeaway"
            continue

        if line_clean.lower().startswith("### sources"):
            current = None
            continue

        if current:
            sections[current] += line + "\n"

    for key in sections:
        sections[key] = sections[key].strip()

    return sections


@app.get("/")
def root():
    return {
        "message": "MIT AI Teaching Assistant API is running!"
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ask")
def ask(data: dict):
    question = data.get("question", "").strip()

    if not question:
        return {
            "error": "Question is required"
        }

    answer, sources = ask_question(question)

    parsed = parse_answer(answer)

    return {
        "explanation": parsed["explanation"],
        "intuition": parsed["intuition"],
        "example": parsed["example"],
        "takeaway": parsed["takeaway"],
        "sources": [
            {
                "lecture": source["lecture"],
                "chunk_id": source["chunk_id"],
                "distance": source["distance"],
            }
            for source in sources
        ],
    }