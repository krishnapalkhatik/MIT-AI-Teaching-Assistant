
import streamlit as st
from scripts import rag

st.set_page_config(
    page_title="MIT AI Teaching Assistant",
    page_icon="🎓",
    layout="centered",
)

st.title("🎓 MIT AI Teaching Assistant")
st.caption("Your personal tutor, powered by MIT 6.0002 lectures.")

with st.sidebar:
    st.header("About")
    st.write("Ask questions and explore concepts from the MIT lecture collection.")

    if st.button("Clear chat"):
        st.session_state.messages = []
        st.session_state.rag_history = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "rag_history" not in st.session_state:
    st.session_state.rag_history = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        for source in message.get("sources", []):
            st.caption(
                f"Source: {source['lecture']} · Chunk {source['chunk_id']}"
            )

query = st.chat_input("Ask a question about your MIT lectures...")

if query:
    st.session_state.messages.append(
        {"role": "user", "content": query}
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching lectures and preparing your answer..."):
            rag.conversation_history = st.session_state.rag_history
            answer, sources = rag.ask_question(query)

            st.markdown(answer)

            if sources:
                with st.expander("📚 Retrieved lecture sources"):
                    for source in sources:
                        st.markdown(
                            f"**{source['lecture']}** · "
                            f"Chunk {source['chunk_id']}"
                        )
                        st.write(source["text"][:500])

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
    })
    st.session_state.rag_history = rag.conversation_history.copy()
