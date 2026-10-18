'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const clientPath = process.argv[2] || path.join(__dirname, '../promisegraph/static/app.js');
const source = fs.readFileSync(clientPath, 'utf8').replace(/startup\(\);\s*$/, '');
const report = (state, authority, suggestion) => ({
 state, reason:'Synthetic regression check', required_cm:'34', limit_cm:'30.48', impact_count:suggestion?1:0,
 fingerprint:'a'.repeat(64), authority_id:authority, context:{sku:'STD',revision:'R3',region:'EU'},
 evidence:[], alternatives:[], affected:suggestion?[{action:'REVIEW_DRAFT',suggestion,title:'Quote',document_id:'quote',current:'Old claim',risk:'wrong_promise'}]:[]
});
function harness(){
 const elements=new Map(), alerts=[], clips=[], downloads=[];
 function element(id){if(!elements.has(id))elements.set(id,{value:'',checked:false,disabled:false,textContent:'',innerHTML:'',
 classList:{add(){},remove(){},toggle(){}},addEventListener(){},scrollIntoView(){},querySelectorAll(){return []}});
 return elements.get(id);}
 element('variant').value='standard-r3';element('mattress').value='30';element('topper').value='4';
 element('authority').value='drawing';element('reason').value='Synthetic source reviewed';element('confirm').checked=true;
 let handler=async url=>{if(url==='/api/portfolio')return {variants_scanned:3,requires_review:0,drafts_ready:1,safe_variants:2,items:[]};throw Error('Unexpected request '+url);};
 const context=vm.createContext({document:{getElementById:element,createElement(){return {click(){downloads.push(this.download);}};}},
 navigator:{clipboard:{async writeText(text){clips.push(text);}}},alert:text=>alerts.push(text),
 fetch:async(url,opts)=>({ok:true,json:async()=>handler(url,opts)}),
 Blob:class{constructor(parts){this.parts=parts;}},URL:{createObjectURL(blob){context.lastBlob=blob;return 'blob:synthetic';},revokeObjectURL(){}},
 setTimeout(){},console});
 vm.runInContext(source,context);
 return {context,element,alerts,clips,downloads,setHandler(fn){handler=fn;},run(code){return vm.runInContext(code,context);}};
}
async function main(){
 const h=harness(), old=report('REVIEW_REQUIRED',null,null), next=report('FAIL','drawing','Use approved 30.48 cm limit');
 h.run('report='+JSON.stringify(old)+';reportInputs=payload();');
 h.setHandler(async url=>url==='/api/decide'?{decision_id:'decision-1',result:next}:{variants_scanned:3,requires_review:0,drafts_ready:1,safe_variants:2,items:[]});
 await h.run('approve()');await h.run('copyCorrectionDrafts()');
 assert.equal(h.clips.length,1,'Approved drafts must be immediately available without reloading');
 assert.match(h.clips[0],/Use approved 30.48 cm limit/);
 await h.run('exportDraft()');
 assert.equal(JSON.parse(h.context.lastBlob.parts[0]).result.authority_id,'drawing','Export must use approved report');
 h.element('mattress').value='31';await h.run('exportDraft()');
 assert.equal(h.downloads.length,1,'Changed inputs must block stale export');
 assert.match(h.alerts.at(-1),/Inputs changed/);
 const racing=harness();racing.run('report='+JSON.stringify(old)+';reportInputs=payload();');
 let release;const pending=new Promise(resolve=>{release=resolve;});
 racing.setHandler(async()=>pending);
 const approval=racing.run('approve()');
 racing.element('variant').value='deep-r3';
 racing.run('analysisSequence++;report='+JSON.stringify(report('PASS','deep',null))+';reportInputs=payload();');
 release({decision_id:'late',result:next});await approval;
 assert.equal(racing.run('report.authority_id'),'deep','Late decision response must not overwrite another variant');
 console.log('Client regression checks passed: approved copy/export, changed-input guard, late-response isolation.');
}
main().catch(error=>{console.error(error);process.exitCode=1;});
