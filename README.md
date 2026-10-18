# PromiseGraph — Before You Promise

**Graph Hacks 2026 · Track 01: Agents That Act on Connected Data**  
**New event-window implementation: October 18, 2026.** Concept and a separate early experimental checkpoint existed before the event; this version's implementation, source, UI and verification were produced during the official hackathon window. See `docs/PROVENANCE.md`.

> One bad product promise can appear in a product page, a quotation and an FAQ. PromiseGraph traces contradictory specifications to the exact SKU and revision and drafts all necessary corrections before the error becomes an expensive return.

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
4. Choose a source based on the documentary evidence, record a reason, and inspect saved audit history. The **Review / revise source decision** control opens a deliberate new review even after a prior visitor selected a source; earlier decisions remain in the graph. Every generated correction remains an editorial draft.
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

## Screens & controls

- Single-screen interactive workbench: precise variant + dimensions, real graph status, source witness cards, impact radius, suggested drafts, reviewer approval, graph paths, persistent decisions.
- Copyable/downloadable JSON draft packet includes source evidence, impact and graph paths. **Never auto-publishes.**
- Genuine local graph is required. Separate unit/API tests use explicit doubles; they do not prove FalkorDB integration.

## Caveats and non-goals

- Dataset is 100% synthetic: fictional brand, sources, quotations, SKUs and documents. No UDF data or personal/customer information is used.
- The agent uses a *deterministic tool-directed decision loop* and a strict extractor for one documented source-statement format, not a generative LLM runtime. It makes decisions from connected graph state, discloses ambiguity, drafts safe edits and keeps graph memory. This limits claims about model inference.
- It evaluates *documented compatibility*, not experimentally measured product fit. There are no real claims of measured returns prevented, time saved or merchant adoption.
- Single local reviewer, one Uvicorn worker. No user auth, hardened concurrency, multitenant support, real storefront integration, invoice edits or unattended publication.
- A separate GitHub Actions run verified the real FalkorDB integration and recorded a Playwright browser demo with English narration against the real database. [Download the public demo video](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/releases/download/graphhacks-demo-2026/PromiseGraph_Real_Demo_Narrated.mp4). Render Free is a convenient preview but uses ephemeral local storage; it cannot establish cross-restart persistence.

## Live demo and independently inspectable evidence

- [Full narrated demo video (MP4)](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/releases/download/graphhacks-demo-2026/PromiseGraph_Real_Demo_Narrated.mp4) — 86-second browser recording against real FalkorDB.
- [Video recording workflow](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/live-demo.yml) — reproducible Playwright test and recorded artifact.
- [Real graph and API verification](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/verify.yml) — database-backed integration tests.
- [Project story / competition blog](docs/ARTICLE_FINAL.md) — explains the user's problem, one-click portfolio scan, evidence provenance, safety gates and tested limitations.

## Competition and disclosure

Built with significant assistance from ChatGPT. The original idea/preparation predates the Oct 15–18 hackathon; this source is the **new event-window implementation** (October 18). Any final entrant must review and be able to explain the graph schema, Cypher, code, testing and decisions; the organisers may reject blind AI-generated submissions. **Submitting this archive without meaningful participant technical review may not satisfy eligibility.**

Official rules: https://www.wemakedevs.org/hackathons/falkordb/rules

Only public or synthetic data are used; no paid tools or external service credentials are required. No submission was performed as part of creating this package.

### Mandatory live graph smoke test (separate from local checks)

```bash
RUN_GRAPH_TESTS=1 python -m pytest tests/test_live_graph.py -v
```

The smoke test is run in CI with genuine FalkorDB and an isolated graph name; it exercises actual Cypher query paths, records a reviewer decision, checks separate variant isolation and creates a fresh DB connection to verify persisted memory. If it fails, the release gate remains blocked.

### Optional one-service preview deployment — ephemeral storage

The application can alternatively start the real embedded FalkorDBLite (`FALKORDB_MODE=embedded`, `pip install -r requirements-embedded.txt`) on a Linux host that permits Unix sockets. `render.yaml` documents the one-service Render Free configuration; the deployed service has been launched and a public-readonly HTTP smoke check is included in GitHub Actions. **Do not confuse FalkorDBLite with an in-memory fake:** it runs a genuine FalkorDB graph engine. On Render Free the filesystem can disappear when the service sleeps or redeploys, so reviewer decisions are **not durable across that restart**; the standard local Docker build with a persistent volume is the reliable competition evidence for memory. The existing Render Free preview is available at https://promisegraph-graphhacks-2026.onrender.com; its UI and uptime should be checked independently.
