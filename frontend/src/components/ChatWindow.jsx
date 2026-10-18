import { useEffect, useRef } from "react";
import MessageBubble from "./MessageBubble";
import SuggestionCard from "./SuggestionCard";
import { Spark } from "./Icons";
import { SUGGESTIONS } from "./suggestions";

export default function ChatWindow({ messages, loading, onSuggest }) {
  const endRef = useRef(null);
  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, loading]);

  if (!messages.length && !loading) {
    return (
      <div className="scroll">
        <div className="empty">
          <span className="eyebrow">MIT 6.0002 · Intro to Computational Thinking</span>
          <h1>Learn MIT AI, <em>one question</em> at a time.</h1>
          <p className="lede">
            Ask questions about the MIT 6.0002 lectures and learn concepts through explanations, intuition and examples.
          </p>
          <div className="suggestions">
            {SUGGESTIONS.map((s, i) => <SuggestionCard key={s} index={i} text={s} onClick={onSuggest} />)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="scroll">
      <div className="thread">
        {messages.map((m) => <MessageBubble key={m.id} message={m} />)}
        {loading && (
          <div className="msg msg-ai">
            <div className="avatar"><Spark size={15} /></div>
            <div className="thinking">
              <span className="dots"><i /><i /><i /></span> Thinking...
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>
    </div>
  );
}

