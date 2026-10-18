# Graph Hacks 2026 — final entry copy

**Status:** Prepared for participant review. This page is NOT proof that the submission form was sent.

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
- **Real FalkorDB narrated video:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/releases/download/graphhacks-demo-2026/PromiseGraph_Real_Demo_Narrated.mp4
- **Graph and test results:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/verify.yml
- **Video/real browser test:** https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/actions/workflows/live-demo.yml

## Participant-only field — review before submission
Complete truthfully in your own words:
- What user problem you chose and why.
- Which app decisions you reviewed or influenced.
- Whether you can explain the graph model, Cypher traversals and decision gate.
- Whether you reviewed the running demo and AI coding disclosure.

Do not claim that the participant wrote or independently validated code if they did not. Do not submit blindly generated work contrary to the competition rules.

## Human final gate
Open the application, watch the narrated video, understand the key flows, and submit using the registered WeMakeDevs account **before 18 October 2026, 21:29 Kyiv time**. This document is preparation, not an actual submission receipt.
