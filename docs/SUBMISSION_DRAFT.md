# Graph Hacks entry — copy only after release gates pass

**Name:** PromiseGraph — Before You Promise

**Track:** Agents That Act on Connected Data

**Tagline:** Stop bad product promises before they become returns.

**Description:**
PromiseGraph is a graph-powered product-claim verification agent. It finds contradictions in supplier documents for an *exact* SKU, revision and market; checks dimensions with exact unit arithmetic; traverses the graph to every dependent customer-facing claim; and prepares evidence-backed correction drafts. When sources disagree it deliberately stops and asks a reviewer to choose an authoritative document, saving the reason in FalkorDB for the next session. No unsupported assumption and no automatic publication. Demo data are synthetic.

**What makes the graph indispensable:**
A Variant connects to Attribute, Evidence, Documents and Promises through Cypher relationship traversals. The blast-radius search and persisted reviewer Decision are unavailable if FalkorDB is removed. The system fails closed, without an in-memory fixture fallback.

**Tech:** Python 3.12+, FastAPI, FalkorDB, Cypher, vanilla JavaScript, Docker Compose. AI coding assistance disclosed. Decision engine is deterministic and does not claim LLM runtime.

**Repo:** [ADD PUBLISHED EVENT-WINDOW REPO URL]

**Demo video:** [ADD REAL WORKING-DEMO VIDEO URL]

**Run:** Docker Compose + pip install -r requirements.txt + uvicorn. See README.

**Participant contribution & verification:** [HUMAN PARTICIPANT WRITES TRUE DETAILS OF OWN REVIEW AND DECISIONS; NEVER AUTO-FILL]
