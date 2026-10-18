'use strict';
const $=id=>document.getElementById(id);
let report=null;
let reportInputs=null;
let analysisSequence=0;
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const payload=()=>({id:$('variant').value,mattress:$('mattress').value,topper:$('topper').value,unit:'cm'});
async function api(path,opts={}){
 const response=await fetch(path,{...opts,headers:{'Content-Type':'application/json',...(opts.headers||{})}});
 if(!response.ok){let error;try{error=(await response.json()).detail}catch{error=response.statusText};throw Error(typeof error==='string'?error:JSON.stringify(error))}
 return response.json();
}
const status=(value,label,css)=>{$('status').textContent=label;$('status').className='pill '+css};
async function startup(){try{
 const h=await api('/api/health');$('connection').textContent=`FalkorDB · ${h.nodes} nodes · ${h.edges} edges`;
 const variants=await api('/api/variants');$('variant').innerHTML=variants.map(v=>`<option value="${esc(v.id)}">${esc(v.name)} · ${esc(v.region)}</option>`).join('');
 if(variants.some(v=>v.id==='standard-r3'))$('variant').value='standard-r3';
 await check();
 await scanPortfolio();
 }catch(e){$('connection').textContent='FalkorDB unavailable';$('headline').textContent='Graph connection required';$('explanation').textContent=e.message;$('check').disabled=true;status(null,'Database offline','fail');}}
