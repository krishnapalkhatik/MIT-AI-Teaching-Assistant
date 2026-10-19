# MIT AI Teaching Assistant 🎓

An AI-powered teaching assistant that helps students understand concepts from MIT 6.0002 lecture materials through simple explanations, intuition, examples, and key takeaways.

🔗 **Live Demo:** [MIT AI Teaching Assistant](https://mit-ai-teaching-assistant.vercel.app)

📂 **GitHub Repository:** [MIT-AI-Teaching-Assistant](https://github.com/krishnapalkhatik97-jpg/MIT-AI-Teaching-Assistant)

## ✨ Features

- **Lecture-based question answering:** Ask questions about MIT 6.0002 course concepts.
- **AI-generated explanations:** Get structured explanations, intuition, examples, and key takeaways.
- **Retrieval-Augmented Generation (RAG):** Retrieve relevant lecture chunks to provide context for AI responses.
- **Source references:** View the lecture and chunk associated with retrieved information.
- **Interactive web interface:** A React-based interface for asking questions and exploring previous questions.
- **Cloud deployment:** Frontend hosted on Vercel and backend hosted on Render.

## 🛠️ Tech Stack

| Component | Technologies |
|---|---|
| Frontend | React, JavaScript, Vite, CSS |
| Backend | Python, FastAPI |
| AI / LLM | Groq API |
| Retrieval | FAISS, Sentence Transformers |
| Embeddings | all-MiniLM-L6-v2 |
| Deployment | Vercel, Render |

## 🧠 How It Works

1. **Lecture processing:** Lecture videos are transcribed into text.
2. **Chunking:** Transcripts are split into smaller text sections.
3. **Retrieval:** Relevant lecture chunks are selected for a student's question.
4. **AI generation:** The retrieved context is sent to the Groq API.
5. **Response:** The application displays a structured answer with source references.

## 🏗️ Architecture

```text
Student Question
       ↓
React Frontend (Vercel)
       ↓
FastAPI Backend (Render)
       ↓
Lecture Chunk Retrieval
       ↓
Groq API + Retrieved Context
       ↓
Explanation, Example & Key Takeaway
```

## 🚀 Run Locally

### Prerequisites

- Python 3.10 or later
- Node.js and npm
- A Groq API key

### 1. Clone the repository

```bash
git clone https://github.com/krishnapalkhatik97-jpg/MIT-AI-Teaching-Assistant.git
cd MIT-AI-Teaching-Assistant
```

### 2. Set up the Python environment

```bash
python -m venv venv
```

Activate the environment on Windows:

```powershell
.\venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

Set the following variables in your local environment:

```text
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=openai/gpt-oss-20b
```

Never commit API keys or other secrets to GitHub.

### 4. Start the backend

From the repository root:

```bash
uvicorn backend.main:app --reload
```

The API runs locally at `http://127.0.0.1:8000`.

API documentation is available at `http://127.0.0.1:8000/docs`.

### 5. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite in your terminal.

## 📁 Project Structure

```text
MIT-AI-Teaching-Assistant/
├── backend/
│   ├── main.py
│   └── rag_api.py
├── data/
│   ├── faiss_index.index
│   └── metadata.pkl
├── frontend/
│   ├── src/
│   ├── index.html
│   └── package.json
├── scripts/
├── app.py
├── requirements.txt
└── README.md
```

## 🔐 Security

- Keep API keys in environment variables.
- Do not commit `.env` files or credentials.
- Use public deployment URLs for sharing the application.

## ⚠️ Notes

- The deployed backend uses a free hosting plan and may take longer to respond after inactivity.
- AI responses depend on the relevance of retrieved lecture content and the availability of the LLM API.

## 👨‍💻 Author

**Krishna Pal Khatik**

[GitHub Profile](https://github.com/krishnapalkhatik97-jpg)

---

If you find this project useful, consider starring the repository ⭐
