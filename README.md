# Housing Navigator Agent

This is the source code submission for the "Agent Development Kit Hackathon with Google Cloud".

## Project Overview

The Housing Navigator Agent is a conversational AI built on Google Cloud's Vertex AI platform. It assists prospective homebuyers by answering questions about housing programs, checking preliminary eligibility, estimating affordability, setting property alerts, and scheduling mock appointments.

## Architecture

* **Agent Core:** Vertex AI Playbook (Dialogflow CX)
* **Knowledge Base:** Vertex AI Search (RAG)
* **Custom Tools:** 4 Python functions deployed on Google Cloud Run
* **Frontend:** Dialogflow Messenger hosted on a static web page.

## Files in this Repository

* `index.html`: The simple webpage that hosts the Dialogflow Messenger chat widget.
* `appointment_tool.py`: The backend logic for the mock appointment scheduler.
* `alert_tool.py`: The backend logic for the mock property alert tool.
* `affordability_tool.py`: The backend logic for the simplified affordability estimator.
* `eligibility_tool.py`: The backend logic for the preliminary eligibility checker.

## How to Demo

Please visit the live application URL: [Your Live Demo URL from Netlify/Firebase Here]