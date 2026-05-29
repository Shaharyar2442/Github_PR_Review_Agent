# Code Review Agent - Version 2.0 Plan

## What this expansion does
We are upgrading our Code Review Agent from a local terminal script to a multi-tenant, cloud-hosted SaaS. This includes adding a sleek React frontend for human-in-the-loop approvals, integrating a VectorDB to give the agent full repository context, and deploying the entire system to free cloud providers as a registered GitHub App.

## V2.0 Tech Stack
| Tool | Why chosen | Free tier limits |
|---|---|---|
| Next.js | Modern React framework for building our interactive dashboard. | N/A (open source) |
| TailwindCSS | Utility-first CSS framework for rapid, beautiful glassmorphism styling. | N/A (open source) |
| ChromaDB | Lightweight, open-source vector database to store code embeddings for RAG. | N/A (open source) |
| Supabase | Serverless PostgreSQL database to persist LangGraph memory across cloud restarts. | 500MB database, 2 projects (free tier) |
| Render | Cloud platform to host our FastAPI python backend. | 1 free web service (spins down on inactivity) |
| Vercel | Cloud platform to host our Next.js frontend dashboard. | Generous free tier for hobbyists |

## Phases

### PHASE 7 — React Frontend Dashboard
* **Goal**: Build a Next.js application that lists pending reviews and allows you to approve or reject them visually.
* **Key concepts**: React components, Tailwind styling, FastAPI CORS, fetching state from LangGraph memory.
* **Done when**: You can view a dashboard of pending PRs and click a button to successfully resume the LangGraph workflow.

### PHASE 8 — VectorDB & RAG (Agentic Memory)
* **Goal**: Give the agent the ability to search the entire codebase, not just the PR diff.
* **Key concepts**: Retrieval-Augmented Generation (RAG), embeddings, Vector databases, new LangGraph tools.
* **Done when**: The agent autonomously queries ChromaDB to understand how a changed function affects other files.

### PHASE 9 — Cloud Deployment & GitHub App
* **Goal**: Register the project as a GitHub App and deploy it to the internet so anyone can use it.
* **Key concepts**: Multi-tenancy, GitHub App authentication, Postgres checkpointers, Cloud deployment.
* **Done when**: Your agent is running live on the internet, and a friend can install it on their repo!

## Current status
* **Phase**: Phase 7 — React Frontend Dashboard
* **Last completed step**: Approved V2.0 Implementation Plan.
* **Next step**: Scaffold the Next.js application in the `frontend` folder.