async function check(){const sequence=++analysisSequence;const inputs=payload();report=null;reportInputs=null;try{$('check').disabled=true;status(null,'Analyzing…','neutral');const next=await api('/api/analyze',{method:'POST',body:JSON.stringify(inputs)});if(sequence===analysisSequence){report=next;reportInputs=inputs;render(next)}}catch(e){if(sequence===analysisSequence){report=null;reportInputs=null;$('explanation').textContent=e.message;$('claims').textContent='No current analysis';$('sources').textContent='No current evidence';$('review').classList.add('hidden');status(null,'Error','fail')}}finally{if(sequence===analysisSequence)$('check').disabled=false}}
function render(r){let state=r.state;
 status(null,({REVIEW_REQUIRED:'SOURCE CONFLICT',BLOCKED:'STOP · SOURCE INVALID',PASS:'DOCUMENTED FIT',FAIL:'UNSUPPORTED CLAIM'})[state],({REVIEW_REQUIRED:'review',BLOCKED:'fail',PASS:'pass',FAIL:'fail'})[state]);
 $('headline').textContent=({REVIEW_REQUIRED:'Two sources. Two answers. One decision to make.',BLOCKED:'A source or customer-facing claim cannot be trusted yet.',PASS:'The selected documentation supports this fit.',FAIL:'This promise would mislead the buyer.'})[state];
 $('explanation').textContent=r.reason+(r.rejected_claims?.length?' Invalid customer claims: '+r.rejected_claims.map(x=>x.id).join(', ')+'.':'')+(r.replay?' READ-ONLY REPLAY: no earlier decision is erased or changed.':'');$('required').textContent=r.required_cm+' cm';$('limit').textContent=r.limit_cm?r.limit_cm+' cm':'Unresolved';$('impact').textContent=r.limit_cm?String(r.impact_count):'Pending';
 $('scenarios').classList.toggle('hidden',!(r.alternatives||[]).length);
 $('scenarioCards').innerHTML=(r.alternatives||[]).map(a=>`<div class="scenario"><span class="tag">WHAT IF · ${esc(a.requested_result)}</span><strong>${esc(a.title)}</strong><p>Allowed stack: <b>${esc(a.limit_cm)} cm</b></p><p><b>${esc(a.affected_count)}</b> dependent claims would need correction</p><div class="subtitle">${esc(a.affected_titles.join(' · ')||'No linked claims need correction')}</div><small>Not an approved decision</small></div>`).join('');
 $('sources').innerHTML=r.evidence.map(s=>`<div class="source"><span class="tag">${esc(s.normalized_cm)} CM · ${esc(s.unit)} ORIGINAL</span><strong>${esc(s.title)}</strong><div class="subtitle">${esc(s.id)} · ${esc(s.region)} / ${esc(s.revision)}</div><blockquote>${esc(s.quote)}</blockquote></div>`).join('')||'No valid sources';
 $('claims').innerHTML=r.affected.map(c=>`<div class="claim"><span class="tag">${esc(c.risk==='wrong_promise'?'NEEDS CORRECTION':c.risk==='okay'?'SUPPORTED':'WAITING FOR REVIEW')}</span><strong>${esc(c.title)}</strong><div class="preview">${esc(c.current)}</div>${c.suggestion?`<div class="draft">SUGGESTED DRAFT: ${esc(c.suggestion)}</div>`:''}</div>`).join('')||'No dependent claims found';
 $('review').classList.toggle('hidden',state!=='REVIEW_REQUIRED'||!!r.preview);
 $('authority').innerHTML=r.evidence.map(s=>`<option value="${esc(s.id)}">${esc(s.title)} — ${esc(s.normalized_cm)} cm</option>`).join('');
 $('details').classList.add('hidden');$('confirm').checked=false;
}
async function scanPortfolio(){
 const button=$('scanPortfolio');button.disabled=true;$('portfolioSummary').textContent='Following graph relationships across all variants…';
 try{
  const d=await api('/api/portfolio');
  $('portfolioSummary').textContent=`${d.variants_scanned} variants checked · ${d.requires_review} awaiting source review · ${d.drafts_ready} with corrections to review · ${d.safe_variants} requiring no changes`;
  $('portfolioItems').innerHTML=d.items.map(v=>`<button type="button" class="portfolio-item" data-variant="${esc(v.id)}"><strong>${esc(v.name)}</strong><span class="tag">${esc(v.action.replaceAll('_',' '))}</span><small>${esc(v.sku)} · ${esc(v.revision)} · ${esc(v.evidence_sources)} source(s) · ${esc(v.dependent_claims)} dependent claim(s) · up to ${esc(v.possible_impact)} at risk</small></button>`).join('');
  $('portfolioItems').querySelectorAll('button[data-variant]').forEach(b=>b.addEventListener('click',()=>{
   $('variant').value=b.dataset.variant;check();$('headline').scrollIntoView({behavior:'smooth',block:'center'});
  }));
 }catch(e){$('portfolioSummary').textContent='Portfolio scan unavailable: '+e.message}
 finally{button.disabled=false}
}
async function reconsider(){
 await check();
 if(!report)return;
 if((report.rejected_evidence||[]).length){alert('Cannot review invalid sources. Repair their quotations first.');return}
 if(!(report.evidence||[]).length){alert('No verified source available.');return}
 $('review').classList.remove('hidden');
 $('review').scrollIntoView({behavior:'smooth',block:'center'});
}
async function replay(){
 const sequence=++analysisSequence,inputs=payload();report=null;reportInputs=null;$('review').classList.add('hidden');
 try{$('replay').disabled=true;const value=await api('/api/replay-conflict',{method:'POST',body:JSON.stringify(inputs)});
  if(sequence===analysisSequence){report=value;reportInputs=inputs;render(value);$('previewNote').textContent=value.preview_note;}
 }catch(e){if(sequence===analysisSequence)$('previewNote').textContent='Replay unavailable: '+e.message}
 finally{$('replay').disabled=false}
}
async function preview(){
 const sequence=++analysisSequence,inputs=payload();report=null;reportInputs=null;$('review').classList.add('hidden');
 try{$('preview').disabled=true;const data={...inputs,title:$('newtitle').value,text:$('newtext').value};
 const value=await api('/api/preview-source',{method:'POST',body:JSON.stringify(data)});
 if(sequence===analysisSequence){report=value;reportInputs=inputs;render(value);$('previewNote').textContent=value.preview_note;}
 }catch(e){if(sequence===analysisSequence)$('previewNote').textContent='Source preview unavailable: '+e.message}
 finally{$('preview').disabled=false}}
async function approve(){if(!report)return;try{if(report.preview){alert('A read-only replay or preview cannot be approved. Run a fresh graph analysis first.');return}if(JSON.stringify(payload())!==JSON.stringify(reportInputs)){alert('Inputs changed. Run the analysis again before deciding.');return}if(!$('confirm').checked){alert('Please confirm you reviewed the evidence.');return}
 const inputs=payload(),sequence=analysisSequence;
 const data={...inputs,evidence_id:$('authority').value,reason:$('reason').value,fingerprint:report.fingerprint,confirmed:true};
 $('approve').disabled=true;const next=await api('/api/decide',{method:'POST',body:JSON.stringify(data)});
 if(sequence!==analysisSequence||JSON.stringify(payload())!==JSON.stringify(inputs))return;
 report=next.result;reportInputs=inputs;render(report);
 $('details').textContent='Decision saved to FalkorDB: '+next.decision_id;$('details').classList.remove('hidden');
 await scanPortfolio();
 }catch(e){alert(e.message)}finally{$('approve').disabled=false}}
