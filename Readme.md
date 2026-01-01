# 🔬 Smart Research Assistant: Multimodal RAG Engine

An AI-powered document intelligence platform that goes beyond text. This system uses **Google Gemini 1.5 Pro** to analyze complex PDFs containing **nested tables, financial charts, and technical diagrams** through a visual-first Retrieval-Augmented Generation (RAG) pipeline.

## 🌟 Key Features
* **Multimodal Reasoning:** Uses Computer Vision to "see" page layouts, ensuring that charts and tables—which usually break in standard text-based RAG—are interpreted accurately.
* **Flash-to-Pro Pipeline:** Optimized for cost and performance. **Gemini 2.5 Flash** handles high-volume page indexing, while **Gemini 2.5 Flash** handles complex query reasoning.
* **Vectorized Visual Context:** Implements **ChromaDB** to store and retrieve high-dimensional embeddings of page summaries.
* **Interactive Citations:** Displays the exact page image used as a reference for every AI-generated answer to eliminate hallucinations.
* **Fully Responsive UI:** A modern, mobile-friendly dashboard built with Streamlit and custom CSS glassmorphism.

## 🏗️ System Architecture
1.  **Ingestion:** PDF pages are converted into high-resolution images using `PyMuPDF`.
2.  **Indexing:** Gemini 2.5 Flash generates detailed descriptions for every page (extracting data from charts/tables).
3.  **Storage:** These summaries are stored in a **ChromaDB** vector database.
4.  **Retrieval:** When a user asks a question, the system retrieves the most relevant page images based on semantic similarity.
5.  **Reasoning:** The retrieved images + the user query are sent to Gemini 2.5 Flash for final multimodal synthesis.

## 🛠️ Tech Stack
* **LLM:** Google Gemini 2.5 Pro & Flash (via Google AI Studio API)
* **Vector DB:** ChromaDB
* **Frontend:** Streamlit (Custom CSS)
* **PDF Engine:** PyMuPDF (fitz)
* **Language:** Python 3.10+

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone [https://github.com/Rancidgift57/Smart-Research-Assistant-RAG](https://github.com/Rancidgift57/Smart-Research-Assistant-RAG)

cd smart-research-assistant
```

## Contributing
Contributions are welcome! To contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature-name`).
3. Make your changes and commit (`git commit -m "Add feature-name"`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request with a detailed description of your changes.

Please ensure your code follows the project's coding style and includes appropriate tests.

**Contact:**
Email: nnair7598@gmail.com

**Thank You**
