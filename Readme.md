# ■ FlowOpsAI
**FlowOpsAI** is an **AI + MLOps SaaS orchestration framework** designed to unify **LLMs,
custom ML models, and AI agents** into one seamless platform.
Whether you’re building AI-powered workflows, deploying custom models, or gaining insights from
metrics — FlowOpsAI provides a **production-ready foundation**.
---
## ■ Features
■ **Model Orchestration** – Train, evaluate, and manage custom ML models
■ **LLM Integrations** – Plug-and-play with **OpenAI, Gemini, Anthropic, Mistral, and OSS LLMs**
■ **AI Agents** – Build and run workflow-aware AI agents for automation
■ **Observability** – Logging, metrics, and insights out of the box
■ **Containerized** – Ready for **Docker & Docker Compose** deployment
■ **UI Dashboard** – Interactive frontend for monitoring and managing everything
---
## ■ Project Structure
flowopsai/
■■■ backend/ # FastAPI/Flask backend (API + Trainer + Orchestration logic)
■■■ frontend/ # React-based dashboard (UI to manage workflows/agents/models)
■■■ docker-compose.yml # Multi-service stack definition
■■■ .env # Environment variables (API keys, DB configs, ports)
■■■ README.md # Project documentation
---
## ■ Quick Start
1■■ **Clone the repository**
git clone https://github.com//flowopsai.git
cd flowopsai
2■■ **Set up environment**
cp .env.example .env
# Edit `.env` with your API keys & database config
3■■ **Start the stack**
docker-compose up --build -d
4■■ **Access services**
- ■ **Frontend UI** → http://localhost:3737
- ■■ **Backend API** → http://localhost:8181
- ■ **Agents API** → http://localhost:8052
- ■ **Trainer Service** → http://localhost:8090
---
## ■■ Architecture
Frontend → Backend → Agents/Trainer → Database
---
## ■■ Configuration
Update your `.env` file with the following keys:
# Ports
TRAINER_PORT=8090
FLOWOPSAI_SERVER_PORT=8181
FLOWOPSAI_AGENTS_PORT=8052
FLOWOPSAI_UI_PORT=3737
# Database
POSTGRES_USER=flowopsai
POSTGRES_PASSWORD=supersecretpassword
POSTGRES_DB=flowopsai_db
# API Keys
OPENAI_API_KEY=your-openai-key
GEMINI_API_KEY=your-gemini-key
ANTHROPIC_API_KEY=your-anthropic-key
---
## ■■ Tech Stack
- **Frontend** → React + Vite (UI dashboard)
- **Backend** → FastAPI/Flask (REST API + orchestration)
- **Agents** → Python AI Agents (workflows, automation)
- **Trainer** → Model training & evaluation service
- **Database** → PostgreSQL (persistent storage)
- **Infra** → Docker + Docker Compose
---
## ■ License
This project is licensed under the **MIT License**.
See the LICENSE file for details.