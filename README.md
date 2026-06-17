# 🏦 Autonomous Agentic Compliance Auditor

An intelligent multi-agent system built with **LangGraph** to automate market research, investment strategy formulation, and regulatory compliance auditing.

## 🏗️ System Architecture
The system utilizes a directed acyclic graph (DAG) structure to ensure modularity and auditability.

```mermaid
graph TD
    A[User Input: Streamlit UI] --> B{LangGraph Orchestrator}
    B --> C[Macro Intelligence Agent]
    C -->|Fetch| D[Tavily Search Tool]
    D -->|Raw Data| C
    C -->|Structured Macro Data| E[Market Strategy Agent]
    E -->|JSON Strategy| F[Confidence Scoring Agent]
    F -->|Internal Log| G{Interrupt/Breakpoint}
    G -->|Human Review| H[Auditor Agent]
    H -->|Policy Check| I[Final Decision: Approve/Reject]
    I -->|Audit Report| A
