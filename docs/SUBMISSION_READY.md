# Graph Hacks 2026 — final entry copy

**Status:** Submitted on October 18, 2026 at approximately 20:54 Kyiv time, before the 21:29 Kyiv deadline. The authenticated WeMakeDevs portal displayed **SUBMITTED** for the solo entry **PromiseGraph — Before You Promise**. The saved entry contains the chosen track and all four links below. Portal receipt is not a judging decision or award.

## Project name
PromiseGraph — Before You Promise

## Track
Agents That Act on Connected Data (iPhone 18 Pro track)

## One-line pitch
Stop unsupported product promises before they become customer complaints, returns, and costly rework.

## Short description (under 100 words)
PromiseGraph is an evidence-first, graph-powered claim verification agent. It automatically scans product variants for conflicting supplier specifications, traces exact SKU/revision relationships in FalkorDB, compares downstream consequences, and prepares safe correction drafts for affected product pages and quotations. When sources disagree, the agent pauses for documented human review instead of inventing an answer. Reviewer decisions, reasons and affected claims are connected in FalkorDB. The demo uses synthetic data, and all changes remain drafts until approved.

## Extended description
Product information often contradicts itself: a supplier catalogue says one thing, an engineering drawing says another, and the online store or sales quotation repeats a promise that cannot be supported by both. Manually reconciling those documents and locating every affected customer-facing statement is slow and error-prone.

PromiseGraph tackles this connected-data problem. Its one-click catalogue triage finds review priorities across all product variants. For a selected product and customer request, the agent follows FalkorDB Cypher relationships from exact SKU and revision to evidence, attributes and the documents that publish dependent claims. Decimal unit checks keep 12 inches distinct from 35 centimetres. If sources disagree, two hypothetical outcomes are shown side by side, without pretending either source is correct. A human can select the authoritative source and save the reason in the graph. The agent then drafts corrections only for unsupported connected promises, leaving unrelated product variants and supported documents untouched.

The judge demo shows an invented 35 cm catalogue versus a 12 in / 30.48 cm engineering drawing for a 34 cm mattress + topper. Selecting the drawing flags two downstream promises while the 28 cm FAQ and a separate product variant remain valid. A read-only replay shows the conflict without deleting previous decisions.

No website is automatically edited. There is no generative LLM inference at runtime: this is a bounded deterministic graph-directed agent, and source text previews accept a documented statement format. The public Render Free service has ephemeral storage, so durable memory across hosting restarts is only demonstrated through the separate real FalkorDB integration test. All example data are fictional. Development used ChatGPT AI coding assistance and is disclosed.

## Why FalkorDB is load-bearing
Graph model:
- Model -HAS_VARIANT-> Variant -HAS_SPEC-> Attribute
- Document -CONTAINS-> Evidence -MEASURES-> Attribute
- Document -PUBLISHES-> Promise -DEPENDS_ON-> Attribute
- Decision -SELECTS-> Evidence
- Decision -RESOLVES-> Attribute

Cypher traverses those edges to find precise evidence, affected customer promises, and stored reviewer history. Removing FalkorDB removes core analysis; there is no in-memory JSON substitute in live endpoints.

## Links
- **Source:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026
- **Working application:** https://promisegraph-graphhacks-2026.onrender.com/
- **Product story:** https://promisegraph-graphhacks-2026.onrender.com/story
- **Article:** https://promisegraph-graphhacks-2026.onrender.com/article
- **YouTube demo (unlisted; submitted video link):** https://www.youtube.com/watch?v=3_iHbNts5us
- **Backup real FalkorDB narrated MP4:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/releases/download/graphhacks-demo-2026/PromiseGraph_Real_Demo_Narrated.mp4
- **Graph and test results:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/verify.yml
- **Video/real browser test:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/live-demo.yml

## Participant review and contribution — factual statement

On October 18, the participant confirmed technical review of the project. The participant directed the project toward reducing manual reconciliation work, avoiding unsupported customer promises, and improving the user experience, test reliability, graph dependence, scenario replay and presentation. They reviewed the narrated demo voice and requested the improved Google TTS edition. Implementation used extensive ChatGPT assistance, which is disclosed. This is a statement of the participant's reported review and directions, not a claim that they personally wrote every line of source code.

## Submission confirmation
The participant authorised submission and confirmed technical review. After publication of the demo on YouTube, the final form was submitted and its **SUBMITTED** view was checked. The saved repository, YouTube demo, live deployment, article and **Agents That Act on Connected Data** track matched this package. The authenticated receipt is available at https://www.wemakedevs.org/hackathons/falkordb/submit for the submitting account; that URL is account-specific, not a public project detail page.
