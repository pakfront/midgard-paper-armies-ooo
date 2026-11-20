import functools, http.server, json, pathlib, threading, unittest
from playwright.sync_api import expect, sync_playwright
ROOT=pathlib.Path(__file__).resolve().parents[1]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*args): pass
class Workshop(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server=http.server.ThreadingHTTPServer(('127.0.0.1',0),functools.partial(Quiet,directory=str(ROOT)))
        threading.Thread(target=cls.server.serve_forever,daemon=True).start()
        cls.p=sync_playwright().start();cls.browser=cls.p.chromium.launch()
    @classmethod
    def tearDownClass(cls):
        cls.browser.close();cls.p.stop();cls.server.shutdown()
    def setUp(self):
        self.page=self.browser.new_page(viewport={'width':1440,'height':1100});self.errors=[]
        self.page.on('pageerror',lambda e:self.errors.append(str(e)))
        self.page.goto(f'http://127.0.0.1:{self.server.server_port}/')
    def tearDown(self):
        self.assertEqual(self.errors,[]);self.page.close()
    def test_roster_workflow(self):
        p=self.page
        p.get_by_role('tab',name='Unit types').click()
        p.get_by_role('button',name='+ Standard unit type').click()
        p.locator('[name=name]').fill('Gondor Spears')
        p.locator('[name=base]').select_option('Heavy Infantry')
        p.locator('[name=trait][value=Brittle]').check()
        p.locator('#entry-form button[type=submit]').click()
        p.get_by_role('tab',name='Force',exact=True).click()
        p.get_by_role('button',name='+ Units',exact=True).click()
        p.locator('[name=quantity]').fill('3');p.locator('#entry-form button[type=submit]').click()
        self.assertEqual(p.locator('#roster .unit').count(),3)
        self.assertEqual(p.locator('#roster .unit .break-test').count(),6)
        p.get_by_role('button',name='+ Hero',exact=True).click()
        p.locator('#fields [name=name]').fill('Captain')
        p.locator('[name=heroTrait][value="Army Commander"]').check()
        p.locator('#entry-form button[type=submit]').click()
        self.assertEqual(p.locator('#roster .hero').count(),1)
        data=json.loads(p.evaluate("localStorage.getItem('midgard-army-project.v1')"))
        self.assertEqual(data['army']['types'][0]['points'],20)
        self.assertEqual(data['army']['heroes'][0]['reputation'],3)
        p.reload();self.assertEqual(p.locator('#roster .unit').count(),3)
        with p.expect_download() as download:p.get_by_role('button',name='Save project',exact=True).click()
        saved=json.loads(pathlib.Path(download.value.path()).read_text())
        self.assertEqual(saved,data)
        p.on('dialog',lambda d:d.accept())
        p.locator('#load-file').set_input_files({'name':'army.json','mimeType':'application/json','buffer':json.dumps(saved).encode()})
        self.assertEqual(p.locator('#roster .unit').count(),3)
        p.wait_for_function("document.querySelector('#project-notice').textContent.startsWith('Loaded ')")
        bad=dict(saved,version=999)
        p.locator('#load-file').set_input_files({'name':'bad.json','mimeType':'application/json','buffer':json.dumps(bad).encode()})
        p.wait_for_function("document.querySelector('#project-notice').textContent.startsWith('Could not open project')")
        self.assertIn('Could not open project',p.locator('#project-notice').inner_text())
        self.assertEqual(p.locator('#roster .unit').count(),3)
        for col in ['one','two']:
            p.locator('#columns').select_option(col)
            for paper in ['Letter','A4']:
                p.locator('#roster-paper').select_option(paper)
                self.assertTrue(p.pdf(prefer_css_page_size=True).startswith(b'%PDF-'))
        p.set_viewport_size({'width':390,'height':844})
        self.assertTrue(p.evaluate('document.documentElement.scrollWidth <= innerWidth'))
    def test_large_army_and_catalog(self):
        p=self.page
        army=p.evaluate("""async()=>{
            const m=await import('./src/roster/model.js'),r=await import('./src/roster/rules.js'),{catalog}=await import('./src/roster/catalog.js');
            for(const base of catalog.profiles){const p=r.unitProfile(base.name);if(!Number.isFinite(p.points)||!Number.isFinite(p.combat))throw Error(base.name);for(const o of base.options)r.unitProfile(base.name,[o.id]);for(const t of base.availableTraits)r.unitProfile(base.name,[],[t.trait.name]);}
            const a=m.blank();a.name='The defence of Osgiliath';a.settings.columns='two';
            a.contingents[0].name='The city guard';a.contingents.push({id:m.uid(),name:'The river reserve'});
            const t={...r.unitProfile('Heavy Infantry',[],['Brittle']),id:m.uid(),name:'Gondor Spears',nextNumber:1,standard:{profile:'Heavy Infantry',options:[],traits:['Brittle']}};
            a.types.push(t);m.addUnits(a,t.id,a.contingents[0].id,18);m.addUnits(a,t.id,a.contingents[1].id,4);
            const h={...r.heroProfile(3,1,'NO',['Army Commander']),id:m.uid(),name:'Captain of the White Tower',contingentId:a.contingents[0].id};a.heroes.push(h);
            m.validate(a);return a;
        }""")
        project = json.loads((ROOT/'src/roster/osgiliath.json').read_text())
        project['army'] = army
        project['mapping']['labels'] = {}
        p.locator('#load-file').set_input_files({'name':'large.json','mimeType':'application/json','buffer':json.dumps(project).encode()})
        p.wait_for_function("document.querySelector('#project-notice').textContent.startsWith('Loaded ')")
        self.assertEqual(p.locator('#roster .unit').count(),22)
        self.assertEqual(p.locator('#roster .group').count(),4)
        self.assertTrue(p.pdf(prefer_css_page_size=True).startswith(b'%PDF-'))
        # Verify headings and stats remain in the same screen column.
        self.assertTrue(p.locator('#roster .group-head').evaluate_all('(heads)=>heads.every(h=>{const a=h.querySelector("h3").getBoundingClientRect(),b=h.querySelector(".profile").getBoundingClientRect();return Math.abs(a.left-b.left)<400})'))
        army['units']=army['units'][:4]+army['units'][-2:]
        p.once('dialog',lambda d:d.accept())
        p.locator('#load-file').set_input_files({'name':'sample.json','mimeType':'application/json','buffer':json.dumps(project).encode()})
        p.wait_for_function("document.querySelectorAll('#roster .unit').length===6")

    def test_trait_descriptions(self):
        p=self.page
        missing=p.evaluate("""async()=>{
            const {catalog}=await import('./src/roster/catalog.js'),{traitDescription}=await import('./src/roster/traits.js');
            const traits=[...catalog.heroTraits,...catalog.profiles.flatMap(p=>[...(p.builtInTraits||[]),...p.availableTraits.map(t=>t.trait)])];
            return traits.filter(t=>!traitDescription(t.name)).map(t=>t.name);
        }""")
        self.assertEqual(missing,[])
        p.locator('#load-file').set_input_files(str(ROOT/'src/roster/osgiliath.json'))
        p.wait_for_function("document.querySelectorAll('#roster .unit').length===6")
        self.assertTrue(p.locator('#trait-descriptions').is_checked())
        self.assertEqual(p.locator('#roster .trait-description').count(),3)
        self.assertIn('Command Test',p.locator('#roster .group .trait-description').first.inner_text())
        self.assertIn('p. 68',p.locator('#roster .group .trait-description').first.inner_text())
        p.locator('#trait-descriptions').uncheck()
        self.assertEqual(p.locator('#roster .trait-description').count(),0)
        self.assertIn('Brittle',p.locator('#roster .group-head').first.inner_text())
        saved=json.loads(p.evaluate("localStorage.getItem('midgard-army-project.v1')"))
        self.assertFalse(saved['army']['settings']['traitDescriptions'])
        p.reload()
        self.assertFalse(p.locator('#trait-descriptions').is_checked())
        p.locator('#trait-descriptions').check()
        for col in ['one','two']:
            p.locator('#columns').select_option(col)
            p.emulate_media(media='print')
            self.assertEqual(p.locator('#roster .trait-description').count(),3)
            p.emulate_media(media='screen')
        p.set_viewport_size({'width':390,'height':844})
        self.assertTrue(p.evaluate('document.documentElement.scrollWidth <= innerWidth'))
        self.assertTrue(p.locator('#trait-descriptions').is_checked())

    def test_roster_standees_round_trip(self):
        p = self.page
        p.locator('#load-file').set_input_files(ROOT/'src/roster/osgiliath.json')
        expect(p.locator('#roster .contingent-badge')).to_have_count(2)
        expect(p.locator('#roster .summary')).to_contain_text('147')
        expect(p.locator('#roster .summary')).to_contain_text('16')
        p.locator('#paper-nav').click()
        expect(p.locator('#status')).to_contain_text('Choose artwork')
        expect(p.locator('#download')).to_be_disabled()
        p.get_by_label('Default artwork').select_option('gondor-spears')
        p.get_by_label('Hero artwork').select_option('gondor-foot-captain')
        p.get_by_text('Artwork by contingent', exact=True).click()
        p.get_by_label('The river reserve', exact=True).select_option('gondor-swords')
        expect(p.locator('#status')).to_contain_text('7 bases')
        p.locator('#army-nav').click()
        p.get_by_role('tab', name='Force', exact=True).click()
        card = p.locator('.editor-card').filter(has=p.get_by_role('heading', name='Gondor Spears 1', exact=True))
        card.get_by_role('button', name='Move', exact=True).click()
        p.locator('#fields select').select_option(label='The river reserve')
        p.locator('#entry-form [type=submit]').click()
        p.locator('#paper-nav').click()
        with p.expect_download() as download:
            p.locator('#save').click()
        saved = pathlib.Path(download.value.path()).read_bytes()
        p.locator('#load-file').set_input_files({'name':'moved.json','mimeType':'application/json','buffer':saved})
        p.locator('#paper-nav').click()
        expect(p.locator('#download')).to_be_enabled()
        with p.expect_download() as download:
            p.locator('#download').click()
        self.assertTrue(pathlib.Path(download.value.path()).read_bytes().startswith(b'%PDF-'))
        p.reload()
        expect(p.locator('#status')).to_contain_text('7 bases')
        entries = p.evaluate("""async () => {
          const {project, rosterBases} = await import('./src/project.js');
          return rosterBases(project).map(b => [b.label, b.art.id, b.badge.shape]);
        }""")
        self.assertEqual(entries[0], ['Gondor Spears 1', 'gondor-swords', 'diamond'])
        self.assertEqual(sum(art == 'gondor-swords' for _, art, _ in entries), 3)
        self.assertIn(['Captain', 'gondor-foot-captain', 'square'], entries)
        p.locator('#army-nav').click()
        p.emulate_media(media='print')
        expect(p.locator('#roster')).to_be_visible()
        expect(p.locator('.workshop-header')).to_be_hidden()
        self.assertTrue(p.pdf(prefer_css_page_size=True).startswith(b'%PDF-'))

    def test_shared_art_roles_and_large_roster(self):
        result = self.page.evaluate("""async () => {
          const {newProject, validateProject, rosterBases} = await import('./src/project.js');
          const {layoutSetup} = await import('./src/model.js');
          const {addUnits, profile} = await import('./src/roster/model.js');
          const p = newProject();
          for (const role of ['Warriors', 'Skirmishers']) {
            p.army.types.push({...profile(), role, id:role, name:role, nextNumber:1});
            addUnits(p.army, role, p.army.contingents[0].id, 1);
            p.mapping.art[role] = 'gondor-spears';
          }
          validateProject(p);
          const counts = layoutSetup(p.paper, rosterBases(p)).pages.flat()
            .filter(s => s.entryId).map(s => [s.role, s.count]).sort();
          addUnits(p.army, 'Warriors', p.army.contingents[0].id, 99);
          validateProject(p);
          try { rosterBases(p); } catch (e) { return {counts, message:e.message}; }
        }""")
        self.assertEqual(result['counts'], [['Skirmishers', 1], ['Warriors', 2]])
        self.assertIn('101', result['message'])

    def test_badge_only_mounted_base_and_undo(self):
        result = self.page.evaluate("""async () => {
          const {newProject, replaceProject, editProject, rosterBases, undoProject} = await import('./src/project.js');
          const store = await import('./src/project.js');
          const {profile} = await import('./src/roster/model.js');
          const {layoutSetup} = await import('./src/model.js');
          const {prepareArtwork, pageScene, createPDF} = await import('./src/render.js');
          const next = newProject();
          next.army.heroes.push({...profile(), level:2, name:'Marshal', id:'marshal', contingentId:next.army.contingents[0].id});
          next.mapping.art.marshal = 'gondor-captain';
          next.mapping.labels.marshal = 'Leader';
          next.paper.nameplates = false;
          next.paper.labelPlacement = 'separate';
          replaceProject(next, 'load');
          const layout = layoutSetup(next.paper, rosterBases(next));
          const parts = layout.pages.flat();
          const rear = parts.find(part => part.rearGround);
          const assets = await prepareArtwork(layout);
          const badge = pageScene(layout, 0).some(op => op.type === 'polygon' && op.fill === rear.badge.color);
          const pdf = await createPDF(layout, assets);
          editProject(p => { p.army.heroes = []; }, 'army');
          const deleted = !store.project.mapping.art.marshal && !store.project.mapping.labels.marshal;
          undoProject();
          return {rear:rear.entryId, badge, pdf:pdf.length, deleted, restored:rosterBases(store.project)[0].label};
        }""")
        self.assertEqual(result['rear'], 'marshal')
        self.assertTrue(result['badge'] and result['deleted'])
        self.assertGreater(result['pdf'], 10000)
        self.assertEqual(result['restored'], 'Leader')

    def test_model_and_rules(self):
        result=self.page.evaluate('''async()=>{
        const m=await import('./src/roster/model.js'),r=await import('./src/roster/rules.js');
        const a=m.blank(),c=a.contingents[0].id;
        const t={...r.unitProfile('Shooters'),id:m.uid(),name:'Scouts',nextNumber:1};a.types.push(t);
        m.addUnits(a,t.id,c,2);a.contingents.push({id:m.uid(),name:'Reserve'});
        const first=a.units[0].id;a.units[0].contingentId=a.contingents[1].id;
        m.addUnits(a,t.id,c,1);m.validate(JSON.parse(JSON.stringify(a)));
        const invalid=structuredClone(a);invalid.units[0].contingentId='missing';let rejected=false;try{m.validate(invalid)}catch{rejected=true}
        const conflict=()=>{try{r.unitProfile('Heavy Infantry',[1,2]);return false}catch{return true}};
        return {names:a.units.map(u=>u.name),stable:a.units[0].id===first,armour:t.armour,rejected,conflict:conflict(),hero:r.heroProfile(4,1,'NO',['Army Commander'])};}''')
        self.assertEqual(result['names'],['Scouts 1','Scouts 2','Scouts 3'])
        self.assertEqual(result['armour'],[2,3]);self.assertTrue(result['stable']);self.assertTrue(result['rejected']);self.assertTrue(result['conflict'])
        self.assertEqual(result['hero']['points'],37);self.assertEqual(result['hero']['reputation'],5)
if __name__=='__main__':unittest.main()
