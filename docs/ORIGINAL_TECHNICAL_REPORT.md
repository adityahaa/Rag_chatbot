# PDF RAG chatbot technical report

## Problem and pipeline

The application answers document questions with an inspectable retrieved context. Streamlit coordinates local pdfplumber extraction, recursive character splitting (1,000 characters, overlap 200), Google embeddings, persistent Chroma indexing, similarity retrieval, and direct Gemini prompt invocation. Default k is 3 and UI temperature is 0.2. Chunk labels identify retrieved positions, not verified document citations.

## Data and experimental setup

Users provide PDFs. No bundled corpus, labeled question set, baseline run, or measured result exists. Extraction supports machine-readable text; scanned inputs need an OCR stage that is not implemented. Conversation history is visual session state and is not included in model prompts. Metadata dictionaries constructed in the UI are not passed to store_embeddings, limiting source traceability.

## Evaluation methodology

A future evaluation should use public/synthetic PDFs with answer spans and unanswerable questions. Record document hashes, model/package versions, chunk boundaries, k, and prompt. Measure retrieval Recall@k against labeled spans, answer correctness, source attribution, and abstention on unanswerable items. Compare vector retrieval with keyword retrieval and context-free generation on the same questions. These comparisons are proposed, not executed; no accuracy values are asserted.

## Reproduction blockers and limitations

Follow the root README for the intended launch. The legacy langchain.text_splitter import has been replaced with langchain_text_splitters and its direct requirement. Unpinned packages still make complete installation compatibility uncertain. The archived experimental Gemini generation ID and embedding ID need provider validation. API configuration is process-wide; persistence is shared and is not isolated by user. Failed document processing can leave temporary files. Prompt instructions do not enforce groundedness or prevent prompt injection. Use approved public/synthetic content only. See [verification record](VERIFICATION.md) for executed checks; no live provider answer was generated in this review.
