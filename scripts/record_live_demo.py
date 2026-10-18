"""Authentic browser demo; real FalkorDB is required, no mocks or fake screenshots."""
from pathlib import Path
import os, subprocess, sys, time, json, urllib.request, shutil, tempfile
from gtts import gTTS
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
        # Same live graph and browser: verify the new automatic portfolio workflow.
        expect(page.locator('#portfolioSummary')).to_contain_text('3 variants checked',timeout=20000)
        expect(page.locator('button[data-variant]')).to_have_count(3,timeout=20000)
        story=page.request.get(URL+'/story',timeout=20000)
        assert story.status_code==200 and 'One bad claim.' in story.text()
        article=page.request.get(URL+'/article',timeout=20000)
        assert article.status_code==200 and 'FalkorDB' in article.text()
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
        # Read-only replay must not erase the stored reviewer decision.
        page.locator('#replay').click()
        expect(page.locator('#status')).to_contain_text('SOURCE CONFLICT')
        expect(page.locator('#previewNote')).to_contain_text('Existing reviewer decisions are preserved')
        page.locator('#history').click()
        expect(page.locator('#details')).to_contain_text('Synthetic',timeout=20000)
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
    # Use the same Google TTS family as the previously approved PactSignal video.
    # Timed separate phrases; no robotic espeak or audio that ends early.
    lines=[
        (2,"A product description can become an expensive promise. PromiseGraph checks the evidence before publication."),
        (10,"Two specifications disagree for the exact product variant. FalkorDB traces both sources."),
        (18,"Paste a new supplier statement. Preview its impact without modifying the graph."),
        (26,"Conflicting sources must not be silently resolved. The agent requests human review."),
        (34,"The engineering drawing is chosen. A reviewer records the reason in FalkorDB."),
        (43,"Two promises need corrections. The supported FAQ is left untouched."),
        (52,"Real graph paths link each product specification to its customer-facing documents."),
        (59,"Here is the saved review history. Future checks can retrieve this decision."),
        (67,"A different product version still passes. Its information stays separate."),
        (75,"PromiseGraph. Traceable evidence, safe corrections, fewer manual checks. Fictional data.")
    ]
    with tempfile.TemporaryDirectory(prefix='promisegraph-gtts-') as tmp:
        root=Path(tmp)
        audio_inputs=[]
        filters=[]
        voice_labels=[]
        recorded_cues=[]
        for i,(offset,phrase) in enumerate(lines):
            mp3=root/f'voice-{i:02d}.mp3'
            for retry in range(4):
                try:
                    # Standard Google English TTS voice, no synthetic robot alternative.
                    gTTS(text=phrase,lang='en',tld='com',slow=False).save(str(mp3))
                    break
                except Exception:
                    if retry==3:raise
                    time.sleep(3*(retry+1))
            probe=subprocess.check_output(['ffprobe','-v','error',
                '-show_entries','format=duration','-of',
                'default=noprint_wrappers=1:nokey=1',str(mp3)],text=True)
            clip_seconds=float(probe.strip())
            audio_inputs.extend(['-i',str(mp3)])
            label=f'g{i}'
            filters.append(f'[{i+1}:a]aresample=48000,'
                f'aformat=sample_fmts=fltp:channel_layouts=stereo,'
                f'adelay={offset*1000}|{offset*1000}[{label}]')
            voice_labels.append(f'[{label}]')
            recorded_cues.append({'start_seconds':offset,'speech':phrase,
                                  'clip_seconds':round(clip_seconds,2)})
        video_seconds=float(subprocess.check_output(['ffprobe','-v','error',
            '-show_entries','format=duration','-of',
            'default=noprint_wrappers=1:nokey=1',
            str(OUT/'real-browser.webm')],text=True).strip())
        filters.append(''.join(voice_labels)
            +f'amix=inputs={len(lines)}:duration=longest:normalize=0,'
            +'acompressor=threshold=-19dB:ratio=2.2:attack=12:release=160,'
            +'loudnorm=I=-8:TP=-0.8:LRA=5,apad,'
            +f'atrim=duration={video_seconds:.3f}[narrated]')
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y',
            '-i',str(OUT/'real-browser.webm'),*audio_inputs,
            '-filter_complex',';'.join(filters),
            '-map','0:v:0','-map','[narrated]',
            '-c:v','libx264','-preset','veryfast','-crf','25',
            '-pix_fmt','yuv420p',
            '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
            '-movflags','+faststart',
            str(OUT/'PromiseGraph_Real_Demo_Narrated.mp4')],check=True)
        (OUT/'voice-settings.json').write_text(json.dumps({
            'source_reference':'PactSignal approved 17 Oct 2026',
            'engine':'Google TTS','language':'English','tld':'com',
            'output':'stereo AAC 48000 Hz; target -8 LUFS, -0.8 dBTP',
            'video_duration_seconds':video_seconds,
            'scenes':recorded_cues
        },indent=2))
    print('GOOGLE_TTS_AUDIO_REPLACED',len(lines),'scenes')
    (OUT/'run-evidence.json').write_text(json.dumps(health,indent=2))
    print('REAL FALKORDB VERIFIED; NARRATED VIDEO CREATED')
finally:
    server.terminate()
    try:server.wait(timeout=8)
    except subprocess.TimeoutExpired:server.kill()
