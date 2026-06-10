# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Student reviews of EE professors at CCNY's Grove School of Engineering, drawn from the website of Rate My Professors. 

This knowledge does not exist through official channels because the university only publishes faculty credentials and research interests. So knowledge of student assessments of grading style, exam difficulty, or whether a professor actually teaches well does not come through official channels. RMP allows students to find advice that normally only travels through word of mouth between students who know each other.


---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

The main sources for what I needed to find were on Discord, RMP, and Reddit in that order. Having Discord chats as a source was kind of unfeasible due to the general nature of how text conversations. Reddit proved to be very scarce for EE CCNY information, and for the threads that did exist, I did not really trust the source for information. RMP professor seemed to be the only reliable source in this matter.

| #  | Source                | Type | URL                                                    |
|----|-----------------------|------|--------------------------------------------------------|
| 1  | Andrii Golovin        | RMP  | https://www.ratemyprofessors.com/professor/1823726     |
| 2  | Joseph Barba          | RMP  | https://www.ratemyprofessors.com/professor/1937184     |
| 3  | Liubov Kreminska      | RMP  | https://www.ratemyprofessors.com/professor/2071926     |
| 4  | Nidal Khrais          | RMP  | https://www.ratemyprofessors.com/professor/802899      |
| 5  | Ping-Pei Ho           | RMP  | https://www.ratemyprofessors.com/professor/288006      |
| 6  | Julio Reyes           | RMP  | https://www.ratemyprofessors.com/professor/1199855     |
| 7  | M. Ümit Uyar          | RMP  | https://www.ratemyprofessors.com/professor/519308      |
| 8  | Ali Duale             | RMP  | https://www.ratemyprofessors.com/professor/1962765     |
| 9  | Yi Sun                | RMP  | https://www.ratemyprofessors.com/professor/288005      |
| 10 | Roger Dorsinville     | RMP  | https://www.ratemyprofessors.com/professor/287999      |
| 11 | Samah Saeed           | RMP  | https://www.ratemyprofessors.com/professor/2839499     |
| 12 | Alfredo Cano Martinez | RMP  | https://www.ratemyprofessors.com/professor/2132415     |
| 13 | Hakan Pekcan          | RMP  | https://www.ratemyprofessors.com/professor/2129998     |
| 14 | Sang-Woo Seo          | RMP  | https://www.ratemyprofessors.com/professor/1274141     |
| 15 | Bruce Kim             | RMP  | https://www.ratemyprofessors.com/professor/2005606     |
| 16 | Edward Baurin         | RMP  | https://www.ratemyprofessors.com/professor/1274143     |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

Chunked at the review level.

**Overlap:**

No overlap.

**Reasoning:**

Each RMP review is a self-contained unit of opinion from a single student about a single experience. This is the natural way to do it in my opinion, because any other way risks splitting a student's complaint from its respective context. No overlap is needed since chunks are not positionally related. No minimum length filter because even short reviews are valid.


---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:** 

all-MiniLM-L6-v2 via sentence-transformers

**Top-k:**

5

**Production tradeoff reflection:**

all-MiniLM-L6-v2 is fast and free but general-purpose. For real deployment, text-embedding-3-large would give better accuracy on informal student writing at the cost of API latency and money. 

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

```markdown
| # | Question                                  | Expected answer                            |
|---|-------------------------------------------|--------------------------------------------|
| 1 | Which EE professor is easiest to pass?    | Khrais or Pekcan named, citing high        |
|   |                                           | ratings and would-take-again               |
| 2 | Does Golovin curve grades?                | No — multiple reviews explicitly say       |
|   |                                           | he does not curve                          |
| 3 | Who gives the most partial credit?        | Barba — reviews note he is generous with   |
|   |                                           | partial credit for shown work              |
| 4 | What do students say about Barba's exams? | Exam-heavy grading, curves class average   |
|   |                                           | to 60,  drops lowest midterm               |
| 5 | Is Pekcan a good professor for circuits?  | Yes — reviews praise his clarity and       |
|   |                                           | helpfulness for ENGR204                    |
```

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1. Some professors have very few reviews, which will affect retrieval quality for those professors. Cannot really do anything about it, just a gap.

2. Some reviews are sarcastic or clearly jokes. For example, a sarcastic Barba review saying "Easiest class ever! Anyone who gets below an A+ needs to drop this major" might be treated as a genuine response by the LLM.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

     [Rate My Professors website]
          │
          ▼
    [ scrape_rmp.py ]
    cloudscraper → RMP GraphQL API
    → 16 raw .txt files saved to rmp_professor_files/
          │
          ▼
    [ ingest.py ]
    Parse reviews → extract Comment: blocks
    one chunk per review → data/chunks/chunks.json
          │
          ▼
    [ embed.py ]
    SentenceTransformer("all-MiniLM-L6-v2")
    → ChromaDB (persistent) → data/chroma_db/
    Collection: "unofficial_guide"
          │
          ▼
    [ retrieve.py ]
    Query → embed query → semantic search (k=5)
    → return top chunks + source filenames
          │
          ▼
    [ query.py ]
    Grounded generation via Groq llama-3.3-70b-versatile
    System prompt enforces: answer only from retrieved context
    → {"answer": str, "sources": list}
          │
          ▼
    [ app.py ]
    Gradio UI: text input → ask() → answer + sources displayed


---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 1 and 2:**

Claude Code. Input: Project context. Help brainstorm project approach and reason through various architectural decisions. Help write the planning.md in appropriate technical terms as well as make formatting and tedious sections easier to write (i.e describing architectural diagram and getting ASCII drawing)

**Milestone 3 — Ingestion and chunking:**

Claude Code. Input: Documents and Chunking Strategy sections. Produce ingest.py that extracts one Comment: block per review and saves to chunks.json. Verify by checking chunk count matches ~570 total reviews across all 16 files.

**Milestone 4 — Embedding and retrieval:**

Claude Code. Input: Retrieval Approach section + chunks.json. Produce embed.py and retrieve.py using all-MiniLM-L6-v2 and ChromaDB with source metadata. Verify by running test queries and confirming returned sources match expected professors.

**Milestone 5 — Generation and interface:**

Claude Code. Input: grounding requirements + Evaluation Plan. Produce query.py with grounded system prompt and app.py Gradio UI. Verify by running all 5 eval questions and confirming answers cite real source files and refuse out-of-scope questions.
