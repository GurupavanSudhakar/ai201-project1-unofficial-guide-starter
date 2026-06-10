# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Student reviews of EE professors at CCNY's Grove School of Engineering, drawn from the website of Rate My Professors. 

This knowledge does not exist through official channels because the university only publishes faculty credentials and research interests. So knowledge of student assessments of grading style, exam difficulty, or whether a professor actually teaches well does not come through official channels. RMP allows students to find advice that normally only travels through word of mouth between students who know each other.


---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

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

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

**Chunk size:**

One review per chunk, not length-based. Each `Comment:` block in the raw .txt files is extracted as a single chunk, regardless of length. This preserves the natural unit of the data (one experience).

**Overlap:**

None, because each review is independent of another one. Overlap would only make sense if a single piece of information could span two adjacent chunks, which isn't the case here.

**Why these choices fit your documents:**

Each RMP review is a self-contained unit of opinion from a single student about a single professor. Splitting a review mid-sentence would risk detaching a complaint or compliment from its context

**Final chunk count:**

588 chunks across 16 files.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:**

all-MiniLM-L6-v2 via sentence-transformers


**Production tradeoff reflection:**

all-MiniLM-L6-v2 is fast and free but general-purpose. For real deployment, text-embedding-3-large would give better accuracy on informal student writing at the cost of API latency and money. 

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

The system prompt passed to `llama-3.3-70b-versatile` via Groq is:

> "You are a helpful assistant for CCNY EE students. Answer questions ONLY using the review excerpts provided. Do not use any outside knowledge. If the provided excerpts do not contain enough information to answer the question, say exactly: 'I don't have enough information in the reviews to answer that.' Always cite which source file(s) your answer draws from."

The out-of-scope test confirmed this works: asking "What is the best restaurant near CCNY?" returned the exact refusal phrase even though ChromaDB still returned chunks (the LLM correctly recognized none of them were relevant to the question).


**How source attribution is surfaced in the response:**

Source attribution is built programmatically in `query.py` before the LLM call, not inferred from the LLM's output. 

After `retrieve()` returns the top-k chunks, the sources list is constructed as `list(dict.fromkeys(c["source"] for c in chunks))`, unique filenames in retrieval order. The LLM is not trusted to decide which sources it drew from; the pipeline tracks that independently and surfaces it as a separate field in the response dict: `{"answer": str, "sources": list}`.

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Which EE professor is easiest to pass? | Khrais or Pekcan named, citing high ratings and would-take-again | Named Uyar and Sun as top candidates with supporting quotes; Pekcan appeared in retrieved sources but wasn't the primary answer | Relevant | Partially accurate — Uyar is defensible but Pekcan/Khrais were expected |
| 2 | Does Golovin curve grades? | No — multiple reviews explicitly say he does not curve | Correctly answered no, quoted review directly: "he will not curve" | Relevant | Accurate |
| 3 | Who gives the most partial credit? | Barba — reviews note he is generous with partial credit for shown work | Named Barba from top result; also mentioned Kreminska gives good partial credit | Partially relevant | Partially accurate — Barba identified but answer was less decisive than expected |
| 4 | What do students say about Barba's exams? | Exam-heavy grading, curves class average, drops lowest midterm | Summarized as hard exams with a curve and generous partial credit for shown work; matched review content well | Relevant | Accurate |
| 5 | Is Pekcan a good professor for circuits? | Yes — reviews praise his clarity and helpfulness for ENGR204 | Yes — all 8 retrieved chunks from hakan_pekcan.txt, praised teaching style, easy grading, and project-based midterm | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:**

"Who gives the most partial credit?" and any query containing the words "who", "how", "homework", "those", or "show".

**What the system returned:**

Results restricted entirely to `ping-pei_ho.txt`, so the LLM answered about Professor Ho even though the question had nothing to do with him. 

For the partial credit question specifically, it returned Ho's reviews about deducting points from lab reports, the opposite of what was asked.

**Root cause (tied to a specific pipeline stage):**

The bug was in the retrieval stage, in `retrieve.py`. The professor name detection used a plain substring check: `if last_name in query_lower`. The key `"ho"` in the `PROFESSOR_MAP` is only two letters, and those two letters appear inside dozens of common English words. 

`"ho"` is a substring of `"who"`, `"how"`, `"homework"`, `"those"`, `"show"`, and others. So the filter fired incorrectly on those queries, and ChromaDB was told to restrict its search to only `ping-pei_ho.txt`, about 40 chunks out of 588, before semantic search even ran. The LLM then had no choice but to answer from that restricted pool.

**What you would change to fix it:**

Replace the substring check with a word-boundary regex: `re.search(r'\b' + re.escape(last_name) + r'\b', query_lower)`. The `\b` anchors require non-word characters (spaces, punctuation, or start/end of string) on both sides of the match, so `"who"` no longer triggers it but a query explicitly saying "Ho" or "Professor Ho" still does. This fix was applied and confirmed working.

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The architecture diagram in planning.md gave a clear stage-by-stage breakdown, scrape → ingest → embed → retrieve → generate → UI, that mapped directly to individual Python files. 

This made it possible to direct Claude Code at exactly one stage at a time, handing it only the relevant section of the spec as context. Without that structure, prompting an AI tool to "build a RAG system" would have produced something much harder to verify or debug, because there would be no agreed-upon breakdown of what each file was supposed to do.

**One way your implementation diverged from the spec, and why:**

The spec described pure semantic search with top-k=8 and made no mention of professor name detection. That filter was added during implementation after observing that professor-specific queries like "Does Golovin curve?" were returning chunks from other professors alongside the relevant ones. 

The fix was to detect a professor's last name in the query and restrict ChromaDB to that professor's source file before running semantic search. This wasn't in the spec because it only became an obvious need once the system was running and returning real results.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* 

A sample of the raw `.txt` file format showing the `Review #N` header and `Comment:` block structure, plus the Chunking Strategy section from planning.md specifying one-review-per-chunk with no overlap.

- *What it produced:* 

`ingest.py`: splits on `^Review #\d+` regex, extracts `Comment:` blocks including multi-line ones, cleans HTML entities via `html.unescape()`, collapses whitespace, and outputs `chunks.json` with `chunk_id`, `source`, and `text` fields.

- *What I changed or overrode:* 

Added a `professor` field to each chunk (extracted from the `Professor:` header line at the top of each file). The original spec only included `chunk_id` and `source`, but having the professor name as explicit metadata made downstream filtering cleaner without having to parse filenames.

**Instance 2**

- *What I gave the AI:* 

The `PROFESSOR_MAP` dictionary mapping last names to filenames, and a description of the desired behavior: if the query mentions a professor's last name, restrict the ChromaDB search to only that professor's source file.

- *What it produced:* 

The detection logic using a plain `if last_name in query_lower` substring check inside `retrieve()`.

- *What I changed or overrode:* 

Had to override the detection logic after discovering it was causing "who", "how", and "homework" to silently filter every query to `ping-pei_ho.txt`. Replaced the substring check with `re.search(r'\b' + re.escape(last_name) + r'\b', query_lower)` to require whole-word matches only.
