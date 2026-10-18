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
