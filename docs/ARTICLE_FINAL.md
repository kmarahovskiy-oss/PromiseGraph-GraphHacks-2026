# One Wrong Measurement, Three Wrong Promises
*How we built PromiseGraph, an evidence-first decision agent using FalkorDB — Graph Hacks 2026*

Picture a shopper choosing a mattress-and-topper combination for a particular bed. The product page says it fits. A sales quotation repeats the same claim. A support FAQ seems to agree. Then a technical drawing reveals a different maximum height.

An ordinary search engine can find both documents. It cannot reliably answer the difficult question: **which exact product variation does each document describe, and how many customer promises depend on it?**

That is the pain PromiseGraph addresses: the time spent reconciling fragmented documents, and the risk of issuing a confident but unsupported answer.

## The demo in one minute

Our invented product, AstraRest Standard R3, has two source documents:
- Supplier catalogue: maximum combined height **35 cm**.
- Engineering drawing: maximum combined height **12 inches**, precisely **30.48 cm**.

A 30 cm mattress plus a 4 cm topper totals 34 cm. Under the catalogue it appears acceptable; under the drawing it is not. A product page and a quotation both promise that it fits. A support FAQ mentions 28 cm, which remains supported either way. A different model, AstraRest Deep R3, permits 40 cm.

The interesting part isn't the arithmetic. It is **who should be trusted, what changes after that decision, and what must remain untouched.**

PromiseGraph first shows both possible interpretations and their downstream effects. It does not silently choose the friendliest number. A reviewer then selects the authoritative source and records the reason. In our scripted synthetic example, that is the engineering drawing. Once approved, the agent follows graph edges and prepares correction drafts for the two unsupported statements, retaining the valid FAQ and leaving the different model alone.

No website is silently rewritten, and a documentary compatibility check is never presented as a physical safety or fit guarantee.

## Why FalkorDB is essential

The graph's nodes and edges encode meaning, not just presentation:

```text
Model -HAS_VARIANT-> Variant -HAS_SPEC-> Attribute
Document -CONTAINS-> Evidence -MEASURES-> Attribute
Document -PUBLISHES-> Promise -DEPENDS_ON-> Attribute
Decision -SELECTS-> Evidence
Decision -RESOLVES-> Attribute
```

An exact SKU, revision and region identifies the attribute. Source quotations belong to evidence nodes, which link back to their original documents. Published promises depend on the same attribute. A reviewer decision records which evidence was selected and why.

Cypher queries traverse these relationships to find the relevant source witnesses and the downstream claims. Replacing the graph with an unrelated list would lose the very path the application needs to explain. If FalkorDB is unavailable, the live API reports an error rather than pretending to work from a hidden JSON response.

The result is traceable: a user can see the source, its exact quotation, the chosen interpretation, the affected publications, and the saved history.

## A useful stop is a useful action

Many demonstrations celebrate agents that act without asking. Sometimes the best action is to **refuse to invent certainty**.

PromiseGraph's work loop is bounded:
1. Load the exact variant and its source evidence from FalkorDB.
2. Validate source quotations and measurement conversions using exact decimal arithmetic.
3. Detect incompatible limits and preview how each choice changes the impact radius.
4. Require a human to resolve an actual contradiction.
5. Save the decision in the graph; generate editorial drafts only for unsupported dependent statements.

There is also a read-only intake preview. Paste a source sentence in a documented format, such as “Maximum total mattress-and-topper height: 32 cm.” The program extracts that quotation and previews the effect without saving the provisional statement. Unsupported formats are rejected instead of being hallucinated.

This is **not** a general-purpose LLM parser, and we do not advertise it as one. Our prototype uses a deterministic graph-directed decision loop. Its value is controlled actions, trustworthy evidence and inspectable memory.

## What we verified

The project includes unit and API tests as well as a GitHub Actions integration job that runs the real FalkorDB container and verifies Cypher queries, variant isolation, reviewer decision storage and retrieval through a second client.

A separate Playwright workflow launches the application with real FalkorDB, interacts with the browser, and produces a narrated demo video. These are reproducible, rather than static design mock-ups.

The public Render preview runs on a free service with temporary storage. It is not a durable production database and **should not** be used to claim persistence across host restarts. For durable self-hosted use, the repository includes a Docker Compose configuration with FalkorDB persistence.

We did not connect merchant accounts, measure real return reductions or claim production adoption. Every SKU, source and promise in the demo is synthetic. AI coding assistance from ChatGPT was used and is disclosed.

## Why this matters

Product-data teams do not need another screen that says “conflict detected.” They need a safe answer to: **Where did this claim come from, which other documents repeat it, what should I change, and what must I not touch?**

That is the promise of a graph-backed agent: less chasing, fewer avoidable edits, more accountability. The final publication decision stays with a person, but the tedious relationship tracing does not.

*PromiseGraph — Before You Promise.*

**Explore:** [source, setup and graph model](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026) · [genuine narrated demo](https://github.com/kmarahovskiy-oss/PromiseGraph-GraphHacks-2026/releases/download/graphhacks-demo-2026/PromiseGraph_Real_Demo_Narrated.mp4) · [live preview](https://promisegraph-graphhacks-2026.onrender.com)

**Context:** [Graph Hacks official rules](https://www.wemakedevs.org/hackathons/falkordb/rules); [Baymard product page UX research](https://baymard.com/research/product-page) (general motivation, not project outcome evidence).
