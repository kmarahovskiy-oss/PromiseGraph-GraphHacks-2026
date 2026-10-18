"""Generate reproducible entirely synthetic demonstration evidence."""
from pathlib import Path
import json
from decimal import Decimal
ROOT=Path(__file__).resolve().parent

def src(id,title,height,unit,variant,uri):
    quote=f'Maximum total mattress-and-topper height: {height} {unit}.'
    body=f'SYNTHETIC DOCUMENT — {title}\nProduct specification\n{quote}\nOther conditions are not covered.'
    start=body.index(quote)
    normalized=str(Decimal(str(height))*{'cm':Decimal('1'),'in':Decimal('2.54')}[unit])
    return {'id':id,'document_id':'doc:'+id,'title':title,'text':body,'uri':uri,
        'value':str(height),'unit':unit,'normalized_cm':normalized,'quote':quote,'start':start,'end':start+len(quote)}

def prom(id, title, required, text):
    return {'id':id,'document_id':'page:'+id,'title':title, 'text':text, 'required_cm':str(required)}

def variant(id,sku,revision,name,limits,promises):
    ctx={'model':'AstraRest 90','sku':sku,'revision':revision,'region':'EU','name':name}
    return {'id':id,'context':ctx,'evidence':limits,'promises':promises}

variants=[
    variant('standard-r3','AR90-STD','R3','AstraRest Standard • R3',[
      src('e-standard-supplier','Supplier catalog, R3',35,'cm','standard','synthetic://supplier/r3'),
      src('e-standard-drawing','Engineering drawing, R3',12,'in','standard','synthetic://drawing/r3')], [
      prom('p-store','Online store • product page',34,'A 30 cm mattress plus a 4 cm topper fits the AstraRest 90 Standard (R3).'),
      prom('p-quote','Sales quotation #Q-104',34,'Confirmed fit for 34 cm combined height on Standard R3.'),
      prom('p-faq','Support FAQ',28,'A 28 cm total stack is suitable for Standard R3.')]),
    variant('deep-r3','AR90-DEEP','R3','AstraRest Deep • R3',[
      src('e-deep','Deep engineering spec, R3',40,'cm','deep','synthetic://drawing/deep')],[
      prom('p-deep','Online store • Deep variant',38,'Deep R3 accommodates 38 cm combined height.')]),
    variant('standard-r2','AR90-STD','R2','AstraRest Standard • R2',[
      src('e-standard-old','Archived spec, R2',36,'cm','old','synthetic://archive/r2')],[
      prom('p-old','Archived listing • R2',34,'Previous revision R2 supports 34 cm.')])
]
(ROOT/'demo.json').write_text(json.dumps({'schema':'promisegraph-demo-v2','synthetic':True,'variants':variants},ensure_ascii=False,indent=2), encoding='utf-8')
print('Wrote:',ROOT/'demo.json',len(variants),'variants')
