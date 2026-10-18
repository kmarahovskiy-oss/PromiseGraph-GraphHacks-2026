"""Hard graph integration gate. Run: RUN_GRAPH_TESTS=1 pytest tests/test_live_graph.py -v"""
import os
from uuid import uuid4
from pathlib import Path
import pytest
from promisegraph.store import GraphStore
from promisegraph.domain import analyze,fingerprint

pytestmark = pytest.mark.skipif(os.getenv('RUN_GRAPH_TESTS')!='1',reason='Needs real FalkorDB Docker server and official Python client; not a fake success')
ROOT=Path(__file__).resolve().parents[1]

def test_real_graph_seed_trace_decision_memory():
    # Isolated graph ensures this test cannot change an existing review history.
    graph_name='promisegraph_test_'+uuid4().hex
    g=GraphStore(graph=graph_name)
    g.seed(ROOT/'data/demo.json')
    assert len(g.contexts())==3
    b=g.bundle('standard-r3')
    assert analyze(b)['state']=='REVIEW_REQUIRED'
    assert len(g.paths('standard-r3'))==3
    result=g.approve('standard-r3','e-standard-drawing',
        'Synthetic drawing reviewed as authoritative for smoke test',fingerprint(b))
    assert result
    assert analyze(g.bundle('standard-r3'))['impact_count']==2
    assert analyze(g.bundle('deep-r3'),'34','4')['state']=='PASS'
    assert len(g.audit('standard-r3'))==1
    # Fresh connection to same graph checks durable DB memory.
    g2=GraphStore(graph=graph_name)
    assert g2.bundle('standard-r3')['authority']=='e-standard-drawing'
    assert len(g2.audit('standard-r3'))==1


def test_real_graph_portfolio_scan_and_replay_stay_readonly():
    from fastapi.testclient import TestClient
    from promisegraph.app import create_app
    graph_name='promisegraph_portfolio_test_'+uuid4().hex
    g=GraphStore(graph=graph_name)
    g.seed(ROOT/'data/demo.json')
    client=TestClient(create_app(g))
    scan=client.get('/api/portfolio')
    assert scan.status_code == 200
    rows=scan.json()
    assert rows['source']=='real_falkordb'
    assert rows['variants_scanned']==3
    assert rows['requires_review']==1
    assert rows['safe_variants']==2
    assert rows['items'][0]['id']=='standard-r3'
    assert rows['items'][0]['possible_impact']==2
    before=g.bundle('standard-r3')
    decision=g.approve('standard-r3','e-standard-drawing',
        'Signed engineering drawing selected in real test',fingerprint(before))
    assert decision
    replay=client.post('/api/replay-conflict',json={'id':'standard-r3'})
    assert replay.status_code==200
    replayed=replay.json()
    assert replayed['state']=='REVIEW_REQUIRED' and replayed['replay']
    assert replayed['preview'] and len(replayed['alternatives'])==2
    assert g.bundle('standard-r3')['authority']=='e-standard-drawing'
    assert len(g.audit('standard-r3'))==1
    fresh=client.get('/api/portfolio').json()
    assert fresh['drafts_ready']==1 and fresh['requires_review']==0
