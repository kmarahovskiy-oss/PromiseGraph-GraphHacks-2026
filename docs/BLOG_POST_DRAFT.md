# Your Product Page Is a Promise. What If Your Documents Disagree?

*PromiseGraph · Graph Hacks 2026 · Draft for human editing and publication only after the real demo is verified.*

A customer clicks “Buy” because the description says the mattress will fit. A support representative confirms it. The sales quotation repeats the same promise. Then a specification turns up that makes the promise impossible.

No one intentionally lied. They simply copied what they found in different documents. A return, a complaint and an awkward phone call follow.

This is not a hypothetical UX problem. Baymard Institute's research shows that shoppers need clear size information and struggle when product pages fail to communicate scale and dimensions. We should not equate that with a measured PromiseGraph effect: we have no live merchant trial and make no claim of returns prevented.

## The real problem isn't arithmetic. It's relationships.

Converting 12 inches into 30.48 centimetres takes no effort. The hard part is answering: Which document applies to **this exact SKU**? Is it the latest revision? Which product pages and quotations reference that specification? If the authoritative source changes, which other promises should be revisited — and which should stay untouched?

Traditional keyword search might surface a dozen documents. A spreadsheet can store a number. Neither automatically reveals the chain from a supplier quotation to the product variant, its specification, and every downstream promise.

## One fictional product, two incompatible truths

Our synthetic AstraRest Standard R3 case has two sources for the same physical constraint:

- A supplier catalogue says the maximum combined mattress-and-topper height is 35 cm.
- An engineering drawing says the maximum is 12 inches — exactly 30.48 cm.

The store promises that a 30 cm mattress and a 4 cm topper will fit. Another quotation repeats the promise. A support FAQ says a 28 cm total will fit. Meanwhile, the Deep variant has a different 40 cm limit.

A naive algorithm picks 35 cm and says “Yes.” An equally naive algorithm picks the smaller value and declares everything wrong. **PromiseGraph does neither.** It recognises the contradiction and asks a reviewer to identify the authoritative source and explain why.

That pause is a feature. Confidence without evidence is a liability.

Before the reviewer chooses, PromiseGraph now shows a **counterfactual side-by-side**: accepting the 35 cm catalogue would leave the two 34 cm promises supported, whereas accepting the 30.48 cm drawing would flag two of them. The previews are explicitly *not* approvals. This makes the cost of the decision legible without pretending the algorithm knows which conflicting document is correct.

## Why FalkorDB is the engine, not a logo

We represent the claim as a connected graph:

`Variant → Attribute ← Evidence ← Document`  
`Attribute ← Promise ← Document`  
`Decision → Evidence`, and `Decision → Attribute`

FalkorDB Cypher traversals locate the exact evidence, trace dependent customer-facing claims and persist the selected source-of-truth decision. A different variant or obsolete revision does not share the same attribute node. When the evidence changes, the set of impacted promises emerges from graph topology.

The test we apply to the architecture is simple: **remove FalkorDB**. Without the graph, the live service cannot retrieve its evidence, impacted documents or review history. There is no hidden JSON “demo database” in the live endpoint.

## Bring your own source — without breaking the graph

The updated prototype also accepts a synthetic source excerpt pasted into the workbench. A strict parser recognises an explicit total-height statement and preserves its exact quotation and unit conversion. PromiseGraph then temporarily adds this witness to the retrieved graph context and previews what would change. The shared demo graph is not mutated, and the preview cannot be approved as if it were a stored source. This is bounded document intake, **not open-ended generative document understanding**; broader formats and real integrations remain future work.

## What happens after a human decision?

If the reviewer confirms the 12-inch engineering drawing, PromiseGraph marks the 34 cm promise unsupported. It prepares proposed corrections for the linked store listing and sales quotation. It retains the 28 cm FAQ, which remains supported, and does not touch the 40 cm Deep version.

The proposals are drafts, not website updates. Every item comes with its source and reviewer history; a merchandiser decides whether and how to publish.

The system saves effort by doing the repetitive cross-document tracing, while preserving human responsibility for disputed evidence.

## Where we draw the boundary

PromiseGraph does not prove that a physical product fits. It verifies what controlled source documents justify. It does not crawl private company systems, publish unsupervised edits or make unsupported performance claims. The prototype uses synthetic data and a deterministic graph-driven decision loop; it does not claim a generative model is running in production. Development used ChatGPT coding assistance, which we disclose explicitly.

A high-quality agent needs not only the ability to act, but also the wisdom to **stop when evidence is contradictory**.

*Technical implementation: Python, FastAPI, FalkorDB and Cypher. The event-window implementation includes domain and API tests. The live graph, visual review and real demo video must be verified before this draft is published.*

### Research links

- Baymard Institute, Product Page UX: https://baymard.com/research/product-page
- Baymard, Product Page UX Best Practices: https://baymard.com/research-articles/current-state-ecommerce-product-page-ux
- Graph Hacks official rules: https://www.wemakedevs.org/hackathons/falkordb/rules
