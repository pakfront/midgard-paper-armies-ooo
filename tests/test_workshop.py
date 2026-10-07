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
        self.page.goto(self.url)
        self.ready()

    def tearDown(self):
        self.context.close()
        self.assertEqual(self.errors, [])

    def ready(self):
        expect(self.page.locator('#download')).to_be_enabled(timeout=30000)

    def test_fake_ground_shadows_profiles_alpha_geometry_pdf_and_storage(self):
        expect(self.page.locator('#fake-shadows')).not_to_be_checked()
        self.page.locator('#fake-shadows').check()
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        self.assertTrue(json.loads(payload)['fakeShadows'])
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
                const shadowOps=ops.filter(o=>o.key?.startsWith('shadow:')&&o.x===s.x&&o.y>=s.y&&o.y<s.y+s.height);
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
        self.page.locator('#cavalry-base-depth').select_option('40')
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
        for selector, value in [('#cavalry-base-depth', '40'), ('#figure-background', 'gradient'),
                                ('#gradient-bottom', '#345678'), ('#gradient-top', '#effaff'),
                                ('#label-placement', 'attached')]:
            expect(self.page.locator(selector)).to_have_value(value)
        result = self.page.evaluate('''async () => {
          const {defaultSetup,validateSetup,makeStrip}=await import('./src/model.js');
          const {catalog}=await import('./src/catalog.js');
          const legacy=defaultSetup();legacy.paper='a4';
          for(const k of ['cavalryBaseDepth','figureBackground','gradientBottom','gradientTop','labelPlacement'])delete legacy[k];
          const restored=validateSetup(legacy), s={...defaultSetup(),cavalryBaseDepth:40};
          const cav=makeStrip(catalog.find(a=>a.kind==='Mounted'&&!a.hero),s);
          return {legacy:restored, cavalry:[cav.baseWidth,cav.baseDepth,cav.width,cav.height,cav.pitch],
            heroes:catalog.filter(a=>a.hero).map(a=>{const x=makeStrip(a,s);return [x.baseWidth,x.baseDepth,x.count]})};
        }''')
        self.assertEqual(result['cavalry'], [40, 40, 40, 208, 10])
        self.assertTrue(all(h == [20, 20, 1] for h in result['heroes']))
        self.assertEqual(result['legacy']['paper'], 'a4')
        self.assertEqual(result['legacy']['cavalryBaseDepth'], 20)
        self.assertEqual(result['legacy']['figureBackground'], 'solid')
        self.assertEqual(result['legacy']['labelPlacement'], 'separate')

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
          for(const depth of [20,40]) for(const paper of ['letter','a4']) for(const orientation of ['portrait','landscape']) {
            const s={...defaultSetup(),cavalryBaseDepth:depth,paper,orientation,riders:2,nameplates:true,labelPlacement:'attached',
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
                ground:x.sections.filter(s=>s.kind==='ground').reduce((n,s)=>n+s.height,0),span:x.span,
                bounds:[x.width-x.bodyWidth,x.height-x.bodyHeight],tabs:x.wrapTabs,bodyY:x.bodyY,
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
                self.assertEqual(label['height'], 9)
                self.assertEqual(label['width'], label['baseWidth'])
            self.assertEqual(sorted(n['rotation'] for n in layout['named']), [0, 180])
            self.assertTrue(all(abs(n['size'] * 72 / 25.4 - 6) < 1e-6 for n in layout['named']))
            self.assertEqual(layout['pages'], layout['expected'])
            self.assertIn('First Guard', layout['text'])
            for strip in layout['strips']:
                self.assertAlmostEqual(strip['ground'], strip['span'])
                self.assertEqual(strip['bounds'], [10, 0] if strip['mounted'] else [0, 20])
                for tab in strip['tabs']:
                    self.assertEqual(tab['width'] if strip['mounted'] else tab['height'], 10)
                if strip['mounted']:
                    self.assertAlmostEqual(sum(t['height'] for t in strip['tabs']), strip['span'])
                    self.assertEqual(strip['bodyY'], 0)
                else:
                    self.assertEqual([t['edge'] for t in strip['tabs']], ['front', 'back'])
                    self.assertEqual(strip['bodyY'], 10)
                if strip['hero']:
                    self.assertEqual(strip['base'], [20, 20])

    def test_era_and_faction_filters_preserve_selected_bases(self):
        eras = self.page.evaluate("async () => (await import('./src/catalog.js')).catalog.map(a => a.era)")
        self.assertEqual(set(eras), {'middle-earth-third-age', 'american-civil-war'})
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

    def test_middle_earth_expansion_artwork_and_foot_heroes_export(self):
        ids = ['isengard-warg-riders', 'rohan-foot-captain', 'mordor-spearmen',
               'mordor-morannon', 'mordor-banner-bearer', 'mordor-catapult',
               'gondor-foot-captain', 'harad-spearmen', 'harad-archers',
               'harad-cavalry', 'gondor-aragorn-foot', 'mordor-cave-troll']
        result = self.page.evaluate('''async ids => {
          const {catalog} = await import('./src/catalog.js');
          const {defaultSetup, layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const setup = {...defaultSetup(), ranks: 3, riders: 2, nameplates: true};
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
                self.assertEqual(strip['count'], 2 if strip['kind'] == 'Mounted' else 3)
        self.assertEqual(result['labels'].count([18, 4]), 4)

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
          setup.nameplates = true;
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
          setup.nameplates = true;
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
          setup.nameplates = true;
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
        self.assertEqual(self.page.locator('.art-card:visible').count(), 8)
        result = self.page.evaluate("""async () => {
          const {defaultSetup, layoutSetup, makeStrip} = await import('./src/model.js');
          const {catalog} = await import('./src/catalog.js');
          const {prepareArtwork, createPDF} = await import('./src/render.js');
          const art = catalog.find(a=>a.id==='rohan-eowyn'), setup=defaultSetup();
          setup.quantities=Object.fromEntries(catalog.map(a=>[a.id,a===art?1:0]));
          setup.nameplates=true;
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

    def test_setup_colors_round_trip_and_blank_backs(self):
        self.page.locator('#ground-color').fill('#245632')
        self.page.locator('#figure-color').fill('#e8dbb4')
        self.page.locator('#silhouette-color').fill('#cc3300')
        self.page.locator('#reverse').select_option('blank')
        self.ready()
        with self.page.expect_download() as saved:
            self.page.locator('#save').click()
        payload = Path(saved.value.path()).read_bytes()
        setup = json.loads(payload)
        self.assertEqual(setup['groundColor'], '#245632')
        self.assertEqual(setup['figureColor'], '#e8dbb4')
        self.assertEqual(setup['silhouetteColor'], '#cc3300')
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
          const s=JSON.parse(localStorage.getItem('uprights.setup.v1')),l=layoutSetup(s);
          return {fills:pageScene(l,0).filter(x=>x.type==='rect'&&x.fill&&x.fill!=='#ffffff').map(x=>x.fill),
            images:pageScene(l,0).filter(x=>x.type==='image').map(x=>x.key),
            backs:l.pages.flat().filter(x=>x.art.kind==='Infantry').flatMap(x=>x.sections.filter(a=>a.side==='back').map(a=>a.variant))};
        }''')
        self.assertEqual(set(result['fills']), {'#245632', '#e8dbb4'})
        self.assertEqual(set(result['backs']), {'blank'})
        self.assertFalse(any(':silhouette' in key or ':blank' in key for key in result['images']))

    def test_pdf_download_has_exact_page_size_artwork_and_colors(self):
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

    def test_archer_units_load_legacy_setups_and_export_pdf(self):
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
          const saved = JSON.parse(localStorage.getItem('uprights.setup.v1'));
          return saved && Object.entries(saved.quantities).every(([id, count]) => count === (ids.includes(id) ? 1 : 0));
        }''', arg=archer_ids)
        self.ready()
        result = self.page.evaluate('''async () => {
          const {layoutSetup}=await import('./src/model.js');
          const {prepareArtwork,createPDF}=await import('./src/render.js');
          const setup=JSON.parse(localStorage.getItem('uprights.setup.v1'));
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
        self.page.locator('#ground-color').fill('#245632')
        self.ready()
        before = self.page.evaluate("localStorage.getItem('uprights.setup.v1')")

        def cancel(dialog):
            self.assertEqual(dialog.type, 'confirm')
            self.assertIn('all selected bases', dialog.message)
            dialog.dismiss()

        self.page.once('dialog', cancel)
        self.page.locator('#clear').click()
        self.assertEqual(before, self.page.evaluate("localStorage.getItem('uprights.setup.v1')"))
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
        saved = self.page.evaluate("JSON.parse(localStorage.getItem('uprights.setup.v1'))")
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
        expect(self.page.locator('.notice')).to_contain_text('Could not load setup')
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

    def test_nameplates_names_storage_pdf_and_readability(self):
        self.page.locator('#nameplates').check()
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
          const setup=JSON.parse(localStorage.getItem('uprights.setup.v1'));
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
        self.assertEqual(self.page.locator('.art-card:visible').count(), 10)
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
