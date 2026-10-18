'use strict';
const $=id=>document.getElementById(id);
let report=null;
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
 }catch(e){$('connection').textContent='FalkorDB unavailable';$('headline').textContent='Graph connection required';$('explanation').textContent=e.message;$('check').disabled=true;status(null,'Database offline','fail');}}
async function check(){const sequence=++analysisSequence;try{$('check').disabled=true;status(null,'Analyzing…','neutral');const next=await api('/api/analyze',{method:'POST',body:JSON.stringify(payload())});if(sequence===analysisSequence){report=next;render(next)}}catch(e){if(sequence===analysisSequence){report=null;$('explanation').textContent=e.message;$('claims').textContent='No current analysis';$('sources').textContent='No current evidence';status(null,'Error','fail')}}finally{if(sequence===analysisSequence)$('check').disabled=false}}
function render(r){let state=r.state;
 status(null,({REVIEW_REQUIRED:'SOURCE CONFLICT',BLOCKED:'STOP · SOURCE INVALID',PASS:'DOCUMENTED FIT',FAIL:'UNSUPPORTED CLAIM'})[state],({REVIEW_REQUIRED:'review',BLOCKED:'fail',PASS:'pass',FAIL:'fail'})[state]);
 $('headline').textContent=({REVIEW_REQUIRED:'Two sources. Two answers. One decision to make.',BLOCKED:'Evidence cannot be trusted yet.',PASS:'The selected documentation supports this fit.',FAIL:'This promise would mislead the buyer.'})[state];
 $('explanation').textContent=r.reason+(r.replay?' READ-ONLY REPLAY: no earlier decision is erased or changed.':'');$('required').textContent=r.required_cm+' cm';$('limit').textContent=r.limit_cm?r.limit_cm+' cm':'Unresolved';$('impact').textContent=r.limit_cm?String(r.impact_count):'Pending';
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
 ++analysisSequence;$('check').disabled=false;
 try{$('replay').disabled=true;
  report=await api('/api/replay-conflict',{method:'POST',body:JSON.stringify(payload())});
  render(report);$('previewNote').textContent=report.preview_note;
 }catch(e){$('previewNote').textContent=e.message}finally{$('replay').disabled=false}
}
async function preview(){++analysisSequence;$('check').disabled=false;try{
 $('preview').disabled=true;const data={...payload(),title:$('newtitle').value,text:$('newtext').value};
 report=await api('/api/preview-source',{method:'POST',body:JSON.stringify(data)});
 render(report);$('previewNote').textContent=report.preview_note;
 }catch(e){$('previewNote').textContent=e.message}finally{$('preview').disabled=false}}
async function approve(){if(!report)return;try{if(!$('confirm').checked){alert('Please confirm you reviewed the evidence.');return}
 const data={...payload(),evidence_id:$('authority').value,reason:$('reason').value,fingerprint:report.fingerprint,confirmed:true};
 $('approve').disabled=true;const next=await api('/api/decide',{method:'POST',body:JSON.stringify(data)});render(next.result);
 $('details').textContent='Decision saved to FalkorDB: '+next.decision_id;$('details').classList.remove('hidden');
 }catch(e){alert(e.message)}finally{$('approve').disabled=false}}
async function detail(name,path){if(!payload().id)return;try{const data=await api(path);$('details').textContent=name+'\n'+JSON.stringify(data,null,2);$('details').classList.remove('hidden')}catch(e){alert(e.message)}}
async function exportDraft(){if(!report)return;try{const data=await api('/api/export',{method:'POST',body:JSON.stringify(payload())});const blob=new Blob([JSON.stringify(data,null,2)],{type:'application/json'});const u=URL.createObjectURL(blob);const a=document.createElement('a');a.href=u;a.download='promisegraph-review-draft.json';a.click();setTimeout(()=>URL.revokeObjectURL(u),5000)}catch(e){alert(e.message)}}
$('check').addEventListener('click',()=>{$('previewNote').textContent='';check()});$('reconsider').addEventListener('click',reconsider);$('scanPortfolio').addEventListener('click',scanPortfolio);$('replay').addEventListener('click',replay);$('preview').addEventListener('click',preview);$('approve').addEventListener('click',approve);$('paths').addEventListener('click',()=>detail('GRAPH PATHS','/api/paths/'+encodeURIComponent(payload().id)));$('history').addEventListener('click',()=>detail('REVIEW HISTORY','/api/audit/'+encodeURIComponent(payload().id)));$('export').addEventListener('click',exportDraft);
$('variant').addEventListener('change',()=>{$('previewNote').textContent='';check()});$('mattress').addEventListener('change',check);$('topper').addEventListener('change',check);
startup();
