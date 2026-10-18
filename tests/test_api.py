from fastapi.testclient import TestClient
from promisegraph.app import create_app
from test_domain import bundle

class FauxStore:
    # Test double for API contract only, never used in live app.
    def __init__(self):self.data=bundle(0);self.decision=None
    def bundle(self,id):
        if id!='standard-r3':raise KeyError(id)
        return self.data
    def contexts(self):return [{'id':'standard-r3','name':'Demo'}]
    def counts(self):return {'nodes':42,'edges':41}
    def paths(self,id):return []
    def audit(self,id):return []
    def approve(self,id,evidence,reason,fingerprint):
        self.data['authority']=evidence;return 'test-decision-id'

def test_lifecycle_and_contract():
    c=TestClient(create_app(FauxStore()))
    assert c.get('/api/health').status_code==200
    assert len(c.get('/api/variants').json())==1
    r=c.post('/api/analyze',json={'id':'standard-r3'}).json()
    assert r['state']=='REVIEW_REQUIRED' and len(r['agent_trace'])==5
    assert c.post('/api/decide',json={'id':'standard-r3','evidence_id':'e-standard-drawing','reason':'Drawing approved by reviewer','fingerprint':r['fingerprint'],'confirmed':False}).status_code==422
    agreed=c.post('/api/decide',json={'id':'standard-r3','evidence_id':'e-standard-drawing','reason':'Drawing approved by reviewer','fingerprint':r['fingerprint'],'confirmed':True})
    assert agreed.status_code==200
    assert agreed.json()['result']['impact_count']==2
    assert c.post('/api/export',json={'id':'standard-r3'}).json()['automatically_published'] is False
    assert c.get('/api/paths/standard-r3').status_code==200

def test_source_preview_requires_real_graph_bundle_and_does_not_write():
    store=FauxStore();c=TestClient(create_app(store))
    response=c.post('/api/preview-source',json={'id':'standard-r3','title':'Updated drawing',
        'text':'New R3. Maximum total mattress-and-topper height: 32 cm.'})
    assert response.status_code==200
    body=response.json()
    assert body['preview'] is True and len(body['evidence'])==3
    assert store.data['authority'] is None and len(store.data['evidence'])==2
    bad=c.post('/api/preview-source',json={'id':'standard-r3','title':'Something',
        'text':'A very long but unstructured product description that has no maximum height.'})
    assert bad.status_code==422
