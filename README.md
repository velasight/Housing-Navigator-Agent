# Housing Navigator Agent

This is the source code submission for the "Agent Development Kit Hackathon with Google Cloud".

**Live Demo URL:** https://affordablehousingagent.netlify.app/
---

## 1. Project Overview & Goal

The "Housing Navigator Agent" is a sophisticated, conversational AI proof of concept built on Google Cloud's Vertex AI platform. Its primary goal is to act as a helpful, 24/7 digital assistant for prospective homebuyers interacting with a housing authority. It aims to reduce friction in the application process, provide instant answers to common questions, and guide users toward their homeownership goals through a simple, intuitive chat interface.

### Core Capabilities:

* **Information Retrieval (RAG):** Answers user questions about housing policies, programs, and eligibility criteria by searching a knowledge base of provided documents.
* **Appointment Scheduling (Mock):** Allows users to schedule mock appointments with housing counselors.
* **Property Alerts (Mock):** Enables users to set up personalized alerts for properties that meet their criteria and fall within affordable housing program limits.
* **Affordability Estimation (Mock):** Provides users with a simplified, preliminary estimate of an affordable home price and potential monthly payments to help set realistic expectations.
* **Eligibility Check (Mock):** Guides users through a preliminary, non-binding eligibility check for assistance programs based on their specific inputs.

## 2. Google Cloud Architecture

The agent is built using a modern, serverless architecture that separates conversational logic from backend tasks.

* **Orchestration & NLU (The "Brain"):** A **Vertex AI Playbook** (built on Dialogflow CX) acts as the central command center, using a Gemini model to understand user intent, manage the conversation, and decide which tool to use.
* **Knowledge Base (RAG):** A **Vertex AI Search Data Store** provides the RAG capability, ingesting documents from a Google Cloud Storage bucket.
* **Custom Tools (Backend Logic):** Four distinct backend tools are built as serverless Python functions and deployed as individual **Google Cloud Run** services.
* **User Interface:** A **Dialogflow Messenger** integration provides a pre-built, secure, and customizable web chat widget hosted on a static web page.

**High-Level Flow:**
`User <--> Dialogflow Messenger UI <--> Dialogflow CX API (Playbook Agent) <--> [Vertex AI Search Data Store OR Google Cloud Run Tools]`

---

## Appendix A: Troubleshooting Guide - Challenges & Resolutions

This project involved navigating several real-world technical challenges.

1.  **Challenge: Agent Doesn't Answer Follow-up Questions**
    * **Symptom:** The agent would acknowledge an informational question but then provide no further response.
    * **Diagnosis:** The Playbook's LLM was executing a `respond` action and then waiting for new input, not immediately chaining the RAG tool call.
    * **Solution:** We refined the Playbook "Instructions" to be more explicit about the sequence of actions and created "Examples" (few-shot prompting) to teach the agent the desired conversational pattern.

2.  **Challenge: Cloud Function Fails to Deploy ("Missing Target")**
    * **Symptom:** Cloud Run services failed to start with a "container failed to start" error.
    * **Diagnosis:** Runtime logs showed a `functions_framework.exceptions.MissingTargetException`. The system didn't know which Python function to execute.
    * **Solution:** We explicitly defined the entry point by setting the **`GOOGLE_FUNCTION_TARGET`** environment variable in the Cloud Run service configuration to the exact name of the Python function.

3.  **Challenge: Data Store Linking Conflict (Search vs. Chat)**
    * **Symptom:** A `FAILED_PRECONDITION` error occurred when adding the RAG data store as a tool to the Playbook.
    * **Diagnosis:** The data store was created under a "Search" type application and could not be used by a "Chat" type agent (the Playbook).
    * **Solution:** We created a **new, separate data store** from *within* the Playbook's "Add tool" interface to ensure it was created in the correct context.

4.  **Challenge: Core IAM & Organization Policy Block (Support Required)**
    * **Symptom:** Despite being the `Organization Administrator` on a fully activated billing account, it was impossible to edit the "Domain Restricted Sharing" Organization Policy (the "Edit policy" button was greyed out). This prevented making Cloud Run services public, causing `403 Forbidden` errors.
    * **Diagnosis:** A fundamental, platform-level issue with the account's state where permissions were not being honored as documented.
    * **Solution:** The only path forward was to **contact Google Cloud Support**. After purchasing a plan and adding the necessary support roles, the issue was explained to the support team, who were able to resolve the backend permissions state.

---
