const API_BASE = "https://mit-ai-teaching-assistant.onrender.com";
export async function askQuestion(question) {
  const response = await fetch(`${API_BASE}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question: question.trim(),
    }),
  });

  if (!response.ok) {
    throw new Error(`Backend error: ${response.status}`);
  }

  const data = await response.json();

  if (data.error) {
    throw new Error(data.error);
  }

  return {
    explanation: data.explanation || "",
    intuition: data.intuition || "",
    example: data.example || "",
    takeaway: data.takeaway || "",
    sources: (data.sources || []).map((source) => ({
      name: source.lecture,
      chunk: source.chunk_id,
      distance: source.distance,
    })),
  };
}