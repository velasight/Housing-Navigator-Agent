Addendum: High-Level Guide for Microsoft Azure Implementation
Objective: To outline how a system similar to the "Housing Navigator Agent" could be built using the Microsoft Azure ecosystem.

Architectural Component Mapping:

The core capabilities can be mapped from Google Cloud services to their Azure counterparts:

Functionality	Google Cloud (GCP) Service	Microsoft Azure Equivalent	Description
Document Storage	Google Cloud Storage (GCS)	Azure Blob Storage	Used to store the source PDF and text documents for the knowledge base.
RAG/Knowledge Base	Vertex AI Search Data Store	Azure AI Search	Ingests, chunks, and indexes documents from Blob Storage. Its "Skillsets" feature can call an embedding model, and it supports vector search. This is the heart of the RAG system.
LLM & Embeddings	Gemini (via Vertex AI)	Azure OpenAI Service	Provides the GPT-4 (for reasoning/generation) and Ada/embedding models (for vectorization). This is the "brain" of the agent.
Agent Orchestration	Vertex AI Playbook / Dialogflow CX	Azure Bot Service + Bot Code	The Bot Service provides the framework and channels. The core orchestration logic (deciding when to use RAG vs. a tool) would be written in code (e.g., C#, Python) using a framework.
Orchestration Framework	(Built into Playbook)	Semantic Kernel / LangChain	These open-source SDKs are commonly used within an Azure Bot to structure the interactions between the Bot Service, Azure OpenAI (for planning), Azure AI Search (for RAG), and Azure Functions (for tools).
Custom Tools	Google Cloud Run	Azure Functions	Serverless, HTTP-triggered functions written in Python, C#, etc., to execute specific business logic (e.g., the affordability estimator, eligibility checker).
