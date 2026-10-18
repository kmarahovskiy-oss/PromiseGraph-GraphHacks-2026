# PromiseGraph — Before You Promise

**Graph Hacks 2026 · Track 01: Agents That Act on Connected Data**  
**New event-window implementation: October 18, 2026.** Concept and a separate early experimental checkpoint existed before the event; this version's implementation, source, UI and verification were produced during the official hackathon window. See `docs/PROVENANCE.md`.

> One bad product promise can appear in a product page, a quotation and an FAQ. PromiseGraph traces contradictory specifications to the exact SKU and revision and drafts all necessary corrections before the error becomes an expensive return.

## Submitted entry and judge links

**Submitted:** October 18, 2026, approximately 20:54 Kyiv time. The authenticated WeMakeDevs portal confirmed **SUBMITTED** for **PromiseGraph — Before You Promise**, solo entry, track **Agents That Act on Connected Data**. This records portal receipt, not judging approval or an award.

- [Working application](https://promisegraph-graphhacks-2026.onrender.com/)
- [YouTube demo — unlisted, accessible by link](https://www.youtube.com/watch?v=3_iHbNts5us)
- [Project article / AirPods side-prize entry](https://promisegraph-graphhacks-2026.onrender.com/article)
- [Product story](https://promisegraph-graphhacks-2026.onrender.com/story)
- [Verification workflow](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/verify.yml)

The entry includes separate repository, demo-video, live-deployment and blog fields. This repository contains the source, setup instructions, graph model, Cypher queries and test evidence; judges can inspect or run it locally.

## User pain & promised outcome

A merchandiser wants to publish a statement without spending an afternoon reconciling spec sheets. A sales person shouldn't have to discover that their quote contradicts an engineering drawing after delivery. Today the problem is fragmented across source documents, product variants, measurements, published claims and approval history. Keyword search cannot reliably trace *the exact* impacted promises or distinguish similar variants.

**Jobs to be done**

1. **One click:** select an exact variant and dimensions; the agent traces its evidence, checks units and returns a safe status.
2. **Try a new source without editing the graph:** paste a synthetic text excerpt with a documented limit, automatically extract its exact quotation and unit, compare its effects against graph-linked claims, then discard the preview.
3. **No made-up certainty:** 35 cm and 12 in (30.48 cm) are conflicting manufacturer claims. Never auto-pick the more convenient number.
4. **Counterfactual review:** before selecting the source, compare how each verified alternative would change the outcome and downstream correction workload. Neither possibility becomes truth automatically.
5. **No repeat manual work:** once a reviewer approves the engineering drawing, graph traversal locates every dependent claim and prepares exact replacement drafts.
6. **No cross-contamination:** Deep variant, older revision and different region remain separate.
7. **Remember why:** persist the source-of-truth decision and reviewer reason as graph nodes and edges, and retrieve them next time.
8. **Human control:** no autonomous publishing or external changes. A documentary PASS is *not* a physical-product guarantee.

## Fast reviewer journey (no separate test stand)

1. Open the live service, select **Scan all variants** to get a graph-backed risk queue across all sample SKUs and revisions.
2. Select the conflicted SKU and review two alternative source decisions and their exact downstream effects.
3. Even if a previous visitor approved a source, **Replay original source conflict** safely reconstructs the original alternatives in a read-only view without deleting decisions.
4. Choose a source based on the documentary evidence, record a reason, and inspect saved audit history. Every generated correction remains an editorial draft.
5. Switch to a different SKU and confirm it is unaffected. No customer data or private company infrastructure is used.

The portfolio scan is automated graph-tool orchestration, **not** a claim that a generative LLM is running. Shared demo decisions are visible to all visitors during the free-service process lifetime; users should never enter private documents or make real-business decisions with the demo.

## Real graph architecture

```
(Model)-[:HAS_VARIANT]->(Variant)-[:HAS_SPEC]->(Attribute)
                                             ^              ^
                                             |              |
                         (Evidence)-[:MEASURES]             [:DEPENDS_ON]-(Promise)
                            ^                                              ^
                       [:CONTAINS]                                     [:PUBLISHES]
                            |                                              |
                        (Document)                                    (Document)

(Decision)-[:SELECTS]->(Evidence)
(Decision)-[:RESOLVES]->(Attribute)
```

**Why FalkorDB is non-removable:** Every request loads exact variant attributes, follows `MEASURES` backwards to original source quotations and `DEPENDS_ON` backwards to every impacted promise using Cypher. Human decisions live in the graph and modify subsequent evaluations. The real application does not serve demo fixtures when graph connectivity fails (HTTP 503). Full queries: `promisegraph/queries.py`; adapter: `promisegraph/store.py`.

## Install & verify locally

Requirements: Python 3.12+; Docker/Compose; free local resources, no paid API key.

```bash
# Start the real FalkorDB database (binds Redis port ONLY to 127.0.0.1)
docker compose up -d falkordb

python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt

python -m pytest tests -q
# Open a terminal at the project root. Run ONE worker.
python -m uvicorn promisegraph.app:app --host 127.0.0.1 --port 8000 --workers 1
```

Navigate to `http://127.0.0.1:8000/`. FalkorDB Browser is also available at `http://127.0.0.1:3000` for inspecting paths. Loading the page connects to **real** FalkorDB and seeds only invented example data into the isolated graph named `promisegraph_contest_2026`.

Smoke test:

```bash
curl -f http://127.0.0.1:8000/api/health
curl -s http://127.0.0.1:8000/api/variants
curl -s -H 'Content-Type: application/json' -X POST http://127.0.0.1:8000/api/analyze \
  -d '{"id":"standard-r3","mattress":"30","topper":"4","unit":"cm"}'
```

Expected initially: `REVIEW_REQUIRED` — two contradictory documents, not an automatically accepted answer.

Review **engineering drawing, 12 in = 30.48 cm**, record a reason and explicitly approve. Expected: `FAIL`, exactly two unsafe dependent promises (product page and quotation); Support FAQ 28 cm stays safe. Inspect the Deep variant — it remains untouched. Refresh the page and inspect audit history — your reviewer decision remains in FalkorDB.

For the live integration verification, ensure `GET /api/health` says `source: real_graph`, test the review action end-to-end, and restart the service to check memory persistence. Do not use fake test doubles for a contest demo.

## Product story and decision value

[**Read the full illustrated project article**](https://promisegraph-graphhacks-2026.onrender.com/article) — the customer problem, graph modelling decisions, tests, technical limits and demonstration. This article is also in `docs/ARTICLE_FINAL.md`.

[**Explore the human-centred product story**](https://promisegraph-graphhacks-2026.onrender.com/story) — the problem, three workflows, the traceable FalkorDB decision, live workbench and real narrated video. The story is hosted by the same Render service, not a separate test site. All examples are synthetic and no financial benefits are invented.

## Screens & controls

- Single-screen interactive workbench: precise variant + dimensions, real graph status, source witness cards, impact radius, suggested drafts, reviewer approval, graph paths, persistent decisions.
- Copyable/downloadable JSON draft packet includes source evidence, impact and graph paths. **Never auto-publishes.**
- Genuine local graph is required. Separate unit/API tests use explicit doubles; they do not prove FalkorDB integration.

## Caveats and non-goals

- Dataset is 100% synthetic: fictional brand, sources, quotations, SKUs and documents. No UDF data or personal/customer information is used.
- The agent uses a *deterministic tool-directed decision loop* and a strict extractor for one documented source-statement format, not a generative LLM runtime. It makes decisions from connected graph state, discloses ambiguity, drafts safe edits and keeps graph memory. This limits claims about model inference.
- It evaluates *documented compatibility*, not experimentally measured product fit. There are no real claims of measured returns prevented, time saved or merchant adoption.
- Single local reviewer, one Uvicorn worker. No user auth, hardened concurrency, multitenant support, real storefront integration, invoice edits or unattended publication.
- **Verified:** GitHub Actions runs unit/API tests and real FalkorDB graph integration (Cypher, separate variant isolation, saved review decision through a new database connection), checks the JavaScript syntax and independently exercises the public Render URL, API health, portfolio triage and UI. A separate Playwright run recorded real browser interactions against FalkorDB and published the Google TTS-narrated video as a GitHub Release. [Verification workflow](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/verify.yml) · [Genuine demo workflow](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/live-demo.yml). Free Render's temporary filesystem must **not** be described as persistent across service restarts.

## Competition and disclosure

Built with significant assistance from ChatGPT. The original idea/preparation predates the Oct 15–18 hackathon; this source is the **new event-window implementation** (October 18). Any final entrant must review and be able to explain the graph schema, Cypher, code, testing and decisions; the organisers may reject blind AI-generated submissions. **The participant explicitly confirmed completing a technical review on October 18, 2026.** That is a participant report, not a third-party certification; the participant remains responsible for understanding and explaining the code and design.

Official rules: https://www.wemakedevs.org/hackathons/falkordb/rules

Only public or synthetic data are used; no paid tools or external service credentials are required. The later portal submission was completed on October 18; see the submission status and links above.

### Mandatory live graph smoke test (separate from local checks)

```bash
RUN_GRAPH_TESTS=1 python -m pytest tests/test_live_graph.py -v
```

The smoke test uses an isolated FalkorDB graph name; it exercises actual Cypher query paths, records a reviewer decision, checks separate variant isolation and creates a fresh DB connection to verify persisted memory. If it fails, the release gate remains blocked.

### Existing public one-service preview (non-durable Free tier)

The application can alternatively start the real embedded FalkorDBLite (`FALKORDB_MODE=embedded`, `pip install -r requirements-embedded.txt`) on a Linux host that permits Unix sockets. `render.yaml` documents the one-service Render Free deployment. The deployed preview has been verified through a separate GitHub Actions health / portfolio / UI check. **Do not confuse FalkorDBLite with an in-memory fake:** it runs a genuine FalkorDB graph engine. On Render Free the filesystem can disappear when the service sleeps or redeploys, so reviewer decisions are **not durable across that restart**; the standard local Docker build with a persistent volume is the reliable competition evidence for memory. The public application has been deployed at https://promisegraph-graphhacks-2026.onrender.com/.

## Submission and integrity status — 18 October 2026

The hackathon registration was completed by the participant before submission preparation, and on 18 October the participant confirmed that they had technically reviewed the implementation. The final entry form was submitted through the participant's authenticated WeMakeDevs account at approximately 20:54 Kyiv time. The portal displayed **SUBMITTED**, with the repository, unlisted YouTube demo, live application and article links saved. A GitHub publication alone would not have been a hackathon submission. See [the prepared submission details](docs/SUBMISSION_READY.md) and [the requirement-by-requirement checklist](docs/RULES_AUDIT_2026-10-18.md).
