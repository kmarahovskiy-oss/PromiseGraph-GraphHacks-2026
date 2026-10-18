"""Authentic browser demo; real FalkorDB is required, no mocks or fake screenshots."""
from pathlib import Path
import os, subprocess, sys, time, json, urllib.request, shutil
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'artifacts'/'real-graph-demo'
OUT.mkdir(parents=True,exist_ok=True)
URL='http://127.0.0.1:8765'
env=os.environ.copy()
env.pop('FALKORDB_MODE',None)
env.update(FALKORDB_HOST='127.0.0.1',FALKORDB_PORT='6379')
server=subprocess.Popen([sys.executable,'-m','uvicorn','promisegraph.app:app','--host',
                          '127.0.0.1','--port','8765','--workers','1'],cwd=ROOT,env=env)
try:
    health=None
    for i in range(45):
        try:
            health=json.load(urllib.request.urlopen(URL+'/api/health',timeout=2))
            if health['source']!='real_graph' or health['nodes']<1:
                raise RuntimeError('Not a real FalkorDB graph')
            break
        except Exception:time.sleep(1)
    if health is None:raise RuntimeError('Real FalkorDB startup failed')
    with sync_playwright() as p:
        browser=p.chromium.launch()
        context=browser.new_context(viewport={'width':1440,'height':900},
            record_video_dir=str(OUT),record_video_size={'width':1440,'height':900})
        page=context.new_page()
        page.goto(URL,wait_until='domcontentloaded')
        expect(page.locator('#status')).to_contain_text('SOURCE CONFLICT',timeout=20000)
        page.evaluate("""() => {
            const x=document.createElement('div');x.id='filmCaption';
            Object.assign(x.style,{position:'fixed',bottom:'20px',left:'20px',zIndex:'100000',
            padding:'16px 22px',background:'rgba(7,26,25,.97)',border:'2px solid #a1f4c7',
            borderRadius:'10px',font:'bold 22px Arial',color:'#fff',pointerEvents:'none'});
            document.body.appendChild(x);
        }""")
        def scene(msg,secs=6):
            page.evaluate('(t)=>document.getElementById("filmCaption").textContent=t',msg)
            time.sleep(secs)
        scene('PromiseGraph — trace a bad product promise to its sources',8)
        page.locator('#scenarios').scroll_into_view_if_needed()
        scene('Two conflicting sources — two DIFFERENT possible outcomes',8)
        page.locator('#newtext').fill('Synthetic supplier update. Maximum total mattress-and-topper height: 32 cm.')
        page.locator('#preview').click()
        expect(page.locator('#previewNote')).to_contain_text('NOT stored')
        scene('A NEW text excerpt is parsed and checked, without saving it',8)
        page.locator('#check').click()
        expect(page.locator('#status')).to_contain_text('SOURCE CONFLICT')
        page.locator('#review').scroll_into_view_if_needed()
        scene('Human source review: the system never silently guesses',7)
        page.locator('#authority').select_option('e-standard-drawing')
        page.locator('#reason').fill('The engineering drawing is authoritative for this fictional review.')
        page.locator('#confirm').check()
        page.locator('#approve').click()
        expect(page.locator('#status')).to_contain_text('UNSUPPORTED CLAIM')
        scene('Reviewer decision SAVED in real FalkorDB',8)
        page.locator('#claims').scroll_into_view_if_needed()
        scene('Two dependent claims need draft corrections. No autopublish.',9)
        page.locator('#paths').click()
        scene('Graph paths connect exact variant, claim and publication',7)
        page.locator('#history').click()
        scene('Decision history comes from the graph, not preset text',7)
        page.locator('#variant').select_option('deep-r3')
        page.locator('#mattress').fill('34')
        page.locator('#topper').fill('4')
        page.locator('#check').click()
        expect(page.locator('#status')).to_contain_text('DOCUMENTED FIT')
        scene('A different variant remains valid and unchanged',8)
        scene('PromiseGraph · Evidence before promises · Synthetic data',7)
        page.screenshot(path=str(OUT/'real-demo-screenshot.png'),full_page=True)
        movie=page.video
        context.close()
        browser.close()
        shutil.move(movie.path(),str(OUT/'real-browser.webm'))
    speech=('One wrong specification can spread to multiple product pages and quotations. '
      'PromiseGraph uses real FalkorDB relationships to find conflicting evidence for the exact product variant. '
      'The graph shows the downstream consequences of each possible decision without guessing which source is correct. '
      'A new source excerpt can also be checked safely without writing to the shared database. '
      'When documents conflict, a human must choose the authoritative source and record the reason. '
      'That decision is saved in FalkorDB. Two affected customer-facing claims receive draft corrections, '
      'while an unrelated product variant remains unchanged. Nothing is published automatically. '
      'Every example here is synthetic. Built using disclosed AI coding assistance.')
    subprocess.run(['espeak-ng','-v','en-gb','-s','155','-w',str(OUT/'voice.wav'),speech],check=True)
    subprocess.run(['ffmpeg','-y','-i',str(OUT/'real-browser.webm'),'-i',str(OUT/'voice.wav'),
                    '-filter_complex','[1:a]apad[a]','-map','0:v','-map','[a]',
                    '-c:v','libx264','-preset','veryfast','-crf','25','-pix_fmt','yuv420p',
                    '-c:a','aac','-b:a','128k','-shortest',
                    str(OUT/'PromiseGraph_Real_Demo_Narrated.mp4')],check=True)
    (OUT/'run-evidence.json').write_text(json.dumps(health,indent=2))
    print('REAL FALKORDB VERIFIED; NARRATED VIDEO CREATED')
finally:
    server.terminate()
    try:server.wait(timeout=8)
    except subprocess.TimeoutExpired:server.kill()
