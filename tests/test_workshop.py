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
            self.assertEqual(s['width'], 20 if mounted else 40)
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

    def test_monstrosities_two_trolls_panel_and_export(self):
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

    def test_rohan_hero_square_base_and_export(self):
        self.page.locator('[data-filter="Rohan"]').click()
        self.assertEqual(self.page.locator('.art-card:visible').count(), 5)
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
        for input in self.page.locator('.quantity input').all():
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
        self.assertEqual(self.page.locator('.art-card:visible').count(), 9)
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
