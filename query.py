import os
from dotenv import load_dotenv
from groq import Groq
from retrieve import retrieve

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL = "llama-3.3-70b-versatile"

SYSTEM_PROMPT = (
    "You are a helpful assistant for CCNY EE students. "
    "Answer questions ONLY using the review excerpts provided. "
    "Do not use any outside knowledge. "
    "If the provided excerpts do not contain enough information to answer the question, "
    "say exactly: 'I don't have enough information in the reviews to answer that.' "
    "Always cite which source file(s) your answer draws from."
)


def ask(question):
    chunks = retrieve(question)

    context_blocks = "\n\n".join(
        f"Source: {c['source']}\n{c['text']}" for c in chunks
    )
    user_message = f"{context_blocks}\n\nQuestion: {question}"

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    answer = response.choices[0].message.content
    sources = list(dict.fromkeys(c["source"] for c in chunks))
    return {"answer": answer, "sources": sources}


TEST_QUERIES = [
    "Which EE professor is easiest to pass?",
    "What do students say about Barba's exams?",
    "What is the best restaurant near CCNY?",
]

if __name__ == "__main__":
    for question in TEST_QUERIES:
        result = ask(question)
        print(f"Q: {question}")
        print(f"Answer: {result['answer']}")
        print(f"Sources: {result['sources']}")
        print()
