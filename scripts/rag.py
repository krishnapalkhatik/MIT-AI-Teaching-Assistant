from pathlib import Path
import pickle
import requests
import faiss
from sentence_transformers import SentenceTransformer
import os

# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

INDEX_PATH = BASE_DIR / "data" / "faiss_index.index"
METADATA_PATH = BASE_DIR / "data" / "metadata.pkl"


# ============================================================
# LOAD EMBEDDING MODEL
# ============================================================

print("Loading embedding model...")

model_name = "sentence-transformers/all-MiniLM-L6-v2"

model = SentenceTransformer(model_name)


# ============================================================
# LOAD FAISS INDEX + METADATA
# ============================================================

print("Loading FAISS index...")

index = faiss.read_index(str(INDEX_PATH))

with open(METADATA_PATH, "rb") as f:
    chunks = pickle.load(f)

print(f"Loaded {index.ntotal} vectors")


# ============================================================
# CONVERSATION MEMORY
# ============================================================

conversation_history = []


# ============================================================
# ASK QUESTION
# ============================================================

def ask_question(query):

    # --------------------------------------------------------
    # 1. Convert question into embedding
    # --------------------------------------------------------

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True
    )


    # --------------------------------------------------------
    # 2. Retrieve relevant chunks from FAISS
    # --------------------------------------------------------

    k = 10

    distances, indices = index.search(
        query_embedding,
        k
    )

    retrieved_chunks = []

    # Smaller distance = more similar
    DISTANCE_THRESHOLD = 1.35

    for idx, distance in zip(indices[0], distances[0]):

        if idx != -1 and distance <= DISTANCE_THRESHOLD:

            retrieved_chunks.append({
                "lecture": chunks[idx]["lecture"],
                "chunk_id": chunks[idx]["chunk_id"],
                "text": chunks[idx]["text"],
                "distance": float(distance)
            })


    # --------------------------------------------------------
    # 3. Build lecture context
    # --------------------------------------------------------

    context_parts = []

    for item in retrieved_chunks:

        context_parts.append(
            f"Lecture: {item['lecture']}\n"
            f"Chunk ID: {item['chunk_id']}\n"
            f"Content:\n{item['text']}"
        )

    context = "\n\n---\n\n".join(context_parts)


    # --------------------------------------------------------
    # 4. Build conversation history
    # --------------------------------------------------------

    history_text = ""

    if conversation_history:

        history_parts = []

        # Only keep the last 6 exchanges
        for message in conversation_history[-6:]:

            history_parts.append(
                f"{message['role'].upper()}: {message['content']}"
            )

        history_text = "\n".join(history_parts)


    # --------------------------------------------------------
    # 5. Teaching Prompt
    # --------------------------------------------------------

    prompt = f"""
You are an AI Teaching Assistant for MIT 6.0002.

Your job is to teach the student, not just give a short answer.

IMPORTANT RULES:

1. Use ONLY the lecture context provided below for factual information.

2. Do NOT use outside knowledge.

3. Do NOT invent facts, examples, formulas, numerical examples,
   or explanations that are not supported by the lecture context.

4. If the context does not contain enough information to answer
   the question, say:

"I couldn't find enough information in the provided MIT lectures."

5. Explain concepts in a beginner-friendly way.

6. You may use an analogy ONLY if the lecture context contains
   or supports that analogy.

7. If the question involves a process or algorithm, explain it
   step-by-step using information from the lectures.

8. If the lecture gives an example, use that example.

9. Ignore retrieved chunks that are not directly relevant to
   the student's question.

10. Every factual claim should be supported by the retrieved
    lecture context.

11. Keep the answer focused on the student's question.

12. Use the conversation history only to understand references
    such as "it", "this", "that", or follow-up questions.

13. Do not treat information from the conversation history as
    lecture evidence. Lecture context is the source of truth.

ANSWER FORMAT:

### Explanation

Give a clear and beginner-friendly explanation.

### Intuition

Give an intuitive explanation or analogy ONLY when supported
by the lecture context.

### Example

Give an example ONLY if the lecture context contains one.

If there is no suitable example, say:

"No specific example was provided in the retrieved lecture context."

### Key Takeaway

Give 1-3 important points the student should remember.

### Sources

List the lecture names and chunk IDs actually used.

------------------------------------------------------------

CONVERSATION HISTORY:

{history_text}

------------------------------------------------------------

LECTURE CONTEXT:

{context}

------------------------------------------------------------

STUDENT QUESTION:

{query}

"""


    # --------------------------------------------------------
    # 6. Generate answer using local Ollama or a hosted API

    llm_provider = os.getenv("LLM_PROVIDER", "ollama").lower()

    try:
        if llm_provider == "ollama":
            response = requests.post(
                "http://localhost:11434/api/chat",
                json={
                    "model": "qwen3:1.7b",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "stream": False
                },
                timeout=120
            )
            response.raise_for_status()
            answer = response.json()["message"]["content"]

        elif llm_provider == "openai":
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                return "Error: OPENAI_API_KEY is not configured.", retrieved_chunks

            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
                    "messages": [{"role": "user", "content": prompt}]
                },
                timeout=300
            )
            response.raise_for_status()
            answer = response.json()["choices"][0]["message"]["content"]

        else:
            return f"Error: Unsupported LLM_PROVIDER '{llm_provider}'.", retrieved_chunks

    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to the configured LLM provider.", retrieved_chunks
    except requests.exceptions.Timeout:
        return "Error: The LLM provider took too long to respond.", retrieved_chunks
    except requests.exceptions.HTTPError as e:
        return f"Error from LLM provider: {e.response.status_code} — {e.response.text[:500]}", retrieved_chunks
    except (KeyError, ValueError) as e:
        return f"Error reading the LLM response: {e}", retrieved_chunks



    
    # --------------------------------------------------------
    # 7. Handle Ollama errors
    # --------------------------------------------------------

    if response.status_code != 200:

        return (
            f"Error communicating with Ollama: {response.text}",
            retrieved_chunks
        )


    # --------------------------------------------------------
    # 8. Get generated answer
    # --------------------------------------------------------

    result = response.json()

    answer = result["message"]["content"]


    # --------------------------------------------------------
    # 9. Save conversation memory
    # --------------------------------------------------------

    conversation_history.append({
        "role": "student",
        "content": query
    })

    conversation_history.append({
        "role": "assistant",
        "content": answer
    })


    return answer, retrieved_chunks


## ============================================================
# TERMINAL CHAT MODE
# ============================================================

if __name__ == "__main__":

    print("\nMIT AI Teaching Assistant")
    print("Type 'exit' to quit.\n")

    while True:
        query = input("You: ").strip()

        if query.lower() == "exit":
            print("Goodbye!")
            break

        if not query:
            print("Please enter a question.\n")
            continue

        print("\nThinking...\n")

        answer, sources = ask_question(query)

        print("=" * 80)
        print("ANSWER")
        print("=" * 80)
        print(answer)

        print("\n" + "=" * 80)
        print("RETRIEVED SOURCES")
        print("=" * 80)

        for i, source in enumerate(sources, start=1):
            print(f"\n--- Source {i} ---")
            print(f"Lecture: {source['lecture']}")
            print(f"Chunk ID: {source['chunk_id']}")
            print(f"Distance: {source['distance']:.4f}")
            print(source["text"][:400])

        print()