from pathlib import Path
import json,copy
import pytest
from promisegraph.domain import measure,verify_evidence,analyze,fingerprint,preview_source
ROOT=Path(__file__).resolve().parents[1]
DATA=json.loads((ROOT/'data/demo.json').read_text())

def bundle(index):
    v=copy.deepcopy(DATA['variants'][index]);ctx=v['context']
    return {'context':ctx,'evidence':[{**e,**ctx} for e in v['evidence']], 'promises':v['promises'], 'authority':None}

def test_cm_exact(): assert measure('12','in')==measure('30.48','cm')
def test_nonfinite_rejected():
    for value in ['NaN','Infinity','-1','4.1234567']:
        with pytest.raises(ValueError):measure(value)
def test_unknown_unit():
    with pytest.raises(ValueError):measure('1','m')
def test_evidence_all_valid():
    for i in range(3):
        b=bundle(i)
        for e in b['evidence']: assert verify_evidence(e,b['context'])
def test_mismatched_quote_blocked():
    b=bundle(0);b['evidence'][0]['quote']='I made this up'
    assert analyze(b)['state']=='BLOCKED'
def test_out_of_bounds_quote_blocked():
    b=bundle(0);b['evidence'][0]['end']=100000
    assert analyze(b)['state']=='BLOCKED'
def test_wrong_variant_blocked():
    b=bundle(0);b['evidence'][0]['sku']='WRONG'
    assert analyze(b)['state']=='BLOCKED'
def test_conflict_requires_review():
    out=analyze(bundle(0))
    assert out['state']=='REVIEW_REQUIRED' and out['impact_count']==0
    assert all(c['action']=='AWAIT_AUTHORITY' for c in out['affected'])
def test_approved_lesser_limit_fails():
    b=bundle(0);b['authority']='e-standard-drawing';r=analyze(b)
    assert r['state']=='FAIL' and r['limit_cm']=='30.48' and r['impact_count']==2
    assert [a['promise_id'] for a in r['affected'] if a['risk']=='wrong_promise']==['p-store','p-quote']
def test_approved_greater_limit_passes():
    b=bundle(0);b['authority']='e-standard-supplier';r=analyze(b)
    assert r['state']=='PASS' and r['impact_count']==0
def test_deep_separate():
    r=analyze(bundle(1),'34','4')
    assert r['state']=='PASS' and len(r['affected'])==1 and r['affected'][0]['promise_id']=='p-deep'
def test_old_revision_separate():
    r=analyze(bundle(2));assert r['state']=='PASS' and r['context']['revision']=='R2'
def test_fingerprint_changes():
    b=bundle(0);before=fingerprint(b);b['authority']='e-standard-drawing';assert fingerprint(b)!=before
def test_zero_rejected():
    with pytest.raises(ValueError):analyze(bundle(0),'0','0')
def test_negative_rejected():
    with pytest.raises(ValueError):analyze(bundle(0),'-1','4')
def test_exact_unit_edge():
    b=bundle(0);b['authority']='e-standard-drawing'
    assert analyze(b,'30.48','0')['state']=='PASS'
    assert analyze(b,'30.49','0')['state']=='FAIL'

def test_counterfactuals_show_impact_without_choosing_truth():
    b=bundle(0)
    r=analyze(b)
    assert r['state']=='REVIEW_REQUIRED'
    assert r['authority_id'] is None
    alt={a['evidence_id']:a for a in r['alternatives']}
    assert alt['e-standard-supplier']['affected_count']==0
    assert alt['e-standard-drawing']['affected_count']==2
    assert alt['e-standard-drawing']['requested_result']=='FAIL'
    assert b['authority'] is None

def test_no_counterfactual_when_evidence_invalid_or_resolved():
    b=bundle(0)
    b['evidence'][0]['quote']='wrong quote'
    assert analyze(b)['alternatives']==[]
    b=bundle(0);b['authority']='e-standard-drawing'
    assert analyze(b)['alternatives']==[]

def test_preview_new_source_stays_unsaved():
    b=bundle(0);n=len(b['evidence'])
    r=preview_source(b,'Updated document','New revision. Maximum total mattress-and-topper height: 32 cm.')
    assert r['preview'] is True and r['state']=='REVIEW_REQUIRED'
    assert r['preview_source_id'].startswith('preview-')
    assert len(r['evidence'])==3 and len(b['evidence'])==n
    assert r['alternatives'] and b['authority'] is None

def test_preview_unsupported_text_is_rejected():
    with pytest.raises(ValueError):
        preview_source(bundle(0),'Note','Lorem ipsum with no structured measurement at all.')

def test_preview_does_not_inherit_existing_authority():
    b=bundle(0);b['authority']='e-standard-drawing'
    r=preview_source(b,'New document','Source limit. Maximum total mattress-and-topper height: 32 cm.')
    assert r['authority_id'] is None and r['state']=='REVIEW_REQUIRED'
    assert b['authority']=='e-standard-drawing'
