# InvestiLens 🔎📈

**AI-Powered Investor Intelligence Platform**

InvestiLens is a comprehensive, full-stack application designed to empower investors with AI-driven insights. By leveraging advanced Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs), InvestiLens processes complex financial documents, extracts critical data, and generates actionable intelligence and comprehensive reports.

---

## 🌟 Key Features

- **Document Analysis (RAG):** Upload and analyze financial documents (PDFs) to extract meaningful, context-aware insights.
- **AI-Generated Reports:** Automatically generate structured reports based on document context using powerful LLMs.
- **Company Workspaces:** Organize your research, documents, and generated insights into dedicated company workspaces.
- **Interactive Dashboards:** Visualize data and manage your workflow with a sleek, highly responsive React frontend.
- **Local LLM Support:** Privacy-first design supporting local AI model execution via Ollama.

## 🛠️ Tech Stack

### Frontend
- **Framework:** React 18 with Vite
- **Routing:** React Router v7
- **Styling & Animations:** Framer Motion, Vanilla CSS
- **Data Visualization:** Recharts
- **Icons:** Lucide React

### Backend
- **Framework:** FastAPI
- **AI / LLM Orchestration:** LangChain
- **Vector Database:** ChromaDB
- **Embeddings:** Sentence Transformers (HuggingFace)
- **Local Models:** Ollama
- **Document Processing:** PyMuPDF

---

## 📂 Project Structure

```text
InvestiLens/
├── backend/                  # FastAPI backend server
│   ├── app/
│   │   ├── api/              # API Endpoints
│   │   ├── core/             # Configuration and App settings
│   │   ├── llm/              # LLM logic & LangChain integrations
│   │   ├── models/           # Database Models
│   │   ├── rag/              # Retrieval-Augmented Generation logic
│   │   ├── schemas/          # Pydantic validation schemas
│   │   ├── services/         # Business logic
│   │   └── utils/            # Helper functions
│   ├── data/                 # Local data storage (ChromaDB, Docs)
│   └── requirements.txt      # Python dependencies
└── frontend/                 # React frontend application
    ├── src/
    │   ├── components/       # Reusable UI components
    │   ├── pages/            # Application routes (Dashboard, Workspace, Report)
    │   └── App.jsx           # Main React component
    ├── package.json          # Node dependencies
    └── vite.config.js        # Vite configuration
```

---

## 🚀 Getting Started

### Prerequisites

Ensure you have the following installed on your system:
- **Node.js** (v18 or higher)
- **Python** (v3.10 or higher)
- **Ollama** (for running local AI models)

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/InvestiLens.git
cd InvestiLens
```

### 2. Backend Setup

Open a terminal and navigate to the backend directory:

```bash
cd backend

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your specific configurations if needed

# Run the backend development server
python -m uvicorn app.main:app --reload --port 8000
```
*The backend API will be available at `http://localhost:8000`. Interactive API documentation can be accessed at `http://localhost:8000/docs`.*

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# Install dependencies
npm install

# Start the frontend development server
npm run dev
```
*The frontend application will be available at `http://localhost:5173`.*

### 4. Setting up Local LLM (Ollama)
Ensure you have Ollama installed and running in the background. Pull the required models as specified in your configuration (for example, `llama3`):
```bash
ollama pull llama3
```

---

## 💡 Usage

1. Open the frontend application in your browser.
2. Create a new **Company Workspace** from the dashboard.
3. Upload financial documents (PDFs) into the workspace.
4. The system will automatically process and embed the documents using ChromaDB and HuggingFace.
5. Generate intelligence reports, ask conversational questions about the documents, and explore AI-generated insights.

---

## 📄 License

This project is licensed under the MIT License.