function humanDetail(name,data){
 if(name==='REVIEW HISTORY'){
  if(!Array.isArray(data)||!data.length)return 'No reviewer decisions saved for this variant yet.';
  return ['Saved source-of-truth decisions',...data.map((d,i)=>
    (i+1)+'. Evidence: '+d.evidence_id+'\n   Date: '+d.at+'\n   Reason: '+d.reason+'\n   Audit ID: '+d.id)].join('\n\n');
 }
 if(name==='GRAPH PATHS'){
  const rows=data?.relationships||[];
  if(!rows.length)return 'No connected customer-facing promises found for this variant.';
  return ['Exact variant → evidence attribute → dependent promise → publication',
    ...rows.map((r,i)=>(i+1)+'. '+r.variant+' → '+r.attribute+' → '+r.promise+' → '+r.document)].join('\n');
 }
 return JSON.stringify(data,null,2);
}
async function detail(name,path){if(!payload().id)return;const sequence=analysisSequence;try{
 const data=await api(path);
 if(sequence===analysisSequence){$('details').textContent=humanDetail(name,data);$('details').classList.remove('hidden')}
 }catch(e){if(sequence===analysisSequence)alert(e.message)}}
async function exportDraft(){if(!report||!reportInputs){alert('Run an analysis before exporting.');return}if(JSON.stringify(payload())!==JSON.stringify(reportInputs)){alert('Inputs changed. Run analysis again before exporting.');return}try{
 // Export must represent the CURRENT on-screen result, including a read-only
 // replay or preview, rather than silently querying a different graph decision.
 const selected=report,params={...reportInputs};
 const result={format:'promisegraph-visible-report-v3',synthetic:true,automatically_published:false,
  read_only:!!selected.preview,replay:!!selected.replay,output:'review-only',inputs:params,
  result:selected,notice:selected.preview?'Read-only simulation; no source decision was changed or saved.':'Graph-backed analysis; no automatic publication.'};
 const blob=new Blob([JSON.stringify(result,null,2)],{type:'application/json'});
 const u=URL.createObjectURL(blob),a=document.createElement('a');a.href=u;
 a.download=selected.preview?'promisegraph-readonly-preview.json':'promisegraph-review-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),5000)
 }catch(e){alert(e.message)}}
async function copyCorrectionDrafts(){
 if(!report||report.preview){$('details').textContent='A saved review is needed. Run the graph analysis and select an authoritative source first.';$('details').classList.remove('hidden');return}
 if(JSON.stringify(payload())!==JSON.stringify(reportInputs)){$('details').textContent='Inputs changed. Run analysis again before copying.';$('details').classList.remove('hidden');return}
 const drafts=(report.affected||[]).filter(x=>x.action==='REVIEW_DRAFT'&&x.suggestion);
 if(!drafts.length){$('details').textContent='No verified correction drafts are ready. Nothing copied.';$('details').classList.remove('hidden');return}
 const lines=[`PromiseGraph — editorial correction drafts (NOT published)`,`Product variant: ${report.context.sku}, ${report.context.revision}, ${report.context.region}`,`Approved evidence ID: ${report.authority_id}`,`Evidence fingerprint: ${report.fingerprint}`,`Affected claims: ${drafts.length}`,''];
 drafts.forEach((d,i)=>{lines.push(`${i+1}. ${d.title} (${d.document_id})`,`Current: ${d.current}`,`Proposed: ${d.suggestion}`,'')});
 lines.push('Review every edit before publishing. Synthetic demonstration data.');
 const text=lines.join('\n');
 try{if(!navigator.clipboard?.writeText)throw Error('Clipboard API unavailable');await navigator.clipboard.writeText(text);$('details').textContent=`Copied ${drafts.length} evidence-backed correction draft(s) to clipboard.`}
 catch(_){const blob=new Blob([text],{type:'text/plain;charset=utf-8'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='promisegraph-correction-drafts.txt';a.click();setTimeout(()=>URL.revokeObjectURL(url),5000);$('details').textContent=`Clipboard unavailable; downloaded ${drafts.length} draft(s) as a text file.`}
 $('details').classList.remove('hidden');
}
$('check').addEventListener('click',()=>{$('previewNote').textContent='';check()});$('reconsider').addEventListener('click',reconsider);$('scanPortfolio').addEventListener('click',scanPortfolio);$('replay').addEventListener('click',replay);$('preview').addEventListener('click',preview);$('approve').addEventListener('click',approve);$('paths').addEventListener('click',()=>detail('GRAPH PATHS','/api/paths/'+encodeURIComponent(payload().id)));$('history').addEventListener('click',()=>detail('REVIEW HISTORY','/api/audit/'+encodeURIComponent(payload().id)));$('export').addEventListener('click',exportDraft);$('copyDrafts').addEventListener('click',copyCorrectionDrafts);
$('variant').addEventListener('change',()=>{$('previewNote').textContent='';check()});$('mattress').addEventListener('change',check);$('topper').addEventListener('change',check);
startup();
