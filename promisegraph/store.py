"""FalkorDB is mandatory. No JSON/in-memory replacement for graph responses."""
import json, os
from pathlib import Path
from datetime import datetime, timezone
from threading import RLock
from uuid import uuid4
from .domain import verify_evidence, fingerprint
from . import queries as q

class GraphStore:
    def __init__(self, host=None, port=None, graph='promisegraph_contest_2026'):
        if os.getenv('FALKORDB_MODE') == 'embedded':
            # Genuine FalkorDBLite runs FalkorDB+Redis in-process via a local server.
            # It is NOT an in-memory graph substitute. Requires permission for Unix sockets.
            from redislite.falkordb_client import FalkorDB as EmbeddedFalkorDB
            path = Path(os.getenv('FALKORDB_FILE', 'var/promisegraph.db'))
            path.parent.mkdir(parents=True, exist_ok=True)
            self._db = EmbeddedFalkorDB(str(path))
        else:
            from falkordb import FalkorDB  # official client to real TCP service
            self._db = FalkorDB(host=host or os.getenv('FALKORDB_HOST','127.0.0.1'),
                                port=int(port or os.getenv('FALKORDB_PORT','6379')),
                                password=os.getenv('FALKORDB_PASSWORD') or None)
        self.graph = self._db.select_graph(graph)
        self.lock = RLock()

    def query(self, cypher, params=None):
        return self.graph.query(cypher, params=params or {}).result_set

    def seed(self, file):
        data = json.loads(Path(file).read_text(encoding='utf-8'))
        with self.lock:
            for variant in data['variants']:
                ctx = variant['context']
                for e in variant['evidence']:
                    verify_evidence({**ctx,**e},ctx)
                a_id = variant['id']+':height'
                self.query('''MERGE (m:Model {id:$model})
                  MERGE (v:Variant {id:$id}) SET v.model=$model, v.sku=$sku,
                  v.revision=$revision, v.region=$region, v.name=$name
                  MERGE (a:Attribute {id:$attribute}) SET a.property='max_stack_height'
                  MERGE (m)-[:HAS_VARIANT]->(v) MERGE (v)-[:HAS_SPEC]->(a)''',
                  {'id':variant['id'],'attribute':a_id,**ctx})
                for e in variant['evidence']:
                    self.query('''MATCH (a:Attribute {id:$attribute})
                      MERGE (d:Document {id:$document_id}) SET d.title=$title,d.text=$text,d.uri=$uri,d.synthetic=true
                      MERGE (e:Evidence {id:$id}) SET e.value=$value,e.unit=$unit,e.normalized_cm=$normalized_cm,
                      e.quote=$quote,e.start=$start,e.end=$end
                      MERGE (d)-[:CONTAINS]->(e) MERGE (e)-[:MEASURES]->(a)''',{**e,'attribute':a_id})
                for p in variant['promises']:
                    self.query('''MATCH (a:Attribute {id:$attribute})
                      MERGE (d:Document {id:$document_id}) SET d.title=$title,d.text=$text,d.synthetic=true
                      MERGE (p:Promise {id:$id}) SET p.text=$text,p.required_cm=$required_cm
                      MERGE (d)-[:PUBLISHES]->(p) MERGE (p)-[:DEPENDS_ON]->(a)''', {**p,'attribute':a_id})
    def contexts(self):
        return [dict(zip(('id','model','sku','revision','region','name','authority'),r)) for r in self.query(q.CONTEXTS)]
    def bundle(self, id):
        rows=self.query(q.CONTEXT,{'id':id})
        if not rows: raise KeyError('Unknown product variant')
        ctx=dict(zip(('model','sku','revision','region','name'), rows[0][:5]))
        keys=('id','value','unit','normalized_cm','quote','start','end','document_id','title','text','uri','model','sku','revision','region')
        ev=[dict(zip(keys,r)) for r in self.query(q.EVIDENCE,{'id':id})]
        promises=[dict(zip(('id','text','required_cm','document_id','title'),r)) for r in self.query(q.IMPACT,{'id':id})]
        return {'context':ctx,'evidence':ev,'promises':promises,'authority':rows[0][5]}
    def approve(self,id,evidence,reason,expected_fingerprint):
        with self.lock:
            b=self.bundle(id)
            if fingerprint(b)!=expected_fingerprint: raise ValueError('Graph changed; run a new review')
            selected=next((e for e in b['evidence'] if e['id']==evidence),None)
            if selected is None: raise ValueError('Evidence does not belong to selected variant')
            verify_evidence(selected,b['context'])
            decision=str(uuid4())
            rows=self.query(q.DECISION,{'id':id,'evidence':evidence,'decision':decision,'reason':reason,
                      'at':datetime.now(timezone.utc).isoformat(),'fingerprint':expected_fingerprint})
            if not rows: raise ValueError('Decision could not be recorded')
            return decision
    def audit(self,id):
        return [dict(zip(('id','reason','at','evidence_id'),r)) for r in self.query(q.AUDIT,{'id':id})]
    def paths(self,id):
        return [dict(zip(('variant','attribute','promise','document'),r)) for r in self.query(q.EXPLAIN_PATH,{'id':id})]
    def counts(self):
        return {'nodes':self.query('MATCH (n) RETURN count(n)')[0][0],
                'edges':self.query('MATCH ()-[r]->() RETURN count(r)')[0][0]}
