# gemini-document-qa-system
An intelligent document-based question answering system powered by Google Gemini API. Upload documents, ask questions, and get precise answers with source citations.

# Gemini Document QA System

An intelligent document-based question answering system powered by Google Gemini API. Upload documents, ask questions, and get precise answers with source citations.

## 🚀 Features

- **Smart Document Processing** - Supports PDF, TXT, and DOCX files
- **AI-Powered Search** - Uses Gemini embeddings for semantic retrieval
- **Accurate Answers** - Get contextual responses with source references
- **Modern UI** - Clean and responsive web interface
- **Fast Retrieval** - Vector-based similarity search with FAISS

## 🛠️ Tech Stack

- **AI Model**: Google Gemini Pro API
- **Backend**: Python, FastAPI
- **Embeddings**: Gemini Embeddings + FAISS
- **Frontend**: HTML/CSS/JavaScript
- **Document Processing**: PyPDF2, python-docx

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Gemini API key

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/gemini-document-qa-system.git
cd gemini-document-qa-system

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Add your GEMINI_API_KEY to .env file
```

### Usage

```bash
# Start the server
python app.py

# Open browser
http://localhost:8000
```

1. Upload your documents (PDF/TXT/DOCX)
2. Ask questions about the content
3. Get AI-generated answers with sources

## 📁 Project Structure

```
├── app.py
├── docs/                  # contains .txt files
├── templates/
│   ├── index.html
└── requirements.txt

```

## 🔧 Configuration

Create `.env` file:
```env
GEMINI_API_KEY=your_api_key_here
MAX_FILE_SIZE=10MB
EMBEDDING_MODEL=models/embedding-001
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/new-feature`)
3. Commit changes (`git commit -am 'Add new feature'`)
4. Push to branch (`git push origin feature/new-feature`)
5. Open Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Google Gemini API for AI capabilities
- FAISS for efficient vector search
- FastAPI for robust backend framework