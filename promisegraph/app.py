"""A truthful, graph-dependent local API with explicit reviewer gate."""
from pathlib import Path
import os, logging
from threading import Lock
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .domain import analyze, preview_source
from .store import GraphStore

BASE=Path(__file__).resolve().parent.parent
LOG=logging.getLogger('promisegraph')

class MeasureRequest(BaseModel):
    id: str=Field(min_length=1,max_length=100)
    mattress: str=Field(default='30',max_length=30)
    topper: str=Field(default='4',max_length=30)
    unit: str=Field(default='cm',max_length=5)

class SourcePreviewRequest(MeasureRequest):
    title: str=Field(min_length=3,max_length=100)
    text: str=Field(min_length=30,max_length=2000)

class DecisionRequest(MeasureRequest):
    evidence_id: str=Field(min_length=1,max_length=100)
    reason: str=Field(min_length=12,max_length=400)
    fingerprint: str=Field(min_length=64,max_length=64)
    confirmed: bool=False


def create_app(initial_store=None):
    app=FastAPI(title='PromiseGraph: Can we promise this?',version='2026.10.18')
    app.state.store=initial_store
    guard=Lock()
    def db():
        with guard:
            if app.state.store is None:
                try:
                    candidate=GraphStore()
                    candidate.seed(BASE/'data/demo.json')
                    app.state.store=candidate
                except Exception as exc:
                    LOG.exception('Real FalkorDB failed to initialize')
                    raise HTTPException(503,'Real FalkorDB unavailable. No substitute database is used.') from exc
        return app.state.store
    def result(r):
        try:
            return analyze(db().bundle(r.id),r.mattress,r.topper,r.unit)
        except KeyError as exc: raise HTTPException(404,str(exc)) from exc
        except ValueError as exc: raise HTTPException(422,str(exc)) from exc
    @app.get('/api/health')
    def health():
        return {'status':'connected', 'graph':'FalkorDB','source':'real_graph', 'synthetic':True,**db().counts()}
    @app.get('/api/variants')
    def variants(): return db().contexts()
    @app.post('/api/analyze')
    def check(r:MeasureRequest):
        value=result(r)
        trace=[
            {'tool':'graph.select_variant','status':'complete','detail':r.id},
            {'tool':'graph.collect_source_witnesses','status':'complete','detail':f'{len(value["evidence"])} source witnesses'},
            {'tool':'rule.validate_exact_units','status':'complete','detail':f'{value["required_cm"]} cm combined'},
            {'tool':'graph.follow_DEPENDS_ON_edges','status':'complete','detail':f'{len(value["affected"])} connected promises'},
        ]
        if value['needs_source_review']:
            trace.append({'tool':'agent.request_human_source_review','status':'paused','detail':value['reason']})
        elif value['impact_count']:
            trace.append({'tool':'agent.prepare_editorial_drafts','status':'drafts_prepared',
                          'detail':f'{value["impact_count"]} documents require editorial approval; nothing published'})
        else:
            trace.append({'tool':'agent.skip_unnecessary_edits','status':'complete',
                          'detail':'All linked claims supported by selected evidence'})
        value['agent_trace']=trace
        return value
    @app.get('/api/portfolio')
    def portfolio():
        """Autonomous read-only triage of every real graph-backed SKU/revision.

        A conflict blocks downstream action until a reviewer resolves it.
        This uses real graph queries for each variant, not fixture calculations.
        """
        graph=db()
        rows=[]
        for variant in graph.contexts():
            report=analyze(graph.bundle(variant['id']))
            if report['needs_source_review']:
                action='REVIEW_SOURCES'
                priority=1 if report['state']=='BLOCKED' else 2
            elif report['impact_count']:
                action='REVIEW_CORRECTION_DRAFTS'
                priority=3
            else:
                action='NO_CHANGE_REQUIRED'
                priority=4
            rows.append({
                'id':variant['id'],'name':variant['name'],
                'sku':variant['sku'],'revision':variant['revision'],
                'state':report['state'],'action':action,'priority':priority,
                'affected':report['impact_count'],
                'dependent_claims':len(report['affected']),
                'evidence_sources':len(report['evidence']),
                'possible_impact':max((candidate['affected_count'] for candidate in report['alternatives']),default=report['impact_count']),
                'reason':report['reason'],
            })
        rows.sort(key=lambda row:(row['priority'],-row['possible_impact'],row['id']))
        return {'synthetic':True,'readonly':True,'source':'real_falkordb',
                'variants_scanned':len(rows),
                'requires_review':sum(row['action']=='REVIEW_SOURCES' for row in rows),
                'drafts_ready':sum(row['action']=='REVIEW_CORRECTION_DRAFTS' for row in rows),
                'safe_variants':sum(row['action']=='NO_CHANGE_REQUIRED' for row in rows),
                'items':rows}

    @app.post('/api/replay-conflict')
    def replay_conflict(r:MeasureRequest):
        """Read-only original contradiction, independent of prior public demo approvals.

        Does not mutate the graph, remove audit history or overwrite authority.
        """
        try:
            source=db().bundle(r.id)
            report=analyze({**source,'authority':None},r.mattress,r.topper,r.unit)
        except KeyError as exc:raise HTTPException(404,str(exc)) from exc
        except ValueError as exc:raise HTTPException(422,str(exc)) from exc
        report['preview']=True
        report['replay']=True
        report['preview_note']='Read-only replay of conflicting evidence. Existing reviewer decisions are preserved.'
        return report

    @app.post('/api/preview-source')
    def preview(r:SourcePreviewRequest):
        try:
            return preview_source(db().bundle(r.id),r.title,r.text,r.mattress,r.topper,r.unit)
        except KeyError as exc:raise HTTPException(404,str(exc)) from exc
        except ValueError as exc:raise HTTPException(422,str(exc)) from exc
    @app.post('/api/decide')
    def decide(r:DecisionRequest):
        if not r.confirmed: raise HTTPException(422,'Explicit human confirmation is required')
        if len(r.reason.strip())<12: raise HTTPException(422,'Please record an explanatory reason')
        current=result(r)
        if current['rejected_evidence']:raise HTTPException(422,'Invalid sources must be repaired first')
        try:
            decision=db().approve(r.id,r.evidence_id,r.reason.strip(),r.fingerprint)
        except ValueError as exc:raise HTTPException(409,str(exc)) from exc
        return {'decision_id':decision,'result':result(r),'saved_in':'FalkorDB'}
    @app.get('/api/paths/{id}')
    def paths(id:str): return {'id':id,'relationships':db().paths(id)}
    @app.get('/api/audit/{id}')
    def audit(id:str): return db().audit(id)
    @app.post('/api/export')
    def export(r:MeasureRequest):
        value=result(r)
        return {'format':'promisegraph-draft-v2','synthetic':True,'automatically_published':False,
            'output':'review-only','result':value,'graph_paths':db().paths(r.id),'history':db().audit(r.id)}
    app.mount('/static',StaticFiles(directory=BASE/'promisegraph/static'),name='static')
    @app.get('/')
    def index(): return FileResponse(BASE/'promisegraph/static/index.html')
    return app

app=create_app()
