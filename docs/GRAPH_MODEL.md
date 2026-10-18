# Graph design & critical Cypher

| Node | Identity | Purpose |
|---|---|---|
| Model | `id` | Product family |
| Variant | `id`, `model`, `sku`, `revision`, `region` | Exact commercial item context |
| Attribute | `id`, `property` | Requirement under review |
| Document | `id`, `text`, `uri`, `synthetic` | Original evidence and promise publication |
| Evidence | `id`, `quote`, `start`, `end`, `normalized_cm` | Verifiable witness |
| Promise | `id`, `required_cm`, `text` | Customer-facing claim |
| Decision | `id`, `reason`, `at`, `basis` | Recorded human-source selection |

### 1) Evidence chain for exactly one SKU

```cypher
MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)
      <-[:MEASURES]-(e:Evidence)<-[:CONTAINS]-(d:Document)
RETURN e.id, e.quote, d.text, v.sku, v.revision, v.region;
```

### 2) Blast-radius query — graph-dependent core

```cypher
MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)
      <-[:DEPENDS_ON]-(p:Promise)<-[:PUBLISHES]-(d:Document)
RETURN p.id, p.text, p.required_cm, d.title;
```

The product, revision and regional edges are not optional: without the exact `Variant` context, an outdated revision or Deep variant might be incorrectly edited.

### 3) Persistent review decision

```cypher
MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)
      <-[:MEASURES]-(e:Evidence {id:$evidence})
CREATE (r:Decision {id:$decision, reason:$reason, at:$at, basis:$fingerprint})
CREATE (r)-[:SELECTS]->(e)
CREATE (r)-[:RESOLVES]->(a)
SET a.authority_id=e.id
RETURN r.id;
```

The approval API verifies a fingerprint of graph-returned source evidence and promises immediately before mutation, preventing silent acceptance of stale facts under the single-process demo model. Correction drafts only after a valid source is selected.
