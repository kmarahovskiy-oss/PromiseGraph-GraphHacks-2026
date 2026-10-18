# Five-minute participant technical review

**This is a review guide, not a claim that a participant has reviewed it.**

## The customer problem
A supplier catalog states 35 cm maximum stacked height, but the matching R3 engineering drawing states 12 in = 30.48 cm. The online product page and a salesperson promise a 34 cm combination will fit. Manual checking is slow, and the same wrong claim spreads.

## The real graph dependency
1. `Model -HAS_VARIANT-> Variant -HAS_SPEC-> Attribute`. The `Variant.id` uniquely identifies model, SKU, revision, market.
2. `Document -CONTAINS-> Evidence -MEASURES-> Attribute`: source quotes with exact spans and normalized units.
3. `Document -PUBLISHES-> Promise -DEPENDS_ON-> Attribute`: the graph returns impacted claims after an evidence decision.
4. `Decision -SELECTS-> Evidence` and `Decision -RESOLVES-> Attribute`: records source selection, justification and time.

Review `promisegraph/queries.py` to understand each actual Cypher traversal. The application returns HTTP 503 if it cannot reach FalkorDB: no local mock database is substituted in production.

## Expected demo behavior
- Pick **AstraRest Standard R3**, mattress 30 cm + topper 4 cm.
- Before approval: REVIEW_REQUIRED because 35 cm and 30.48 cm conflict.
- Review the drawing (12 inches), provide a reason, approve.
- After approval: FAIL; product page and quotation need corrections; 28 cm FAQ remains safe.
- Select **Deep R3**: unaffected. Refresh and check audit history.

## What was and was not verified
Local domain/API-contract tests use test doubles; they do not validate actual graph execution. A real FalkorDB integration test and genuine video are mandatory before submitting. On free Render services, an embedded graph may lose its filesystem after restart; do not claim persistent cross-restart memory.

## Required participant tasks
1. Read and understand the graph model, queries and agent design.
2. Run or inspect the genuine real-graph verification and demo.
3. Decide whether the evidence-based constraints and non-generative agent behavior are correctly represented.
4. Review the AI coding assistant disclosure and source provenance.
5. Approve the final public submission separately after reviewing the video.
