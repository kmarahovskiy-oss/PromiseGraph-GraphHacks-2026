"""The relationship traversals without which PromiseGraph cannot operate."""
CONTEXTS = '''MATCH (v:Variant)-[:HAS_SPEC]->(a:Attribute)
RETURN v.id, v.model, v.sku, v.revision, v.region, v.name, a.authority_id ORDER BY v.id'''
CONTEXT = '''MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)
RETURN v.model, v.sku, v.revision, v.region, v.name, a.authority_id'''
EVIDENCE = '''MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)<-[:MEASURES]-(e:Evidence)<-[:CONTAINS]-(d:Document)
RETURN e.id, e.value, e.unit, e.normalized_cm, e.quote, e.start, e.end,
d.id, d.title, d.text, d.uri, v.model, v.sku, v.revision, v.region ORDER BY e.id'''
IMPACT = '''MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)<-[:DEPENDS_ON]-(p:Promise)<-[:PUBLISHES]-(d:Document)
RETURN p.id, p.text, p.required_cm, d.id, d.title ORDER BY p.id'''
DECISION = '''MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)<-[:MEASURES]-(e:Evidence {id:$evidence})
CREATE (r:Decision {id:$decision, reason:$reason, at:$at, basis:$fingerprint})
CREATE (r)-[:SELECTS]->(e) CREATE (r)-[:RESOLVES]->(a)
SET a.authority_id=e.id RETURN r.id'''
AUDIT = '''MATCH (v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)<-[:RESOLVES]-(r:Decision)-[:SELECTS]->(e:Evidence)
RETURN r.id, r.reason, r.at, e.id ORDER BY r.at DESC'''
# Traverse exact dependencies; demonstrate that Deep variants are isolated.
EXPLAIN_PATH = '''MATCH path=(v:Variant {id:$id})-[:HAS_SPEC]->(a:Attribute)<-[:DEPENDS_ON]-(p:Promise)<-[:PUBLISHES]-(d:Document)
RETURN v.id, a.id, p.id, d.id ORDER BY p.id'''
