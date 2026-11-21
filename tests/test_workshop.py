"""Browser, fold-geometry, and PDF regression checks against a plain static server."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import re
import threading
import unittest
import zlib

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


class WorkshopTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(QuietHandler, directory=str(ROOT)))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch()

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1440, 'height': 1100})
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        self.page.goto(self.url + "/#manual")
        self.ready()

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def ready(self):
        expect(self.page.locator('#download')).to_be_enabled(timeout=30000)

    def test_settings_and_assembly_tabs_preserve_controls_and_keyboard_navigation(self):
        settings = self.page.get_by_role('tab', name='Settings', exact=True)
        assembly = self.page.get_by_role('tab', name='Instructions', exact=True)
        expect(settings).to_have_attribute('aria-selected', 'true')
        expect(self.page.locator('#assembly-panel')).to_be_hidden()
        self.page.locator('#ranks').select_option('3')
        self.ready()
        assembly.click()
        expect(self.page.locator('#settings-panel')).to_be_hidden()
        expect(self.page.locator('#fold-diagram svg')).to_be_visible()
        self.assertEqual(self.page.locator('#assembly li').count(), 7)
        expect(self.page.locator('#download')).to_be_enabled()
        assembly.press('ArrowLeft')
        expect(settings).to_be_focused()
        expect(self.page.locator('#ranks')).to_have_value('3')
        settings.press('End')
        expect(assembly).to_be_focused()
        assembly.press('Home')
        expect(settings).to_be_focused()
        self.page.set_viewport_size({'width': 390, 'height': 844})
        assembly.click()
        expect(self.page.locator('#fold-diagram svg')).to_be_visible()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_packing_reuses_gaps_and_preserves_spacing_and_captions(self):
        result = self.page.evaluate('''async () => {
          const {pack}=await import('./src/packing.js');
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          // The old row packer needed two sheets: two short pieces can instead
          // share a column beside this tall piece.
          const example=pack([{name:'Tall',width:60,height:200},
            {name:'Short A',width:120,height:90},{name:'Short B',width:120,height:90}]);
          const mixed=layoutSetup({...defaultSetup(),labelPlacement:'separate',nameplates:true,cavalryBaseDepth:40,
            quantities:{'gondor-horse':8,'gondor-swords':12,'orc-troll':4,'rohan-eowyn':4}});
          let seed=731;
          const random=()=>{seed=(Math.imul(seed,1664525)+1013904223)>>>0;return seed/4294967296};
          const layouts=[];
          for(const paper of ['letter','a4'])for(const orientation of ['portrait','landscape'])
            for(const [margin,gap] of [[5,2],[10,4],[25,10]]) {
              const items=Array.from({length:60},(_,id)=>({id,name:'Piece '+id,
                width:20+Math.floor(random()*60),height:4+Math.floor(random()*100)}));
              const settings={paper,orientation,margin,gap},l=pack(items,settings);
              layouts.push({width:l.width,height:l.height,margin,gap,
                deterministic:JSON.stringify(l)===JSON.stringify(pack(items,settings)),
                pages:l.pages.map(p=>p.map(a=>({id:a.id,x:a.x,y:a.y,w:a.width,h:a.height,captionY:a.captionY})))});
            }
          return {example:example.pages.length,mixed:mixed.pages.length,layouts,empty:pack([]).pages.length};
        }''')
        self.assertEqual(result['example'], 1)
        self.assertLessEqual(result['mixed'], 4)  # Previously five Letter sheets.
        self.assertEqual(result['empty'], 0)
        for layout in result['layouts']:
            self.assertTrue(layout['deterministic'])
            self.assertEqual(sorted(a['id'] for p in layout['pages'] for a in p), list(range(60)))
            for page in layout['pages']:
                for i, a in enumerate(page):
                    self.assertGreaterEqual(a['x'], layout['margin'] - 1e-6)
                    self.assertGreaterEqual(a['y'] - 4, layout['margin'] + 9 - 1e-6)
                    self.assertLessEqual(a['x'] + a['w'], layout['width'] - layout['margin'] + 1e-6)
                    self.assertLessEqual(a['y'] + a['h'], layout['height'] - layout['margin'] - 9 + 1e-6)
                    self.assertAlmostEqual(a['captionY'], a['y'] - 1.5)
                    for b in page[i + 1:]:
                        separated = (a['x'] + a['w'] + layout['gap'] <= b['x'] + 1e-6 or
                                     b['x'] + b['w'] + layout['gap'] <= a['x'] + 1e-6 or
                                     a['y'] + a['h'] + layout['gap'] <= b['y'] - 4 + 1e-6 or
                                     b['y'] + b['h'] + layout['gap'] <= a['y'] - 4 + 1e-6)
                        self.assertTrue(separated)

    def test_fake_ground_shadows_profiles_alpha_geometry_pdf_and_storage(self):
        expect(self.page.locator('#fake-shadows')).not_to_be_checked()
        self.page.locator('#fake-shadows').check()
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.assertTrue(json.loads(payload)['paper']['fakeShadows'])
        self.page.locator('#fake-shadows').uncheck()
        self.page.locator('#load-file').set_input_files({'name': 'shadows.json', 'mimeType': 'application/json', 'buffer': payload})
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#fake-shadows')).to_be_checked()
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup,validateSetup}=await import('./src/model.js');
          const {prepareArtwork,pageScene,createPDF,previewSVG,groundShadows}=await import('./src/render.js');
          const legacy=defaultSetup();delete legacy.fakeShadows;
          let invalid=false;try{validateSetup({...defaultSetup(),fakeShadows:'yes'})}catch{invalid=true}
          const results=[];
          for(const depth of [20,40])for(const riders of [2,4]) {
            const setup={...defaultSetup(),fakeShadows:true,cavalryBaseDepth:depth,riders,
              figureBackground:'gradient',nameplates:true,labelPlacement:'attached',names:{'rohan-foot-captain':'Captain'},
              quantities:{'gondor-horse':1,'rohan-eowyn':1,'rohan-foot-captain':1,'gondor-swords':1,'orc-troll':1}};
            const layout=layoutSetup(setup),assets=await prepareArtwork(layout);
            const off=layoutSetup({...setup,fakeShadows:false});
            const strips=[];
            for(const [i,page] of layout.pages.entries()) {
              const ops=pageScene(layout,i);
              for(const s of page) {
                if(s.kind==='nameplate')continue;
                const shadowOps=ops.filter(o=>o.key?.startsWith('shadow:')&&o.x===s.x+(s.bodyX||0)&&o.y>=s.y&&o.y<s.y+s.height);
                const grounds=s.sections.filter(g=>g.kind==='ground');
                const shapes=grounds.flatMap(g=>groundShadows(s,g));
                strips.push({eligible:['Mounted','Infantry'].includes(s.art.kind),mounted:s.art.kind==='Mounted',count:s.count,shadows:shadowOps.length,
                  within:shadowOps.every(o=>o.w===s.bodyWidth&&grounds.some(g=>o.y>=s.y+(s.bodyY||0)+g.y&&o.y+o.h<=s.y+(s.bodyY||0)+g.y+g.height)),
                  squashed:shadowOps.every(o=>o.h< s.panelHeight&&(s.art.kind==='Mounted'?o.h<=s.panelHeight*.8:o.h<=2.5)),
                  oneDirection:shapes.every(a=>a.flipped)&&groundShadows(s,grounds[0]).length===0,
                  fillsSpace:grounds.filter(g=>g.y>0).every(g=>groundShadows(s,g).every(a=>a.height>=g.height*.75))});
              }
            }
            const sample=[...assets.values()].find(a=>a.key.startsWith('shadow:'));
            const im=new Image();im.src=sample.url;await im.decode();
            const c=document.createElement('canvas');c.width=im.width;c.height=im.height;
            const ctx=c.getContext('2d');ctx.drawImage(im,0,0);
            const data=ctx.getImageData(0,0,c.width,c.height).data;
            let visible=0,clear=0,maxAlpha=0,wrongRGB=0;
            for(let i=0;i<data.length;i+=4) {
              if(data[i+3]) {visible++;wrongRGB+=Number(data[i]!==0||data[i+1]!==0||data[i+2]!==0)}else clear++;
              maxAlpha=Math.max(maxAlpha,data[i+3]);
            }
            const bytes=await createPDF(layout,assets),pdf=await PDFLib.PDFDocument.load(bytes);
            results.push({strips,visible,clear,maxAlpha,wrongRGB,pages:pdf.getPageCount(),expected:layout.pages.length,
              preview:layout.pages.some((_,i)=>previewSVG(layout,i,assets).includes(sample.url)),
              sameBounds:JSON.stringify(layout.pages.map(p=>p.map(s=>[s.x,s.y,s.width,s.height])))===JSON.stringify(off.pages.map(p=>p.map(s=>[s.x,s.y,s.width,s.height]))),
              off:off.pages.some((_,i)=>pageScene(off,i).some(o=>o.key?.startsWith('shadow:')))});
          }
          return {results,legacy:validateSetup(legacy).fakeShadows,invalid};
        }''')
        self.assertFalse(result['legacy'])
        self.assertTrue(result['invalid'])
        for layout in result['results']:
            self.assertTrue(layout['sameBounds'])
            self.assertFalse(layout['off'])
            self.assertTrue(layout['preview'])
            self.assertEqual(layout['pages'], layout['expected'])
            self.assertGreater(layout['visible'], 100)
            self.assertGreater(layout['clear'], 100)
            self.assertGreater(layout['maxAlpha'], 60)
            self.assertLessEqual(layout['maxAlpha'], 72)
            self.assertEqual(layout['wrongRGB'], 0)
            for strip in layout['strips']:
                self.assertTrue(strip['within'])
                self.assertTrue(strip['squashed'])
                self.assertEqual(strip['shadows'], strip['count'] * (1 if strip['mounted'] else 2) if strip['eligible'] else 0)
                if strip['mounted']:
                    self.assertTrue(strip['oneDirection'])
                    self.assertTrue(strip['fillsSpace'])

    def test_letter_square_cavalry_and_new_settings_round_trip(self):
        expect(self.page.locator('#paper')).to_have_value('letter')
        self.page.locator('#cavalry-base-depth').select_option('30')
        self.page.locator('#monstrosity-base-depth').select_option('40')
        self.page.locator('#figure-background').select_option('gradient')
        self.page.locator('#gradient-bottom').fill('#345678')
        self.page.locator('#gradient-top').fill('#effaff')
        self.page.locator('#nameplates').check()
        self.page.locator('#label-placement').select_option('attached')
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.page.locator('#cavalry-base-depth').select_option('20')
        self.page.locator('#load-file').set_input_files({'name': 'options.json', 'mimeType': 'application/json', 'buffer': payload})
        self.ready()
        self.page.reload()
        self.ready()
        for selector, value in [('#cavalry-base-depth', '30'), ('#monstrosity-base-depth', '40'), ('#figure-background', 'gradient'),
                                ('#gradient-bottom', '#345678'), ('#gradient-top', '#effaff'),
                                ('#label-placement', 'attached')]:
            expect(self.page.locator(selector)).to_have_value(value)
        result = self.page.evaluate('''async () => {
          const {defaultSetup,validateSetup,makeStrip}=await import('./src/model.js');
          const {catalog}=await import('./src/catalog.js');
          const legacy=defaultSetup();legacy.paper='a4';
          for(const k of ['cavalryBaseDepth','monstrosityBaseDepth','figureBackground','gradientBottom','gradientTop','labelPlacement'])delete legacy[k];
          const restored=validateSetup(legacy), s={...defaultSetup(),cavalryBaseDepth:40};
          const cav=makeStrip(catalog.find(a=>a.kind==='Mounted'&&!a.hero),s);
          return {legacy:restored, cavalry:[cav.baseWidth,cav.baseDepth,cav.width,cav.height,cav.pitch],
            heroes:catalog.filter(a=>a.hero).map(a=>{const x=makeStrip(a,s);return [x.baseWidth,x.baseDepth,x.count]})};
        }''')
        self.assertEqual(result['cavalry'], [40, 40, 40, 208, 10])
        self.assertTrue(all(h == [20, 20, 1] for h in result['heroes']))
        self.assertEqual(result['legacy']['paper'], 'a4')
        self.assertEqual(result['legacy']['cavalryBaseDepth'], 20)
        self.assertEqual(result['legacy']['monstrosityBaseDepth'], 20)
        self.assertEqual(result['legacy']['figureBackground'], 'solid')
        self.assertEqual(result['legacy']['labelPlacement'], 'rear')

    def test_middle_earth_default_battle_roles(self):
        for unit, role in {'gondor-rangers': 'Skirmishers', 'mordor-trackers': 'Skirmishers',
                           'isengard-dunlending-javelinmen': 'Skirmishers',
                           'rohan-outriders': 'Light Riders', 'harad-cavalry': 'Light Riders',
                           'orc-warg-archers': 'Light Riders', 'goblin-spears': 'Warriors',
                           'gondor-archers': 'Warriors', 'isengard-uruk-crossbows': 'Warriors',
                           'rohan-guard': 'Heavy Riders', 'isengard-warg-riders': 'Heavy Riders'}.items():
            expect(self.page.locator(f'#type-{unit}')).to_have_value(role)
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, validateSetup, unitTypeOptions, makeStrip} = await import('./src/model.js');
          const setup = defaultSetup();
          const complete = catalog.filter(a => a.era === 'middle-earth-third-age' && unitTypeOptions(a).length)
            .every(a => unitTypeOptions(a).includes(a.defaultUnitType));
          setup.unitTypes['gondor-rangers'] = 'Warriors';
          delete setup.unitTypes['rohan-outriders'];
          const restored = validateSetup(setup);
          const ranger = catalog.find(a => a.id === 'gondor-rangers');
          const outrider = catalog.find(a => a.id === 'rohan-outriders');
          return {complete, ranger: restored.unitTypes[ranger.id],
            outrider: restored.unitTypes[outrider.id],
            counts: [makeStrip(ranger, defaultSetup()).count, makeStrip(outrider, restored).count]};
        }''')
        self.assertTrue(result['complete'])
        self.assertEqual(result['ranger'], 'Warriors')
        self.assertEqual(result['outrider'], 'Light Riders')
        self.assertEqual(result['counts'], [1, 3])

    def test_per_unit_battle_roles_formations_persistence_and_pdf(self):
        expect(self.page.locator('#ranks')).to_have_value('2')
        expect(self.page.locator('#skirmisher-ranks')).to_have_value('1')
        expect(self.page.locator('#riders')).to_have_value('4')
        expect(self.page.locator('#light-riders')).to_have_value('3')
        self.assertEqual(self.page.locator('#type-rohan-eowyn').count(), 0)
        self.assertEqual(self.page.locator('#type-orc-troll').count(), 0)
        self.page.locator('#type-gondor-swords').select_option('Skirmishers')
        self.page.locator('#type-gondor-horse').select_option('Light Riders')
        self.page.locator('#skirmisher-ranks').select_option('2')
        self.page.locator('#light-riders').select_option('2')
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.page.locator('#type-gondor-swords').select_option('Warriors')
        self.page.locator('#type-gondor-horse').select_option('Heavy Riders')
        self.page.locator('#load-file').set_input_files({'name': 'roles.json', 'mimeType': 'application/json', 'buffer': payload})
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#type-gondor-swords')).to_have_value('Skirmishers')
        expect(self.page.locator('#type-gondor-horse')).to_have_value('Light Riders')
        expect(self.page.locator('#skirmisher-ranks')).to_have_value('2')
        expect(self.page.locator('#light-riders')).to_have_value('2')
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, validateSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const setup = defaultSetup();
          Object.assign(setup.unitTypes, {'gondor-swords':'Warriors', 'gondor-rangers':'Skirmishers',
            'gondor-horse':'Heavy Riders', 'rohan-outriders':'Light Riders'});
          const ids = ['gondor-swords','gondor-rangers','gondor-horse','rohan-outriders','rohan-eowyn','orc-troll'];
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, ids.includes(a.id) ? 1 : 0]));
          const geometry = s => ids.map(id => {const strip=makeStrip(catalog.find(a=>a.id===id),s);
            return [strip.unitType,strip.count,strip.pitch,strip.sections.filter(p=>p.kind==='ground').reduce((n,p)=>n+p.height,0)];});
          const defaults = geometry(setup);
          const changed = geometry({...setup, ranks:3, skirmisherRanks:2, riders:2, lightRiders:4});
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const pdf = await PDFLib.PDFDocument.load(await createPDF(layout,assets));
          const legacy = {...setup, ranks:3, riders:2};
          delete legacy.unitTypes; delete legacy.skirmisherRanks; delete legacy.lightRiders;
          const restored = validateSetup(legacy);
          const rejected = [];
          for (const patch of [{unitTypes:[]},{unitTypes:{'gondor-swords':'Light Riders'}},
            {unitTypes:{'gondor-horse':'Skirmishers'}},{skirmisherRanks:0},{lightRiders:5}]) {
            try {validateSetup({...setup,...patch});rejected.push(false);} catch {rejected.push(true);}
          }
          return {defaults,changed,legacy:geometry(restored),skirmishers:restored.skirmisherRanks,
            light:restored.lightRiders,rejected,pages:pdf.getPageCount(),expected:layout.pages.length};
        }''')
        self.assertEqual([s[1] for s in result['defaults']], [2, 1, 4, 3, 1, 1])
        self.assertEqual([s[1] for s in result['changed']], [3, 2, 2, 4, 1, 1])
        self.assertEqual([s[1] for s in result['legacy']], [3, 3, 2, 2, 1, 1])
        self.assertEqual([s[3] for s in result['defaults']], [20, 20, 40, 40, 20, 20])
        self.assertEqual(result['defaults'][1][2], 20)
        self.assertAlmostEqual(result['defaults'][3][2], 40 / 3)
        self.assertEqual([result['skirmishers'], result['light']], [1, 3])
        self.assertTrue(all(result['rejected']))
        self.assertEqual(result['pages'], result['expected'])

    def test_optional_cavalry_and_monstrosity_depth_geometry_and_pdf(self):
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, validateSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const runs = [];
          for (const depth of [20, 30, 40]) {
            const setup = {...defaultSetup(), cavalryBaseDepth: depth, monstrosityBaseDepth: depth,
              nameplates: true, labelPlacement: 'attached', riders: 2};
            const selected = ['gondor-horse', 'orc-troll', 'orc-monstrosities', 'gondor-ballista',
              'rohan-eowyn', 'gondor-swords'];
            setup.quantities = Object.fromEntries(catalog.map(a => [a.id, selected.includes(a.id) ? 1 : 0]));
            const strips = catalog.map(a => {
              const s = makeStrip(a, setup), original = makeStrip(a, defaultSetup());
              return {id: a.id, hero: !!a.hero, kind: a.kind, depth: s.baseDepth,
                bodyWidth: s.bodyWidth, bodyHeight: s.bodyHeight,
                ground: s.sections.filter(p => p.kind === 'ground').reduce((n,p) => n+p.height,0),
                count: s.count, originalCount: original.count, panel: s.panelHeight,
                originalPanel: original.panelHeight, tabs: s.wrapTabs};
            });
            const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
            const bytes = await createPDF(layout, assets), pdf = await PDFLib.PDFDocument.load(bytes);
            runs.push({depth, strips, pages: pdf.getPageCount(), expected: layout.pages.length,
              pdf: bytes.length, subject: pdf.getSubject()});
          }
          const rejects = [];
          for (const key of ['cavalryBaseDepth','monstrosityBaseDepth']) {
            for (const value of [25, '30', null]) {
              try {validateSetup({...defaultSetup(), [key]: value}); rejects.push(false);}
              catch {rejects.push(true);}
            }
          }
          return {runs, rejects};
        }''')
        self.assertTrue(all(result['rejects']))
        for run in result['runs']:
            self.assertEqual(run['pages'], run['expected'])
            self.assertGreater(run['pdf'], 1000)
            self.assertIn(f"Monstrosities 40 x {run['depth']} mm", run['subject'])
            for strip in run['strips']:
                expected_depth = run['depth'] if not strip['hero'] and strip['kind'] in ['Mounted', 'Monster'] else 20
                self.assertEqual(strip['depth'], expected_depth)
                if strip['kind'] == 'Monster':
                    self.assertEqual(strip['count'], strip['originalCount'])
                    self.assertEqual(strip['panel'], strip['originalPanel'])
                    self.assertEqual(strip['ground'], run['depth'])
                    self.assertEqual(strip['bodyWidth'], 40)
                    self.assertEqual(strip['bodyHeight'], run['depth'] + 2 * strip['count'] * strip['panel'])
                elif strip['kind'] == 'Mounted':
                    self.assertEqual(strip['bodyWidth'], expected_depth)
                    self.assertEqual(strip['ground'], 20 if strip['hero'] else 40)

    def test_mounted_artwork_size_stays_constant_at_deeper_bases(self):
        result = self.page.evaluate("""async () => {
          const {catalog}=await import('./src/catalog.js');
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF,pageScene,previewSVG}=await import('./src/render.js');
          const ids=['rohan-couched-lancers','orc-lunging-wargs','gondor-horse','rohan-eowyn'];
          const runs=[];
          for(const depth of [20,30,40]) {
            const setup={...defaultSetup(),cavalryBaseDepth:depth,riders:2,fakeShadows:true,
              nameplates:true,labelPlacement:'attached',
              quantities:Object.fromEntries(catalog.map(a=>[a.id,ids.includes(a.id)?1:0]))};
            const layout=layoutSetup(setup),assets=await prepareArtwork(layout),bounds={};
            for(const [key,asset] of assets) {
              if(key.startsWith('shadow:')) continue;
              const image=new Image();image.src=asset.url;await image.decode();
              const c=document.createElement('canvas');c.width=image.width;c.height=image.height;
              const ctx=c.getContext('2d');ctx.drawImage(image,0,0);
              const data=ctx.getImageData(0,0,c.width,c.height).data;
              let left=c.width,right=-1,top=c.height,bottom=-1;
              for(let y=0;y<c.height;y++) for(let x=0;x<c.width;x++) {
                if(data[(y*c.width+x)*4+3]>128) {
                  left=Math.min(left,x);right=Math.max(right,x);top=Math.min(top,y);bottom=Math.max(bottom,y);
                }
              }
              const [id,,height,variant]=key.split(':');
              const width=catalog.find(a=>a.id===id).hero?20:depth;
              bounds[id+':'+variant]={width:(right-left+1)*width/c.width,
                height:(bottom-top+1)*Number(height)/c.height,
                center:(left+right+1)*width/(2*c.width),
                bottomGap:(c.height-bottom-1)*Number(height)/c.height,panelWidth:width};
            }
            const bytes=await createPDF(layout,assets),pdf=await PDFLib.PDFDocument.load(bytes);
            const ops=layout.pages.flatMap((_,i)=>pageScene(layout,i));
            runs.push({depth,bounds,pages:pdf.getPageCount(),expected:layout.pages.length,
              bytes:bytes.length,preview:previewSVG(layout,0,assets).includes('<image'),
              widths:ops.filter(o=>o.key?.startsWith('rohan-couched-lancers:')).map(o=>o.w)});
          }
          return runs;
        }""")
        baseline = result[0]['bounds']
        for run in result:
            self.assertGreater(run['bytes'], 1000)
            self.assertEqual(run['pages'], run['expected'])
            self.assertTrue(run['preview'])
            self.assertTrue(run['widths'])
            self.assertTrue(all(w == run['depth'] for w in run['widths']))
            for key, bounds in run['bounds'].items():
                self.assertAlmostEqual(bounds['width'], baseline[key]['width'], delta=0.1)
                self.assertAlmostEqual(bounds['height'], baseline[key]['height'], delta=0.1)
                self.assertAlmostEqual(bounds['bottomGap'], baseline[key]['bottomGap'], delta=0.1)
                self.assertAlmostEqual(bounds['center'], bounds['panelWidth']/2, delta=0.1)

    def test_gradient_direction_including_blank_reverse_and_pdf(self):
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,pageScene,createPDF,previewSVG}=await import('./src/render.js');
          const l=layoutSetup({...defaultSetup(),figureBackground:'gradient',reverse:'blank',quantities:{'gondor-swords':1}});
          const assets=await prepareArtwork(l), strips=l.pages.flat(), colors=[];
          for(const strip of strips) for(const section of strip.sections.filter(s=>s.kind==='face')) {
            const op=pageScene(l,0).find(o=>o.type==='image'&&o.key.startsWith('gradient:')&&o.y===strip.y+section.y);
            const im=new Image();im.src=assets.get(op.key).url;await im.decode();
            const c=document.createElement('canvas');c.width=im.width;c.height=im.height;
            const ctx=c.getContext('2d');ctx.drawImage(im,0,0);
            colors.push({side:section.side,top:[...ctx.getImageData(0,0,1,1).data].slice(0,3),
              bottom:[...ctx.getImageData(0,c.height-1,1,1).data].slice(0,3)});
          }
          const bytes=await createPDF(l,assets),pdf=await PDFLib.PDFDocument.load(bytes);
          return {colors,pages:pdf.getPageCount(),size:pdf.getPages()[0].getSize(),
            preview:previewSVG(l,0,assets).includes(assets.get(pageScene(l,0).find(o=>o.key?.startsWith('gradient:')).key).url)};
        }''')
        dark, light = [69, 107, 148], [238, 247, 255]
        for panel in result['colors']:
            for actual, expected in [(panel['top'], dark if panel['side'] == 'front' else light),
                                     (panel['bottom'], light if panel['side'] == 'front' else dark)]:
                self.assertTrue(all(abs(a - b) <= 1 for a, b in zip(actual, expected)))
        self.assertTrue(result['preview'])
        self.assertEqual(result['pages'], 1)
        self.assertAlmostEqual(result['size']['width'], 612)
        self.assertAlmostEqual(result['size']['height'], 792)

    def test_attached_label_nets_packing_names_and_pdf(self):
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup,makeStrip}=await import('./src/model.js');
          const {catalog}=await import('./src/catalog.js');
          const {prepareArtwork,pageScene,createPDF}=await import('./src/render.js');
          const results=[];
          for(const depth of [20,30,40]) for(const paper of ['letter','a4']) for(const orientation of ['portrait','landscape']) {
            const s={...defaultSetup(),cavalryBaseDepth:depth,paper,orientation,riders:2,lightRiders:2,nameplates:true,labelPlacement:'attached',
              names:{...Object.fromEntries(catalog.filter(a=>a.hero).map(a=>[a.id,'Hero'])),'gondor-swords':'Guard'},copyNames:{'gondor-swords':['First Guard']},
              quantities:Object.fromEntries(catalog.map(a=>[a.id,1]))};
            const l=layoutSetup(s),assets=await prepareArtwork(l),ops=l.pages.flatMap((_,i)=>pageScene(l,i));
            const bytes=await createPDF(l,assets),pdf=await PDFLib.PDFDocument.load(bytes);
            let overlap=false,outside=false;
            for(const page of l.pages)for(let i=0;i<page.length;i++) {
              const a=page[i];outside ||= a.x+a.width>l.width-l.margin+1e-8||a.y+a.height>l.height-l.margin-9+1e-8;
              for(const b of page.slice(i+1))overlap ||= a.x<b.x+b.width&&b.x<a.x+a.width&&a.y-4<b.y+b.height&&b.y-4<a.y+a.height;
            }
            results.push({overlap,outside,pages:pdf.getPageCount(),expected:l.pages.length,
              labels:l.pages.flat().filter(x=>x.kind==='nameplate').map(x=>({wrap:x.wrap,edge:x.edge,width:x.width,height:x.height,baseWidth:x.art.baseWidth||40})),named:ops.filter(o=>o.value==='First Guard').map(o=>({rotation:o.rotation,size:o.size})),text:ops.filter(o=>o.type==='text').map(o=>o.value),
              strips:l.pages.flat().filter(x=>x.kind!=='nameplate').map(x=>({base:[x.baseWidth,x.baseDepth],mounted:x.art.kind==='Mounted',hero:!!x.art.hero,
                count:x.count,panel:x.panelHeight,ground:x.sections.filter(s=>s.kind==='ground').reduce((n,s)=>n+s.height,0),span:x.span,
                bounds:[x.width-x.bodyWidth,x.height-x.bodyHeight],tabs:x.wrapTabs,bodyX:x.bodyX,bodyY:x.bodyY,
                imageWidths:ops.filter(o=>o.type==='image'&&o.x===x.x&&o.y>=x.y&&o.y<x.y+x.bodyHeight).map(o=>o.w)}))});
          }
          const off=layoutSetup({...defaultSetup(),labelPlacement:'attached'});
          return {results,off:off.pages.flat().some(s=>s.wrapTabs)};
        }''')
        self.assertFalse(result['off'])
        for layout in result['results']:
            self.assertFalse(layout['overlap'])
            self.assertFalse(layout['outside'])
            self.assertEqual(len(layout['labels']), 2 * sum(s['mounted'] for s in layout['strips']))
            for label in layout['labels']:
                self.assertTrue(label['wrap'])
                self.assertIn(label['edge'], ['front', 'back'])
                self.assertEqual(label['height'], 10 if label['edge'] == 'back' else 9)
                self.assertEqual(label['width'], label['baseWidth'])
            self.assertEqual(sorted(n['rotation'] for n in layout['named']), [0, 180])
            self.assertTrue(all(abs(n['size'] * 72 / 25.4 - 6) < 1e-6 for n in layout['named']))
            self.assertEqual(layout['pages'], layout['expected'])
            self.assertIn('First Guard', layout['text'])
            for strip in layout['strips']:
                self.assertAlmostEqual(strip['ground'], strip['span'])
                self.assertEqual(strip['bounds'], [0, 20])
                self.assertEqual(strip['bodyY'], 10)
                self.assertEqual(strip['bodyX'], 0)
                self.assertEqual([t['edge'] for t in strip['tabs']], ['front', 'back'])
                self.assertEqual(len(strip['tabs']), 2)
                for tab, expected_y in zip(strip['tabs'], [0, strip['span'] + 2 * strip['count'] * strip['panel'] + 10]):
                    self.assertEqual(tab['height'], 10)
                    self.assertEqual(tab['width'], strip['base'][1] if strip['mounted'] else strip['base'][0])
                    self.assertEqual(tab['x'], 0)
                    self.assertEqual(tab['y'], expected_y)
                    self.assertFalse(tab['side'])
                if strip['hero']:
                    self.assertEqual(strip['base'], [20, 20])

    def test_era_and_faction_filters_preserve_selected_bases(self):
        eras = self.page.evaluate("async () => (await import('./src/catalog.js')).catalog.map(a => a.era)")
        self.assertEqual(set(eras), {'middle-earth-third-age', 'american-civil-war', 'napoleonic', 'wars-of-the-roses'})
        expect(self.page.locator('#era')).to_have_value('middle-earth-third-age')
        # Simulate a future era to exercise filtering across classifications.
        source = (ROOT / 'src/catalog.js').read_text() + """
          eras.push({id: 'future-era', name: 'Future era'});
          catalog.push({...catalog[0], id: 'future-unit', era: 'future-era'});
        """
        self.page.route('**/src/catalog.js', lambda route: route.fulfill(body=source, content_type='text/javascript'))
        self.page.reload()
        self.ready()
        self.page.locator('[data-filter="Orcs"]').click()
        self.assertEqual(self.page.locator('.art-card:visible:not([data-faction="Orcs"])').count(), 0)
        self.page.locator('#era').select_option('future-era')
        self.assertEqual(self.page.locator('.art-card:visible').count(), 1)
        expect(self.page.locator('[data-art="future-unit"]')).to_be_visible()
        self.assertEqual(self.page.locator('[data-filter="Orcs"]').count(), 0)
        expect(self.page.locator('[data-filter="All"]')).to_have_attribute('aria-pressed', 'true')
        self.assertEqual(self.page.locator('#qty-gondor-swords').input_value(), '1')
        expect(self.page.locator('#base-count')).to_have_text('4 bases')
        self.page.locator('#era').select_option('middle-earth-third-age')
        expect(self.page.locator('[data-art="future-unit"]')).to_be_hidden()
        expect(self.page.locator('[data-art="gondor-swords"]')).to_be_visible()
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))

    def test_american_civil_war_infantry_load_and_export(self):
        self.page.locator('#era').select_option('american-civil-war')
        self.assertEqual(self.page.locator('.art-card:visible').count(), 10)
        self.page.locator('[data-filter="CSA"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 5)
        expect(self.page.locator('[data-art="acw-csa-infantry"]')).to_be_visible()
        self.page.locator('[data-filter="USA"]').click()
        expect(self.page.locator('[data-art="acw-usa-infantry"]')).to_be_visible()
        result = self.page.evaluate("""async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => ['acw-csa-infantry','acw-usa-infantry'].includes(a.id));
          const setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          return {pdf: (await createPDF(layout, assets)).length, assets: assets.size,
            strips: arts.map(a => {const s = makeStrip(a, setup);
              return [s.baseWidth, s.baseDepth, s.count, s.width, s.panelHeight];})};
        }""")
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['assets'], 4)
        self.assertEqual(result['strips'], [[40, 20, 2, 40, 14.5]] * 2)

    def test_napoleonic_infantry_load_and_export(self):
        self.page.locator('#era').select_option('napoleonic')
        self.assertEqual(self.page.locator('.art-card:visible').count(), 2)
        self.page.locator('[data-filter="French"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 1)
        expect(self.page.locator('[data-art="napoleonic-french-line"]')).to_be_visible()
        self.page.locator('[data-filter="Spanish"]').click()
        expect(self.page.locator('[data-art="napoleonic-spanish-line"]')).to_be_visible()
        result = self.page.evaluate("""async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => ['napoleonic-french-line','napoleonic-spanish-line'].includes(a.id));
          const setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          return {pdf: (await createPDF(layout, assets)).length, assets: assets.size,
            strips: arts.map(a => {const s = makeStrip(a, setup);
              return [s.baseWidth, s.baseDepth, s.count, s.width, s.panelHeight];})};
        }""")
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['assets'], 4)
        self.assertEqual(result['strips'], [[40, 20, 2, 40, 14.5]] * 2)

    def test_wars_of_the_roses_load_and_export(self):
        self.page.locator('#era').select_option('wars-of-the-roses')
        self.page.locator('[data-filter="English"]').click()
        expect(self.page.locator('.art-card:visible')).to_have_count(10)
        pages = self.page.evaluate("""async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, Number(a.era === 'wars-of-the-roses')]));
          const layout = layoutSetup(setup);
          const pdf = await createPDF(layout, await prepareArtwork(layout));
          return (await PDFLib.PDFDocument.load(pdf)).getPageCount();
        }""")
        self.assertGreater(pages, 0)

    def test_dynamic_cavalry_artwork_and_pdf_export(self):
        result = self.page.evaluate("""async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const ids = ['orc-lunging-wargs', 'mordor-charging-wargs',
            'rohan-sword-riders', 'gondor-charging-lancers', 'rohan-couched-lancers'];
          const arts = ids.map(id => catalog.find(a => a.id === id));
          const images = await Promise.all(arts.map(a => new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
              const canvas = document.createElement('canvas');
              canvas.width = img.width; canvas.height = img.height;
              const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
              const data = ctx.getImageData(0, 0, img.width, img.height).data;
              let clear = 0, solid = 0;
              for(let i=3; i<data.length; i+=4) {
                if(data[i] === 0) clear++;
                if(data[i] >= 250) solid++;
              }
              resolve({clear, solid});
            };
            img.onerror = reject; img.src = a.path;
          })));
          const exports = [];
          for(const depth of [20, 30, 40]) {
            const setup = {...defaultSetup(), cavalryBaseDepth:depth, nameplates:true,
              quantities:Object.fromEntries(catalog.map(a => [a.id, ids.includes(a.id) ? 1 : 0]))};
            const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
            const bytes = await createPDF(layout, assets);
            const pdf = await PDFLib.PDFDocument.load(bytes);
            exports.push({total:layout.total, bytes:bytes.length,
              pages:pdf.getPageCount(), expected:layout.pages.length});
          }
          return {images, exports, mounted:arts.every(a => a.kind === 'Mounted' && !a.hero),
            originals:['orc-wargs', 'rohan-spears', 'rohan-charging-riders', 'gondor-horse']
              .every(id => catalog.some(a => a.id === id))};
        }""")
        self.assertTrue(result['mounted'])
        self.assertTrue(result['originals'])
        for image in result['images']:
            self.assertGreater(image['clear'], 0)
            self.assertGreater(image['solid'], 0)
        for exported in result['exports']:
            self.assertEqual(exported['total'], 5)
            self.assertGreater(exported['bytes'], 1000)
            self.assertEqual(exported['pages'], exported['expected'])

    def test_mordor_faction_artwork_and_pdf_export(self):
        self.page.locator('[data-filter="Mordor"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 8)
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => a.faction === 'Mordor');
          const images = await Promise.all(arts.map(a => new Promise((resolve, reject) => {
            const img = new Image(); img.onload = () => {
              const canvas = document.createElement('canvas');
              canvas.width = img.width; canvas.height = img.height;
              const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
              const pixels = ctx.getImageData(0, 0, img.width, img.height).data;
              let clear = 0, solid = 0;
              for (let i = 3; i < pixels.length; i += 4) {
                if (pixels[i] === 0) clear++;
                // Generated PNG interiors can be 253/254 rather than exactly 255.
                if (pixels[i] >= 250) solid++;
              }
              resolve({clear, solid, pixels:img.width * img.height});
            }; img.onerror = reject; img.src = a.path;
          })));
          const setup = {...defaultSetup(), nameplates: true};
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const bytes = await createPDF(layout, assets), pdf = await PDFLib.PDFDocument.load(bytes);
          return {images, total: layout.total, assets: assets.size, pdf: bytes.length,
            pages: pdf.getPageCount(), expected: layout.pages.length};
        }''')
        self.assertEqual(result['total'], 8)
        self.assertEqual(result['assets'], 16)
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['pages'], result['expected'])
        for image in result['images']:
            self.assertGreater(image['clear'], 0)
            self.assertGreater(image['solid'], image['pixels'] * 0.1)

    def test_light_troop_expansion_factions_artwork_and_export(self):
        units = {'isengard-dunlending-javelinmen': 'Isengard', 'mordor-trackers': 'Mordor',
                 'rohan-outriders': 'Rohan', 'harad-javelin-skirmishers': 'Harad'}
        for unit_id, faction in units.items():
            self.page.locator(f'[data-filter="{faction}"]').click()
            expect(self.page.locator(f'[data-art="{unit_id}"]')).to_be_visible()
            self.assertEqual(self.page.locator(f'.art-card:visible:not([data-faction="{faction}"])').count(), 0)
        self.assertEqual(self.page.locator('#qty-gondor-swords').input_value(), '1')
        result = self.page.evaluate('''async ids => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = ids.map(id => catalog.find(a => a.id === id));
          const images = await Promise.all(arts.map(a => new Promise((resolve, reject) => {
            const img = new Image(); img.onload = () => {
              const canvas = document.createElement('canvas');
              canvas.width = img.width; canvas.height = img.height;
              const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
              const pixels = ctx.getImageData(0, 0, img.width, img.height).data;
              let clear = 0, solid = 0;
              for (let i = 3; i < pixels.length; i += 4) {
                if (pixels[i] === 0) clear++;
                if (pixels[i] === 255) solid++;
              }
              resolve({clear, solid});
            }; img.onerror = reject; img.src = a.path;
          })));
          const setup = {...defaultSetup(),labelPlacement:'separate', riders: 2, nameplates: true};
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const bytes = await createPDF(layout, assets), pdf = await PDFLib.PDFDocument.load(bytes);
          const mounted = arts.find(a => a.kind === 'Mounted');
          const spacing = [2, 4].map(riders => {
            const s = makeStrip(mounted, {...setup, lightRiders: riders}); return [s.count, s.pitch];
          });
          return {images, total: layout.total, assets: assets.size, pdf: bytes.length, spacing,
            pages: pdf.getPageCount(), expected: layout.pages.length,
            strips: arts.map(a => {const s = makeStrip(a, setup);
              return {kind: a.kind, base: [s.baseWidth, s.baseDepth], count: s.count,
                backs: s.sections.filter(p => p.side === 'back').map(p => p.variant)};})};
        }''', list(units))
        self.assertEqual(result['total'], 4)
        self.assertEqual(result['assets'], 8)
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['pages'], result['expected'])
        self.assertEqual(result['spacing'], [[2, 20], [4, 10]])
        for image in result['images']:
            self.assertGreater(image['clear'], 0)
            self.assertGreater(image['solid'], 0)
        for strip, count in zip(result['strips'], [1, 1, 3, 1]):
            self.assertEqual(strip['base'], [40, 20])
            self.assertEqual(strip['count'], count)
            self.assertEqual(strip['backs'], ['mirror' if strip['kind'] == 'Mounted' else 'silhouette'] * count)

    def test_goblin_faction_light_troops_load_and_export(self):
        self.page.locator('[data-filter="Goblins"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 3)
        self.assertEqual(self.page.locator('.art-card:visible:not([data-faction="Goblins"])').count(), 0)
        for unit_id in ['goblin-archers', 'goblin-spears', 'goblin-warg-riders']:
            expect(self.page.locator(f'[data-art="{unit_id}"]')).to_be_visible()
        self.assertEqual(self.page.locator('#qty-gondor-swords').input_value(), '1')
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => a.faction === 'Goblins');
          const images = await Promise.all(arts.map(a => new Promise((resolve, reject) => {
            const img = new Image(); img.onload = () => {
              const canvas = document.createElement('canvas');
              canvas.width = img.width; canvas.height = img.height;
              const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
              const pixels = ctx.getImageData(0, 0, img.width, img.height).data;
              let clear = 0, solid = 0;
              for (let i = 3; i < pixels.length; i += 4) {
                if (pixels[i] === 0) clear++;
                if (pixels[i] === 255) solid++;
              }
              resolve({clear, solid});
            }; img.onerror = reject; img.src = a.path;
          })));
          const setup = {...defaultSetup(), riders: 2};
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const bytes = await createPDF(layout, assets), pdf = await PDFLib.PDFDocument.load(bytes);
          return {images, total: layout.total, assets: assets.size, pdf: bytes.length,
            pages: pdf.getPageCount(), expected: layout.pages.length,
            strips: arts.map(a => {const s = makeStrip(a, setup);
              return {kind: a.kind, base: [s.baseWidth, s.baseDepth], count: s.count,
                backs: s.sections.filter(p => p.side === 'back').map(p => p.variant)};})};
        }''')
        self.assertEqual(result['total'], 3)
        self.assertEqual(result['assets'], 6)
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['pages'], result['expected'])
        for image in result['images']:
            self.assertGreater(image['clear'], 0)
            self.assertGreater(image['solid'], 0)
        for strip, count in zip(result['strips'], [1, 2, 3]):
            self.assertEqual(strip['base'], [40, 20])
            self.assertEqual(strip['count'], count)
            self.assertEqual(strip['backs'], ['mirror' if strip['kind'] == 'Mounted' else 'silhouette'] * count)

    def test_gondor_light_units_load_and_export(self):
        self.page.locator('[data-filter="Gondor"]').click()
        for unit_id in ['gondor-militia', 'gondor-rangers']:
            expect(self.page.locator(f'[data-art="{unit_id}"]')).to_be_visible()
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => ['gondor-militia', 'gondor-rangers'].includes(a.id));
          const loaded = await Promise.all(arts.map(a => new Promise((resolve, reject) => {
            const img = new Image(); img.onload = () => resolve(img.naturalWidth > 0);
            img.onerror = reject; img.src = a.path;
          })));
          const setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, arts.includes(a) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const bytes = await createPDF(layout, assets);
          const pdf = await PDFLib.PDFDocument.load(bytes);
          return {loaded, assets: assets.size, pdf: bytes.length, pages: pdf.getPageCount(),
            expected: layout.pages.length, strips: arts.map(a => {
              const s = makeStrip(a, setup); return [s.baseWidth, s.baseDepth, s.count, s.panelHeight];
            })};
        }''')
        self.assertEqual(result['loaded'], [True, True])
        self.assertEqual(result['assets'], 4)
        self.assertGreater(result['pdf'], 1000)
        self.assertEqual(result['pages'], result['expected'])
        self.assertEqual(result['strips'], [[40, 20, 2, 14.5], [40, 20, 1, 14.5]])

    def test_middle_earth_expansion_artwork_and_foot_heroes_export(self):
        ids = ['isengard-warg-riders', 'rohan-foot-captain', 'mordor-spearmen',
               'mordor-morannon', 'mordor-banner-bearer', 'mordor-warboss', 'mordor-catapult',
               'gondor-foot-captain', 'harad-spearmen', 'harad-archers',
               'harad-cavalry', 'gondor-aragorn-foot', 'mordor-cave-troll']
        result = self.page.evaluate('''async ids => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const setup = {...defaultSetup(),labelPlacement:'separate', ranks: 3, riders: 2, nameplates: true};
          setup.names = {'rohan-foot-captain': 'Rohan captain', 'mordor-banner-bearer': 'Mordor herald',
            'gondor-foot-captain': 'Gondor captain', 'gondor-aragorn-foot': 'Aragorn'};
          setup.quantities = Object.fromEntries(catalog.map(a => [a.id, ids.includes(a.id) ? 1 : 0]));
          const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
          const bytes = await createPDF(layout, assets), pdf = await PDFLib.PDFDocument.load(bytes);
          return {total: layout.total, assets: assets.size, pages: pdf.getPageCount(),
            expected: layout.pages.length, labels: layout.pages.flat().filter(l => l.kind === 'nameplate').map(l => [l.width, l.height]),
            strips: layout.pages.flat().filter(s => s.kind !== 'nameplate').map(s => ({id: s.art.id, hero: !!s.art.hero,
              kind: s.art.kind, width: s.width, baseWidth: s.baseWidth, baseDepth: s.baseDepth,
              count: s.count, panel: s.panelHeight, preserve: !!s.art.preserveAspect}))};
        }''', ids)
        self.assertEqual(result['total'], len(ids))
        self.assertEqual(result['assets'], 2 * len(ids))
        self.assertEqual(result['pages'], result['expected'])
        self.assertEqual(len(result['labels']), len(ids))
        for strip in result['strips']:
            if strip['hero']:
                self.assertEqual(strip['kind'], 'Infantry')
                self.assertEqual([strip['baseWidth'], strip['baseDepth'], strip['width'], strip['count']], [20, 20, 20, 1])
                self.assertTrue(strip['preserve'])
            elif strip['kind'] == 'Monster':
                self.assertEqual(strip['count'], 1)
                self.assertTrue(strip['preserve'])
                self.assertEqual(strip['panel'], 35 if strip['id'] == 'mordor-cave-troll' else 23)
            else:
                self.assertEqual(strip['count'], (3 if strip['id'] == 'harad-cavalry' else 2) if strip['kind'] == 'Mounted' else 3)
        self.assertEqual(result['labels'].count([18, 4]), 5)

    def test_flat_feet_geometry_and_perpendicular_axes(self):
        result = self.page.evaluate('''async () => {
          const {defaultSetup, makeStrip} = await import('./src/model.js');
          const {catalog} = await import('./src/catalog.js');
          const out = [];
          for (let ranks=1; ranks<=4; ranks++) for (let riders=2; riders<=4; riders++) {
            const setup = {...defaultSetup(), ranks, riders};
            for (const art of catalog) {
              const s=makeStrip(art,setup);
              out.push({hero:!!art.hero,kind:art.kind,width:s.width,span:s.span,count:s.count,height:s.height,
                panelHeight:s.panelHeight,ground:s.sections.filter(x=>x.kind==='ground').reduce((n,x)=>n+x.height,0),
                mountain:s.folds.filter(x=>x.kind==='mountain').length,valley:s.folds.filter(x=>x.kind==='valley').length,
                contiguous:s.sections.every((x,i)=>i===0?x.y===0:Math.abs(x.y-s.sections[i-1].y-s.sections[i-1].height)<1e-7),
                variants:s.sections.filter(x=>x.side==='back').map(x=>x.variant)});
            }
          }
          return out;
        }''')
        for s in result:
            mounted = s['kind'] == 'Mounted'
            self.assertEqual(s['width'], 20 if mounted or s['hero'] else 40)
            self.assertAlmostEqual(s['ground'], 20 if s['hero'] else 40 if mounted else 20)
            self.assertAlmostEqual(s['height'], s['ground'] + 2 * s['count'] * s['panelHeight'])
            self.assertEqual(s['mountain'], s['count'])
            self.assertEqual(s['valley'], 2 * s['count'])
            self.assertTrue(s['contiguous'])
            self.assertEqual(set(s['variants']), {'mirror' if mounted else 'silhouette'})

    def test_giant_fixed_tall_panel_and_export(self):
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const art = catalog.find(a=>a.id==='orc-troll'), setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a=>[a.id,a===art?1:0]));
          setup.nameplates = true; setup.labelPlacement = 'separate';
          const strips = [1,2,4].flatMap(ranks=>[10,14.5,30].map(infantryHeight=>{
            const s=makeStrip(art,{...setup,ranks,infantryHeight});
            return {base:[s.baseWidth,s.baseDepth],width:s.width,height:s.height,count:s.count,
              panelHeight:s.panelHeight,ground:s.sections.filter(x=>x.kind==='ground').reduce((n,x)=>n+x.height,0)};
          }));
          const exports = [];
          for (const reverse of ['silhouette','blank']) {
            const layout=layoutSetup({...setup,reverse}), assets=await prepareArtwork(layout);
            exports.push({pdf:(await createPDF(layout,assets)).length,assets:assets.size,
              label:layout.pages.flat().find(s=>s.kind==='nameplate').width,
              back:layout.pages.flat().find(s=>s.kind!=='nameplate').sections.find(s=>s.side==='back').variant});
          }
          return {strips,exports,preserveAspect:art.preserveAspect};
        }''')
        self.assertTrue(result['preserveAspect'])
        for strip in result['strips']:
            self.assertEqual(strip, dict(base=[40,20], width=40, height=90, count=1,
                                         panelHeight=35, ground=20))
        for exported, reverse in zip(result['exports'], ['silhouette', 'blank']):
            self.assertGreater(exported['pdf'], 1000)
            self.assertEqual(exported['label'], 38)
            self.assertEqual(exported['back'], reverse)
            self.assertEqual(exported['assets'], 2 if reverse=='silhouette' else 1)

    def test_trolls_monstrosities_panel_and_export(self):
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const art = catalog.find(a=>a.id==='orc-monstrosities'), setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a=>[a.id,a===art?1:0]));
          setup.nameplates = true; setup.labelPlacement = 'separate';
          const strips = [1,2,4].flatMap(ranks=>[10,14.5,30].map(infantryHeight=>{
            const s=makeStrip(art,{...setup,ranks,infantryHeight});
            return {base:[s.baseWidth,s.baseDepth],width:s.width,height:s.height,count:s.count,
              panelHeight:s.panelHeight,ground:s.sections.filter(x=>x.kind==='ground').reduce((n,x)=>n+x.height,0)};
          }));
          const exports = [];
          for (const reverse of ['silhouette','blank']) {
            const layout=layoutSetup({...setup,reverse}), assets=await prepareArtwork(layout);
            exports.push({pdf:(await createPDF(layout,assets)).length,assets:assets.size,
              label:layout.pages.flat().find(s=>s.kind==='nameplate').width,
              back:layout.pages.flat().find(s=>s.kind!=='nameplate').sections.find(s=>s.side==='back').variant});
          }
          return {strips,exports,preserveAspect:art.preserveAspect};
        }''')
        self.assertTrue(result['preserveAspect'])
        for strip in result['strips']:
            self.assertEqual(strip, dict(base=[40,20], width=40, height=66, count=1,
                                         panelHeight=23, ground=20))
        for exported, reverse in zip(result['exports'], ['silhouette', 'blank']):
            self.assertGreater(exported['pdf'], 1000)
            self.assertEqual(exported['label'], 38)
            self.assertEqual(exported['back'], reverse)
            self.assertEqual(exported['assets'], 2 if reverse=='silhouette' else 1)

    def test_ogres_monstrosities_panel_and_export(self):
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const art = catalog.find(a=>a.id==='orc-ogres'), setup = defaultSetup();
          setup.quantities = Object.fromEntries(catalog.map(a=>[a.id,a===art?1:0]));
          setup.nameplates = true; setup.labelPlacement = 'separate';
          const strips = [1,2,4].flatMap(ranks=>[10,14.5,30].map(infantryHeight=>{
            const s=makeStrip(art,{...setup,ranks,infantryHeight});
            return {base:[s.baseWidth,s.baseDepth],width:s.width,height:s.height,count:s.count,
              panelHeight:s.panelHeight,ground:s.sections.filter(x=>x.kind==='ground').reduce((n,x)=>n+x.height,0)};
          }));
          const exports = [];
          for (const reverse of ['silhouette','blank']) {
            const layout=layoutSetup({...setup,reverse}), assets=await prepareArtwork(layout);
            exports.push({pdf:(await createPDF(layout,assets)).length,assets:assets.size,
              label:layout.pages.flat().find(s=>s.kind==='nameplate').width,
              back:layout.pages.flat().find(s=>s.kind!=='nameplate').sections.find(s=>s.side==='back').variant});
          }
          return {strips,exports,preserveAspect:art.preserveAspect};
        }''')
        self.assertTrue(result['preserveAspect'])
        for strip in result['strips']:
            self.assertEqual(strip, dict(base=[40,20], width=40, height=66, count=1,
                                         panelHeight=23, ground=20))
        for exported, reverse in zip(result['exports'], ['silhouette', 'blank']):
            self.assertGreater(exported['pdf'], 1000)
            self.assertEqual(exported['label'], 38)
            self.assertEqual(exported['back'], reverse)
            self.assertEqual(exported['assets'], 2 if reverse=='silhouette' else 1)

    def test_rohan_hero_square_base_and_export(self):
        self.page.locator('[data-filter="Rohan"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 11)
        result = self.page.evaluate("""async () => {
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {catalog} = await import('./src/catalog.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const art = catalog.find(a=>a.id==='rohan-eowyn'), setup=defaultSetup();
          setup.quantities=Object.fromEntries(catalog.map(a=>[a.id,a===art?1:0]));
          setup.nameplates=true; setup.labelPlacement='separate';
          const strips=[2,3,4].map(riders=>makeStrip(art,{...setup,riders}));
          const layout=layoutSetup(setup), assets=await prepareArtwork(layout);
          const pdf=await createPDF(layout,assets);
          return {strips:strips.map(s=>({width:s.width,span:s.span,count:s.count,height:s.height,
            ground:s.sections.filter(x=>x.kind==='ground').reduce((n,x)=>n+x.height,0),
            variants:s.sections.filter(x=>x.kind==='face').map(x=>x.variant)})),
            label:layout.pages.flat().find(s=>s.kind==='nameplate').width,pdf:pdf.length};
        }""")
        for strip in result['strips']:
            self.assertEqual(strip, dict(width=20, span=20, count=1, height=62,
                                         ground=20, variants=['front', 'mirror']))
        self.assertEqual(result['label'], 18)
        self.assertGreater(result['pdf'], 1000)

    def test_opposite_faces_align_and_silhouettes_are_grey(self):
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup} = await import('./src/model.js');
          const {prepareArtwork,panelKey} = await import('./src/render.js');
          const {catalog} = await import('./src/catalog.js');
          const setup=defaultSetup();
          setup.quantities=Object.fromEntries(catalog.map(art=>[art.id,1]));
          const layout=layoutSetup(setup), assets=await prepareArtwork(layout), result=[];
          async function pixels(url) {
            const img=new Image();img.src=url;await img.decode();
            const c=document.createElement('canvas');c.width=img.width;c.height=img.height;
            const ctx=c.getContext('2d');ctx.drawImage(img,0,0);return {w:c.width,h:c.height,d:ctx.getImageData(0,0,c.width,c.height).data};
          }
          for(const s of layout.pages.flat()) {
            const variant=s.art.kind==='Mounted'?'mirror':'silhouette';
            const a=await pixels(assets.get(panelKey(s,'front')).url),b=await pixels(assets.get(panelKey(s,variant,layout.setup.silhouetteColor)).url);
            let alphaError=0,colorError=0,wrongGrey=0,visible=0;
            for(let y=0;y<a.h;y++) for(let x=0;x<a.w;x++) {
              const i=(y*a.w+x)*4,j=((a.h-1-y)*a.w+x)*4;
              if(Math.abs(a.d[i+3]-b.d[j+3])>1)alphaError++;
              if(b.d[j+3]>0){visible++;if(b.d[j+3]>128 && [0,1,2].some(k=>Math.abs(b.d[j+k]-204)>2))wrongGrey++;}
              if(variant==='mirror' && [0,1,2].some(k=>Math.abs(a.d[i+k]-b.d[j+k])>1))colorError++;
            }
            result.push({variant,alphaError,colorError,wrongGrey,visible});
          }
          return result;
        }''')
        for r in result:
            self.assertEqual(r['alphaError'], 0)
            self.assertEqual(r['colorError'], 0)
            self.assertGreater(r['visible'], 1000)
            if r['variant'] == 'silhouette':
                self.assertEqual(r['wrongGrey'], 0)

    def test_silhouette_color_rendering_cache_and_legacy_setups(self):
        self.page.locator('#silhouette-color').fill('#cc3300')
        self.ready()
        result = self.page.evaluate("""async () => {
          const {defaultSetup, validateSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, pageScene} = await import('./src/render.js');
          const legacy = defaultSetup(); delete legacy.silhouetteColor;
          const layout = layoutSetup({...defaultSetup(), silhouetteColor:'#cc3300'});
          const assets = await prepareArtwork(layout);
          const op = pageScene(layout,0).find(x=>x.type==='image'&&x.key.includes(':silhouette'));
          const image = new Image(); image.src = assets.get(op.key).url; await image.decode();
          const c = document.createElement('canvas'); c.width=image.width; c.height=image.height;
          const ctx=c.getContext('2d'); ctx.drawImage(image,0,0);
          const pixels=ctx.getImageData(0,0,c.width,c.height).data;
          let visible=0, wrong=0;
          for(let i=0;i<pixels.length;i+=4) if(pixels[i+3]>128) {
            visible++; if(Math.abs(pixels[i]-204)>2||Math.abs(pixels[i+1]-51)>2||pixels[i+2]>2) wrong++;
          }
          return {visible,wrong,legacy:validateSetup(legacy).silhouetteColor};
        }""")
        self.assertGreater(result['visible'], 1000)
        self.assertEqual(result['wrong'], 0)
        self.assertEqual(result['legacy'], '#cccccc')

    def test_packing_is_within_margins_and_does_not_overlap(self):
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          const results=[];
          for(const paper of ['a4','letter']) for(const orientation of ['portrait','landscape']) {
            const s={...defaultSetup(),paper,orientation,riders:2};
            const ids=Object.keys(s.quantities);
            ids.forEach((id,i)=>s.quantities[id]=Math.floor(100/ids.length)+(i<100%ids.length?1:0));
            const l=layoutSetup(s);results.push({width:l.width,height:l.height,margin:l.margin,
              pages:l.pages.map(p=>p.map(x=>({x:x.x,y:x.y,w:x.width,h:x.height,captionY:x.captionY})))});
          }
          return results;
        }''')
        for layout in result:
            self.assertGreater(len(layout['pages']), 1)
            self.assertEqual(sum(map(len, layout['pages'])), 100)
            for page in layout['pages']:
                for i, a in enumerate(page):
                    self.assertGreaterEqual(a['x'], layout['margin'])
                    self.assertLessEqual(a['x'] + a['w'], layout['width'] - layout['margin'] + 1e-6)
                    self.assertLessEqual(a['y'] + a['h'], layout['height'] - layout['margin'] - 9 + 1e-6)
                    for b in page[i + 1:]:
                        overlap = (a['x'] < b['x'] + b['w'] and b['x'] < a['x'] + a['w'] and
                                   a['y'] - 4 < b['y'] + b['h'] and b['y'] - 4 < a['y'] + a['h'])
                        self.assertFalse(overlap)

    def test_faction_ground_colors_preview_pdf_and_persistence(self):
        expect(self.page.locator('#ground-color-mode')).to_have_value('faction')
        expect(self.page.locator('#ground-color')).to_be_disabled()
        self.assertEqual(self.page.locator('#faction-filters .faction-swatch').count(), 7)
        result = self.page.evaluate('''async () => {
          const {catalog, factionGroundColors, groundColorFor} = await import('./src/catalog.js');
          const {defaultSetup, validateSetup, layoutSetup} = await import('./src/model.js');
          const {pageScene, prepareArtwork, createPDF, previewSVG} = await import('./src/render.js');
          const coverage = catalog.every(a => /^#[0-9a-f]{6}$/.test(factionGroundColors[a.era]?.[a.faction]?.color));
          const unique = Object.values(factionGroundColors).every(p => {
            const colors = Object.values(p).map(v => v.color); return new Set(colors).size === colors.length;
          });
          const s = {...defaultSetup(), nameplates: true, labelPlacement: 'attached', riders: 2, lightRiders: 2};
          const ids = ['gondor-swords', 'rohan-outriders', 'orc-troll'];
          s.quantities = Object.fromEntries(catalog.map(a => [a.id, ids.includes(a.id) ? 1 : 0]));
          const l = layoutSetup(s), assets = await prepareArtwork(l);
          const allColors = ids.every(id => {
            const art = catalog.find(a => a.id === id), color = groundColorFor(art, s);
            return l.pages.some((p,i) => p.some(item => item.art.id === id) &&
              pageScene(l,i).some(op => op.type === 'rect' && op.fill === color) && previewSVG(l,i,assets).includes(color));
          });
          const pdf = await PDFLib.PDFDocument.load(await createPDF(l, assets));
          const uniform = layoutSetup({...s, groundColorMode: 'setup', groundColor: '#123456'});
          const uniformColors = uniform.pages.flatMap((_,i) => pageScene(uniform,i))
            .filter(op => op.type === 'rect' && op.fill && op.fill !== '#ffffff').map(op => op.fill);
          const legacy = {...s}; delete legacy.groundColorMode;
          let rejected = false; try { validateSetup({...s, groundColorMode: 'invalid'}); } catch { rejected = true; }
          return {coverage,unique,allColors,pages:pdf.getPageCount(),expected:l.pages.length,
            uniformColors:[...new Set(uniformColors)],legacy:validateSetup(legacy).groundColorMode,rejected};
        }''')
        self.assertTrue(result['coverage'] and result['unique'] and result['allColors'] and result['rejected'])
        self.assertEqual(result['pages'], result['expected'])
        self.assertEqual(result['uniformColors'], ['#123456'])
        self.assertEqual(result['legacy'], 'setup')
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.page.locator('#ground-color-mode').select_option('setup')
        self.page.locator('#load-file').set_input_files({'name': 'factions.json', 'mimeType': 'application/json', 'buffer': payload})
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#ground-color-mode')).to_have_value('faction')
        self.page.locator('#era').select_option('american-civil-war')
        self.assertEqual(self.page.locator('#faction-filters .faction-swatch').count(), 2)

    def test_ground_symbols_geometry_and_vector_pdf(self):
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, makeStrip, layoutSetup} = await import('./src/model.js');
          const {groundSymbol, factionSymbols} = await import('./src/symbols.js');
          const {pageScene, previewSVG, prepareArtwork, createPDF} = await import('./src/render.js');
          const checks = [];
          for (const depth of [20,30,40]) for (const count of [1,2,3,4]) for (const attached of [false,true]) {
            const s = {...defaultSetup(), factionSymbols:true, ranks:count, skirmisherRanks:count,
              riders:Math.max(2,count), lightRiders:Math.max(2,count), cavalryBaseDepth:depth,
              monstrosityBaseDepth:depth, nameplates:attached, labelPlacement:'attached'};
            for (const art of catalog) {
              const strip = makeStrip(art,s), mark = groundSymbol(strip,s);
              const expected = art.kind !== 'Mounted' && strip.count > 2 ? false : true;
              const bounded = !mark || (mark.x >= .5 && mark.x + mark.size <= strip.bodyWidth - .5 &&
                mark.y >= mark.section.y + .5 && mark.y + mark.size <= mark.section.y + mark.section.height - .5);
              const grounds = strip.sections.filter(p=>p.kind==='ground');
              const location = !mark || (art.kind === 'Mounted' && strip.count > 1
                ? grounds.slice(1,-1).includes(mark.section) && mark.rotation === 90
                : mark.section === grounds.at(-1));
              checks.push(bounded && location && !!mark === expected);
            }
          }
          const s = {...defaultSetup(),labelPlacement:'separate', factionSymbols:true, fakeShadows:true};
          const ids = ['gondor-swords','rohan-outriders','orc-troll','rohan-eowyn'];
          s.quantities = Object.fromEntries(catalog.map(a=>[a.id,ids.includes(a.id)?1:0]));
          const l=layoutSetup(s), assets=await prepareArtwork(l);
          const ops=l.pages.flatMap((_,i)=>pageScene(l,i));
          const pdf=await createPDF(l,assets), doc=await PDFLib.PDFDocument.load(pdf);
          const svg=previewSVG(l,0,assets);
          const off=layoutSetup({...s,factionSymbols:false});
          const noSymbols=off.pages.every((_,i)=>!pageScene(off,i).some(op=>op.type==='polygon'));
          const patches=l.pages.every((page,i)=>page.filter(s=>s.kind!=='nameplate').every(strip=>{
            const mark=groundSymbol(strip,s), sy=strip.y+(strip.bodyY||0)+mark.y, sx=strip.x+mark.x;
            const scene=pageScene(l,i), index=scene.findIndex(op=>op.type==='polygon'&&
              op.points.every(p=>p[0]>=sx && p[0]<=sx+mark.size && p[1]>=sy && p[1]<=sy+mark.size));
            return index>0 && scene[index-1].type==='rect' && scene[index-1].w===mark.size+.5;
          }));
          return {checks:checks.every(Boolean), coverage:catalog.every(a=>factionSymbols[a.era]?.[a.faction]),
            polygons:ops.filter(op=>op.type==='polygon').length,svg:svg.includes('<polygon'),
            pages:doc.getPageCount(),expected:l.pages.length,noSymbols,patches,
            unchanged:JSON.stringify(l.pages.map(p=>p.map(s=>[s.x,s.y,s.width,s.height])))===
              JSON.stringify(off.pages.map(p=>p.map(s=>[s.x,s.y,s.width,s.height])))};
        }''')
        self.assertTrue(all(result[k] for k in ['checks','coverage','svg','noSymbols','patches','unchanged']), result)
        self.assertGreater(result['polygons'], 0)
        self.assertEqual(result['pages'], result['expected'])

    def test_numbered_labels_and_independent_symbol_controls(self):
        self.page.locator('#faction-symbols').check()
        self.ready()
        expect(self.page.locator('#nameplates')).not_to_be_checked()
        self.assertGreater(self.page.locator('#sheet polygon').count(), 0)
        self.page.locator('#nameplates').check()
        self.page.locator('#number-bases').check()
        self.page.locator('#qty-gondor-swords').fill('2')
        self.ready()
        self.assertIn('Gondor Swords 2', self.page.locator('#sheet').text_content())
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        for control in ['faction-symbols','number-bases','nameplates']:
            self.page.locator(f'#{control}').uncheck()
        self.page.locator('#load-file').set_input_files({'name':'identification.json','mimeType':'application/json','buffer':payload})
        self.ready()
        self.page.reload()
        self.ready()
        for control in ['faction-symbols','number-bases','nameplates']:
            expect(self.page.locator(f'#{control}')).to_be_checked()
        self.page.locator('#faction-symbols').uncheck()
        self.ready()
        self.assertEqual(self.page.locator('#sheet polygon').count(), 0)
        self.assertIn('Gondor Swords 2', self.page.locator('#sheet').text_content())
        result = self.page.evaluate('''async () => {
          const {catalog}=await import('./src/catalog.js');
          const {defaultSetup,baseLabel,layoutSetup,validateSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF}=await import('./src/render.js');
          const a=catalog.find(a=>a.id==='gondor-swords'), hero=catalog.find(a=>a.id==='rohan-eowyn');
          const s={...defaultSetup(),nameplates:true,numberBases:true,
            quantities:{[a.id]:3,[hero.id]:2},names:{[a.id]:'Tower Guard'},copyNames:{[a.id]:['','Veterans']}};
          const names=[baseLabel(a,s,1),baseLabel(a,s,2),baseLabel(a,s,3),baseLabel(hero,s,2),
            baseLabel(a,{...s,quantities:{[a.id]:1}}),baseLabel(a,{...s,numberBases:false})];
          const l=layoutSetup({...s,labelPlacement:'attached'}), assets=await prepareArtwork(l);
          const pdf=await PDFLib.PDFDocument.load(await createPDF(l,assets));
          const strip=l.pages.flat().find(x=>x.art.id===a.id&&x.copy===3&&x.kind!=='nameplate');
          const old={...s}; delete old.numberBases; delete old.factionSymbols;
          const legacy=validateSetup(old), rejected=[];
          for(const patch of [{factionSymbols:1},{numberBases:'yes'}]) {
            try {validateSetup({...s,...patch});rejected.push(false)} catch {rejected.push(true)}
          }
          return {names,attached:strip.labelName,legacy:[legacy.numberBases,legacy.factionSymbols],rejected,
            pages:pdf.getPageCount(),expected:l.pages.length};
        }''')
        self.assertEqual(result['names'], ['Tower Guard 1','Veterans','Tower Guard 3','Rohan Éowyn','Tower Guard','Tower Guard'])
        self.assertEqual(result['attached'], 'Tower Guard 3')
        self.assertEqual(result['legacy'], [False,False])
        self.assertTrue(all(result['rejected']))
        self.assertEqual(result['pages'], result['expected'])

    def test_hero_labels_center_within_base_and_fold_bands(self):
        result = self.page.evaluate('''async () => {
          const {catalog}=await import('./src/catalog.js');
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,pageScene,createPDF}=await import('./src/render.js');
          const doc=await PDFLib.PDFDocument.create();
          const font=await doc.embedFont(PDFLib.StandardFonts.Helvetica), point=72/25.4;
          const checks=[];
          for(const id of ['rohan-eowyn','rohan-foot-captain'])
          for(const placement of ['rear','attached','separate']) for(const symbols of [false,true]) {
            const s={...defaultSetup(),nameplates:true,factionSymbols:symbols,labelPlacement:placement,
              names:{[id]:'Ada'},quantities:Object.fromEntries(catalog.map(a=>[a.id,a.id===id?1:0]))};
            const l=layoutSetup(s),assets=await prepareArtwork(l);
            for(let i=0;i<l.pages.length;i++) {
              const ops=pageScene(l,i),texts=ops.filter(o=>o.type==='text'&&o.value==='Ada');
              for(const text of texts) {
                const item=l.pages[i].find(p=>text.y>p.y&&text.y<p.y+p.height&&text.x>=p.x&&text.x<=p.x+p.width);
                const width=font.widthOfTextAtSize(text.value,text.size*point)/point;
                const center=text.x+(text.rotation===180?-width/2:width/2);
                checks.push(!!item&&Math.abs(center-(item.x+item.width/2))<1e-7);
                if(item?.wrap) {
                  const bandStart=item.edge==='back'?0:3;
                  checks.push(text.y>item.y+bandStart&&text.y<item.y+bandStart+3);
                }
                if(item?.rearGround) checks.push(text.y<item.y+7);
              }
              checks.push(texts.length>0);
            }
            const pdf=await PDFLib.PDFDocument.load(await createPDF(l,assets));
            checks.push(pdf.getPageCount()===l.pages.length);
          }
          return checks;
        }''')
        self.assertTrue(all(result))

    def test_rear_ground_band_geometry_artwork_labels_and_pdf(self):
        expect(self.page.locator('#label-placement')).to_have_value('rear')
        self.page.locator('#nameplates').check()
        self.page.locator('#number-bases').check()
        self.page.locator('#faction-symbols').check()
        self.page.locator('#label-placement').select_option('rear')
        self.ready()
        expect(self.page.locator('#fold-description')).to_contain_text('7 mm')
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.page.locator('#label-placement').select_option('separate')
        self.page.locator('#load-file').set_input_files({'name':'rear.json','mimeType':'application/json','buffer':payload})
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#label-placement')).to_have_value('rear')
        result = self.page.evaluate('''async () => {
          const {catalog,groundColorFor}=await import('./src/catalog.js');
          const {defaultSetup,makeStrip,layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF,pageScene,panelKey}=await import('./src/render.js');
          const base={...defaultSetup(),labelPlacement:'rear',nameplates:true,numberBases:true,factionSymbols:true,fakeShadows:true};
          const checks=[];
          for(const depth of [20,30,40]) for(const ranks of [1,2,3,4]) for(const riders of [2,3,4]) {
            const s={...base,cavalryBaseDepth:depth,monstrosityBaseDepth:depth,ranks,skirmisherRanks:ranks,riders,lightRiders:riders};
            for(const art of catalog) {
              const strip=makeStrip(art,s), ground=strip.sections.filter(p=>p.kind==='ground');
              checks.push(Math.abs(ground.reduce((n,p)=>n+p.height,0)-strip.span)<1e-7 &&
                strip.sections.every(p=>p.height>0) && strip.rearDepth===7 && strip.wrapTabs.length===2 && strip.bodyY===10 &&
                strip.height===strip.bodyHeight+20 && strip.wrapTabs.every(t=>t.height===10&&t.width===strip.bodyWidth) &&
                strip.uprightPositions.every((v,i,a)=>v>0&&v<strip.span&&(!i||v>a[i-1])) &&
                (art.kind==='Mounted' ? strip.postFoldCuts.length===strip.count&&strip.postFoldCuts.every(c=>
                  c.x===0&&c.width===7) : ground.at(-1).height>=7));
            }
          }
          const ids=['gondor-swords','gondor-rangers','gondor-horse','rohan-eowyn','orc-troll'];
          const examples=[],bounds=[];
          for(const depth of [20,30,40]) {
            const s={...base,cavalryBaseDepth:depth,monstrosityBaseDepth:depth};
            s.quantities=Object.fromEntries(catalog.map(a=>[a.id,ids.includes(a.id)?(a.id==='gondor-swords'?2:1):0]));
            const l=layoutSetup(s),assets=await prepareArtwork(l),ops=l.pages.flatMap((_,i)=>pageScene(l,i));
            const pdf=await PDFLib.PDFDocument.load(await createPDF(l,assets));
            const strip=l.pages.flat().find(p=>p.art.id==='gondor-horse'&&p.kind!=='nameplate');
            const key=panelKey(strip,'front'),image=new Image();image.src=assets.get(key).url;await image.decode();
            const canvas=document.createElement('canvas');canvas.width=image.width;canvas.height=image.height;
            const ctx=canvas.getContext('2d');ctx.drawImage(image,0,0);
            const pixels=ctx.getImageData(0,0,image.width,image.height).data;
            let min=image.width,max=-1,rearAlpha=false;
            for(let y=0;y<image.height;y++)for(let x=0;x<image.width;x++)if(pixels[(y*image.width+x)*4+3]>8){
              min=Math.min(min,x);max=Math.max(max,x);if(x/image.width*depth<=7)rearAlpha=true;
            }
            bounds.push({width:(max-min+1)/image.width*depth,rearAlpha,key});
            const labels=l.pages.flat().filter(p=>p.rearGround);
            examples.push({pages:pdf.getPageCount(),expected:l.pages.length,
              rearLabelFolds:labels.every(p=>[7,10].every(offset=>ops.some(op=>op.type==='line'&&op.x===p.x&&op.y===p.y+offset&&op.x2===p.x+p.width)) &&
                ops.some(op=>op.type==='text'&&op.x>=p.x&&op.x<p.x+p.width&&op.y>p.y&&op.y<p.y+7)),
              labels:labels.map(p=>[p.width,p.height]),text:ops.filter(p=>p.type==='text').map(p=>p.value),
              cuts:ops.filter(p=>p.type==='line'&&p.color==='#773c85').length,
              frontWraps:l.pages.flat().filter(p=>p.wrap).map(p=>[p.edge,p.width,p.height]),
              frontText:l.pages.flat().filter(p=>p.rearBand).every(strip=>ops.some(op=>op.type==='text'&&op.value===strip.labelName&&op.rotation===180&&op.y>strip.y+7&&op.y<strip.y+10)),
              tongues:l.pages.flat().filter(p=>p.wrapTabs).every(strip=>strip.wrapTabs.every(tab=>{
                const fills=ops.filter(op=>op.type==='rect'&&op.x===strip.x&&op.y===strip.y+tab.y&&op.w===tab.width&&op.h===tab.height);
                return fills.some(op=>op.fill===groundColorFor(strip.art,s)) && !(strip.art.kind!=='Mounted'&&tab.edge==='back'&&ops.some(op=>op.type==='rect'&&op.fill==='#ffffff'&&op.x===strip.x&&op.w===tab.width&&op.h===3&&op.y>=strip.y+tab.y&&op.y<strip.y+tab.y+10));
              })),
              rearText:l.pages.flat().filter(p=>p.rearBand).every(strip=>ops.some(op=>op.type==='text'&&op.value===strip.labelName&&
                op.y>strip.y+strip.bodyY+strip.rearBand.y&&op.y<strip.y+strip.bodyY+strip.rearBand.y+7)),
              positions:makeStrip(catalog.find(a=>a.id==='gondor-swords'),s).uprightPositions});
          }
          const symbolOnly={...base,nameplates:false};
          const l=layoutSetup(symbolOnly),assets=await prepareArtwork(l);
          const noNames=l.pages.every((_,i)=>!pageScene(l,i).some(o=>o.type==='text'&&o.value==='Gondor Swords'));
          const off=makeStrip(catalog.find(a=>a.id==='gondor-horse'),{...base,nameplates:false,factionSymbols:false});
          const noGuides=layoutSetup({...base,guides:false});
          return {checks:checks.every(Boolean),examples,bounds,noNames,off:!off.rearDepth,
            cutsWithoutGuides:noGuides.pages.some((_,i)=>pageScene(noGuides,i).some(o=>o.color==='#773c85'&&o.type==='line'))};
        }''')
        self.assertTrue(result['checks'] and result['noNames'] and result['off'] and result['cutsWithoutGuides'])
        for example in result['examples']:
            self.assertEqual(example['pages'], example['expected'])
            self.assertEqual(example['labels'], [[40,17],[20,17]])
            self.assertEqual(example['frontWraps'], [['front',40,9],['front',20,9]])
            self.assertTrue(example['frontText'] and example['rearLabelFolds'])
            self.assertEqual(example['positions'], [3,13])
            self.assertTrue(example['tongues'] and example['rearText'])
            self.assertIn('Gondor Swords 2', example['text'])
            self.assertGreater(example['cuts'], 0)
        self.assertTrue(all(not b['rearAlpha'] for b in result['bounds']))
        self.assertLess(result['bounds'][0]['width'], 13)
        self.assertAlmostEqual(result['bounds'][1]['width'], result['bounds'][2]['width'], delta=.1)
        self.assertNotEqual(result['bounds'][0]['key'], result['bounds'][1]['key'])

    def test_setup_colors_round_trip_and_blank_backs(self):
        self.page.locator('#ground-color-mode').select_option('setup')
        self.page.locator('#ground-color').fill('#245632')
        self.page.locator('#figure-color').fill('#e8dbb4')
        self.page.locator('#silhouette-color').fill('#cc3300')
        self.page.locator('#reverse').select_option('blank')
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        setup = json.loads(payload)['paper']
        self.assertEqual(setup['groundColor'], '#245632')
        self.assertEqual(setup['figureColor'], '#e8dbb4')
        self.assertEqual(setup['silhouetteColor'], '#cc3300')
        self.page.locator('#ground-color-mode').select_option('setup')
        self.page.locator('#ground-color').fill('#abcdef')
        self.page.locator('#load-file').set_input_files({'name': 'palette.json', 'mimeType': 'application/json', 'buffer': payload})
        expect(self.page.locator('#ground-color')).to_have_value('#245632')
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#figure-color')).to_have_value('#e8dbb4')
        expect(self.page.locator('#reverse')).to_have_value('blank')
        expect(self.page.locator('#silhouette-color')).to_have_value('#cc3300')
        expect(self.page.locator('#silhouette-color')).to_be_disabled()
        result = self.page.evaluate('''async () => {
          const {layoutSetup}=await import('./src/model.js'),{pageScene}=await import('./src/render.js');
          const s=JSON.parse(localStorage.getItem('midgard-army-project.v1')).paper,l=layoutSetup(s);
          return {fills:pageScene(l,0).filter(x=>x.type==='rect'&&x.fill&&x.fill!=='#ffffff').map(x=>x.fill),
            images:pageScene(l,0).filter(x=>x.type==='image').map(x=>x.key),
            backs:l.pages.flat().filter(x=>x.art.kind==='Infantry').flatMap(x=>x.sections.filter(a=>a.side==='back').map(a=>a.variant))};
        }''')
        self.assertEqual(set(result['fills']), {'#245632', '#e8dbb4'})
        self.assertEqual(set(result['backs']), {'blank'})
        self.assertFalse(any(':silhouette' in key or ':blank' in key for key in result['images']))

    def test_pdf_download_has_exact_page_size_artwork_and_colors(self):
        self.page.locator('#ground-color-mode').select_option('setup')
        self.page.locator('#ground-color').fill('#224466')
        self.page.locator('#figure-color').fill('#ddccaa')
        self.ready()
        with self.page.expect_download(timeout=30000) as download:
            self.page.locator('#download').click()
        data = Path(download.value.path()).read_bytes()
        self.assertTrue(data.startswith(b'%PDF-'))
        self.assertGreater(len(data), 20000)
        streams = []
        for raw in re.findall(rb'stream\r?\n(.*?)\r?\nendstream', data, re.S):
            try:
                streams.append(zlib.decompress(raw))
            except zlib.error:
                pass
        content = b'\n'.join(s for s in streams if b' rg\n' in s and b' Do\n' in s)
        self.assertIn(b'0.13333333333333333 0.26666666666666666 0.4 rg', content)
        self.assertIn(b'0.8666666666666667 0.8 0.6666666666666666 rg', content)
        self.assertIn(b'113.38582677165356', content)  # 40 mm in PDF points
        self.assertIn(b'56.69291338582678', content)  # 20 mm in PDF points
        result = self.page.evaluate('''async () => {
          const {defaultSetup,layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF}=await import('./src/render.js');
          const s={...defaultSetup(),paper:'letter',riders:2};s.quantities['gondor-swords']=18;
          const l=layoutSetup(s),a=await prepareArtwork(l),bytes=await createPDF(l,a);
          const pdf=await PDFLib.PDFDocument.load(bytes);
          return {expected:l.pages.length,count:pdf.getPageCount(),sizes:pdf.getPages().map(p=>p.getSize())};
        }''')
        self.assertGreater(result['count'], 1)
        self.assertEqual(result['count'], result['expected'])
        for size in result['sizes']:
            self.assertAlmostEqual(size['width'], 612)
            self.assertAlmostEqual(size['height'], 792)

    def test_archer_units_load_project_and_export_pdf(self):
        archer_ids = ['gondor-archers', 'gondor-horse-archers', 'orc-archers', 'orc-warg-archers']
        self.page.locator('#load-file').set_input_files(str(ROOT / 'examples/starter-setup.json'))
        self.page.wait_for_function("document.getElementById('load-file').value === ''")
        self.ready()
        for art_id in archer_ids:
            expect(self.page.locator(f'#qty-{art_id}')).to_have_value('0')
        for art_id in ['gondor-swords', 'gondor-horse', 'orc-axes', 'orc-wargs']:
            self.page.locator(f'#qty-{art_id}').fill('0')
        for art_id in archer_ids:
            self.page.locator(f'#qty-{art_id}').fill('1')
        self.page.wait_for_function('''ids => {
          const saved = JSON.parse(localStorage.getItem('midgard-army-project.v1')).paper;
          return saved && Object.entries(saved.quantities).every(([id, count]) => count === (ids.includes(id) ? 1 : 0));
        }''', arg=archer_ids)
        self.ready()
        result = self.page.evaluate('''async () => {
          const {layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF}=await import('./src/render.js');
          const setup=JSON.parse(localStorage.getItem('midgard-army-project.v1')).paper;
          const layout=layoutSetup(setup),assets=await prepareArtwork(layout);
          const bytes=await createPDF(layout,assets),pdf=await PDFLib.PDFDocument.load(bytes);
          return {ids:layout.pages.flat().map(strip=>strip.art.id),
            total:layout.total,assets:assets.size,pages:pdf.getPageCount(),expected:layout.pages.length};
        }''')
        self.assertCountEqual(result['ids'], archer_ids)
        self.assertEqual(result['total'], 4)
        self.assertEqual(result['assets'], 8)
        self.assertEqual(result['pages'], result['expected'])
        with self.page.expect_download(timeout=30000) as download:
            self.page.locator('#download').click()
        self.assertTrue(Path(download.value.path()).read_bytes().startswith(b'%PDF-'))

    def test_clear_setup_confirmation_and_persistence(self):
        self.page.locator('#nameplates').check()
        self.page.locator('#name-gondor-swords').fill('Guard')
        self.page.locator('[data-art="gondor-swords"] summary').click()
        self.page.locator('#copy-name-gondor-swords-1').fill('First Guard')
        self.page.locator('#ground-color-mode').select_option('setup')
        self.page.locator('#ground-color').fill('#245632')
        self.ready()
        before = self.page.evaluate("localStorage.getItem('midgard-army-project.v1')")

        def cancel(dialog):
            self.assertEqual(dialog.type, 'confirm')
            self.assertIn('all selected bases', dialog.message)
            dialog.dismiss()

        self.page.once('dialog', cancel)
        self.page.locator('#clear').click()
        self.assertEqual(before, self.page.evaluate("localStorage.getItem('midgard-army-project.v1')"))
        expect(self.page.locator('#name-gondor-swords')).to_have_value('Guard')
        expect(self.page.locator('#copy-name-gondor-swords-1')).to_have_value('First Guard')

        self.page.once('dialog', lambda dialog: dialog.accept())
        self.page.locator('#clear').click()
        expect(self.page.locator('#base-count')).to_have_text('0 bases')
        expect(self.page.locator('#sheet')).to_contain_text('Choose at least one base')
        expect(self.page.locator('#download')).to_be_disabled()
        self.page.reload()
        expect(self.page.locator('#sheet')).to_contain_text('Choose at least one base')
        expect(self.page.locator('#ground-color')).to_have_value('#245632')
        expect(self.page.locator('#nameplates')).to_be_checked()
        saved = self.page.evaluate("JSON.parse(localStorage.getItem('midgard-army-project.v1')).paper")
        self.assertTrue(all(value == 0 for value in saved['quantities'].values()))
        self.assertTrue(all(value == '' for value in saved['names'].values()))
        self.assertTrue(all(value == [] for value in saved['copyNames'].values()))
        self.page.locator('#qty-gondor-swords').fill('1')
        self.ready()
        expect(self.page.locator('#copy-name-gondor-swords-1')).to_have_value('')

    def test_invalid_setup_empty_army_and_oversized_strips(self):
        self.page.locator('#qty-gondor-swords').fill('-1')
        expect(self.page.locator('#download')).to_be_disabled()
        expect(self.page.locator('#status')).to_contain_text('0 to 50')
        self.page.locator('#qty-gondor-swords').fill('1')
        self.ready()
        before = self.page.locator('#base-count').inner_text()
        self.page.locator('#load-file').set_input_files({'name': 'bad.json', 'mimeType': 'application/json', 'buffer': b'{"version":99}'})
        expect(self.page.locator('#project-notice')).to_contain_text('Could not open project')
        self.assertEqual(before, self.page.locator('#base-count').inner_text())
        self.page.locator('#mounted-height').fill('30')
        expect(self.page.locator('#status')).to_contain_text('does not fit', timeout=10000)
        expect(self.page.locator('#download')).to_be_disabled()
        self.page.locator('#mounted-height').fill('21')
        self.ready()
        for input in self.page.locator('.art-card:visible .quantity input').all():
            input.fill('0')
        expect(self.page.locator('#sheet')).to_contain_text('Choose at least one base')
        expect(self.page.locator('#download')).to_be_disabled()

    def test_warboss_heroes_artwork_geometry_labels_and_pdf(self):
        for faction, unit in [('Isengard', 'isengard-warboss'), ('Orcs', 'orc-warboss')]:
            self.page.locator(f'[data-filter="{faction}"]').click()
            expect(self.page.locator(f'[data-art="{unit}"]')).to_be_visible()
        result = self.page.evaluate('''async () => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup, unitTypeOptions} = await import('./src/model.js');
          const {prepareArtwork, pageScene, createPDF} = await import('./src/render.js');
          const arts = catalog.filter(a => ['isengard-warboss', 'orc-warboss', 'mordor-warboss'].includes(a.id));
          const images = [];
          for (const art of arts) {
            const img = new Image(); img.src = art.path; await img.decode();
            const canvas = document.createElement('canvas'); canvas.width = img.width; canvas.height = img.height;
            const ctx = canvas.getContext('2d'); ctx.drawImage(img, 0, 0);
            const pixels = ctx.getImageData(0, 0, img.width, img.height).data;
            let clear = 0, solid = 0;
            for (let i = 3; i < pixels.length; i += 4) {
              if (pixels[i] === 0) clear++;
              if (pixels[i] >= 250) solid++;
            }
            const corners = [0, img.width - 1, (img.height - 1) * img.width, img.width * img.height - 1]
              .map(i => pixels[i * 4 + 3]);
            images.push({clear, solid, corners, pixels:img.width * img.height});
          }
          const exports = [];
          for (const labelPlacement of ['separate', 'attached']) {
            const setup = {...defaultSetup(), ranks:4, skirmisherRanks:3, riders:4,
              cavalryBaseDepth:40, monstrosityBaseDepth:40, nameplates:true, labelPlacement,
              quantities:Object.fromEntries(catalog.map(art => [art.id, arts.includes(art) ? 1 : 0]))};
            const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
            const strips = layout.pages.flat().filter(s => s.kind !== 'nameplate');
            const ops = layout.pages.flatMap((_, i) => pageScene(layout, i));
            const pdf = await PDFLib.PDFDocument.load(await createPDF(layout, assets));
            exports.push({pages:pdf.getPageCount(), expected:layout.pages.length,
              strips:strips.map(s => [s.art.hero, s.baseWidth, s.baseDepth, s.count, s.art.preserveAspect]),
              names:arts.map(art => ops.some(op => op.type === 'text' && op.value === art.name))});
          }
          return {images, exports, roles:arts.map(unitTypeOptions), names:arts.map(a => a.name)};
        }''')
        self.assertEqual(result['names'], ['Isengard Boss', 'Orc Warboss', 'Mordor Warboss'])
        self.assertEqual(result['roles'], [[], [], []])
        for image in result['images']:
            self.assertGreater(image['clear'], image['pixels'] * 0.1)
            self.assertGreater(image['solid'], image['pixels'] * 0.1)
            self.assertEqual(image['corners'], [0, 0, 0, 0])
        for export in result['exports']:
            self.assertEqual(export['pages'], export['expected'])
            self.assertEqual(export['strips'], [[True, 20, 20, 1, True]] * 3)
            self.assertEqual(export['names'], [True] * 3)

    def test_all_default_names_fit_labels_and_export(self):
        result = self.page.evaluate('''async () => {
          const {catalog, DEFAULT_NAME_LIMIT, HERO_NAME_LIMIT} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, pageScene, createPDF} = await import('./src/render.js');
          const doc = await PDFLib.PDFDocument.create();
          const font = await doc.embedFont(PDFLib.StandardFonts.Helvetica);
          const failures = [], exports = [];
          for (const art of catalog) {
            const limit = art.hero ? HERO_NAME_LIMIT : DEFAULT_NAME_LIMIT;
            if (art.name.length > limit) failures.push(`${art.id}: character limit`);
            if (font.widthOfTextAtSize(art.name, 6) * 25.4 / 72 > (art.hero ? 16 : 36))
              failures.push(`${art.id}: label width`);
          }
          for (const labelPlacement of ['separate', 'attached']) {
            const setup = {...defaultSetup(), nameplates:true, labelPlacement,
              quantities:Object.fromEntries(catalog.map(art => [art.id, 1]))};
            const layout = layoutSetup(setup), assets = await prepareArtwork(layout);
            const operations = layout.pages.flatMap((_, i) => pageScene(layout, i));
            for (const art of catalog) {
              if (!operations.some(op => op.type === 'text' && op.value === art.name))
                failures.push(`${art.id}: missing default label`);
            }
            const bytes = await createPDF(layout, assets);
            const pdf = await PDFLib.PDFDocument.load(bytes);
            exports.push({pages:pdf.getPageCount(), expected:layout.pages.length});
          }
          return {failures, exports, names:catalog.map(art => art.name)};
        }''')
        self.assertEqual(result['failures'], [])
        self.assertEqual(len(result['names']), len(set(result['names'])))
        self.assertIn('Mordor Herald', result['names'])
        self.assertIn('Gondor Lancers', result['names'])
        self.assertIn('Gondor Militia', result['names'])
        for export in result['exports']:
            self.assertEqual(export['pages'], export['expected'])

    def test_nameplates_names_storage_pdf_and_readability(self):
        self.page.locator('#nameplates').check()
        self.page.locator('#label-placement').select_option('separate')
        self.page.locator('#qty-gondor-swords').fill('2')
        self.page.locator('#name-gondor-swords').fill('Éowyn & Guard')
        self.page.locator('[data-art="gondor-swords"] summary').click()
        self.page.locator('#copy-name-gondor-swords-2').fill('Second Guard')
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.page.locator('#name-gondor-swords').fill('Changed')
        self.page.locator('#load-file').set_input_files({'name': 'names.json', 'mimeType': 'application/json', 'buffer': payload})
        self.ready()
        self.page.reload()
        self.ready()
        expect(self.page.locator('#name-gondor-swords')).to_have_value('Éowyn & Guard')
        expect(self.page.locator('#copy-name-gondor-swords-2')).to_have_value('Second Guard')
        result = self.page.evaluate("""async () => {
          const {layoutSetup,defaultSetup,validateSetup}=await import('./src/model.js');
          const {prepareArtwork,pageScene,createPDF}=await import('./src/render.js');
          const setup=JSON.parse(localStorage.getItem('midgard-army-project.v1')).paper;
          const l=layoutSetup(setup),a=await prepareArtwork(l);
          const labels=l.pages.flat().filter(x=>x.kind==='nameplate');
          const ops=l.pages.flatMap((_,i)=>pageScene(l,i));
          const bytes=await createPDF(l,a), pdf=await PDFLib.PDFDocument.load(bytes);
          const legacy=defaultSetup();delete legacy.nameplates;delete legacy.names;delete legacy.copyNames;
          const large=layoutSetup({...setup,quantities:{'gondor-swords':50,'orc-axes':50}});
          let overlap=false;
          for(const page of large.pages) for(let i=0;i<page.length;i++) for(const b of page.slice(i+1)) {
            const a=page[i];if(a.x<b.x+b.width&&b.x<a.x+a.width&&a.y-4<b.y+b.height&&b.y-4<a.y+a.height)overlap=true;
          }
          return {names:labels.map(x=>x.name),sizes:labels.map(x=>[x.width,x.height]),
            text:ops.filter(x=>x.type==='text').map(x=>x.value),pages:pdf.getPageCount(),expected:l.pages.length,
            legacy:validateSetup(legacy).nameplates,overlap,largeLabels:large.labelTotal};
        }""")
        self.assertEqual(result['names'][:2], ['Éowyn & Guard', 'Second Guard'])
        self.assertEqual(result['sizes'], [[38, 4]] * 5)
        self.assertIn('Éowyn & Guard', result['text'])
        self.assertEqual(result['pages'], result['expected'])
        self.assertFalse(result['legacy'])
        self.assertFalse(result['overlap'])
        self.assertEqual(result['largeLabels'], 100)
        self.page.locator('#name-gondor-swords').fill('W' * 80)
        expect(self.page.locator('#status')).to_contain_text('too long', timeout=10000)
        expect(self.page.locator('#download')).to_be_disabled()
        self.page.locator('#name-gondor-swords').fill('Guard 🐴')
        expect(self.page.locator('#status')).to_contain_text('Latin letters')
        self.page.locator('#name-gondor-swords').fill('Guard')
        self.ready()

    def test_mobile_filter_navigation_and_no_external_dependencies(self):
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.assertTrue(self.page.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.page.locator('[data-filter="Orcs"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 12)
        self.assertEqual(self.page.locator('.art-card:visible:not([data-faction="Orcs"])').count(), 0)
        self.assertEqual(self.page.locator('#qty-gondor-swords').input_value(), '1')
        self.page.locator('#qty-orc-axes').fill('20')
        self.ready()
        expect(self.page.locator('#next')).to_be_enabled()
        self.page.locator('#next').click()
        expect(self.page.locator('#page-number')).to_contain_text('Page 2')
        self.page.locator('#previous').click()
        expect(self.page.locator('#page-number')).to_contain_text('Page 1')
        requests = self.page.evaluate('performance.getEntriesByType("resource").map(r=>r.name).filter(n=>n.startsWith("http"))')
        self.assertTrue(all(url.startswith(self.url) for url in requests))


if __name__ == '__main__':
    unittest.main()
