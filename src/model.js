import {catalog} from './catalog.js';
import {pack} from './packing.js';

export function defaultSetup() {
  return {version: 1, ranks: 2, riders: 4, reverse: 'silhouette', infantryHeight: 14.5, mountedHeight: 21,
    groundColor: '#b6bc91', figureColor: '#ffffff', paper: 'a4', orientation: 'portrait', margin: 10, gap: 4, guides: true,
    quantities: Object.fromEntries(catalog.map((art, i) => [art.id, i < 4 ? 1 : 0]))};
}

export function validateSetup(input) {
  if (!input || typeof input !== 'object' || Array.isArray(input) || input.version !== 1) throw Error('This is not an Uprights version 1 setup.');
  const result = defaultSetup();
  const number = (key, min, max, integer = false) => {
    const value = input[key];
    if (typeof value !== 'number' || !Number.isFinite(value) || value < min || value > max || (integer && !Number.isInteger(value))) throw Error(`Invalid ${key}: use ${min} to ${max}${integer ? ' (whole numbers)' : ''}.`);
    result[key] = value;
  };
  number('ranks', 1, 4, true); number('riders', 2, 4, true);
  number('infantryHeight', 10, 30); number('mountedHeight', 15, 30);
  number('margin', 5, 25); number('gap', 2, 10);
  for (const [key, values] of Object.entries({reverse: ['silhouette', 'blank'], paper: ['a4', 'letter'], orientation: ['portrait', 'landscape']})) {
    if (!values.includes(input[key])) throw Error(`Invalid ${key}.`);
    result[key] = input[key];
  }
  for (const key of ['groundColor', 'figureColor']) {
    if (typeof input[key] !== 'string' || !/^#[0-9a-f]{6}$/i.test(input[key])) throw Error(`Invalid ${key}.`);
    result[key] = input[key].toLowerCase();
  }
  if (typeof input.guides !== 'boolean') throw Error('Invalid fold guide setting.');
  result.guides = input.guides;
  if (!input.quantities || typeof input.quantities !== 'object' || Array.isArray(input.quantities)) throw Error('Missing unit quantities.');
  let total = 0;
  for (const art of catalog) {
    const n = input.quantities[art.id] ?? 0;
    if (!Number.isInteger(n) || n < 0 || n > 50) throw Error(`${art.name}: choose 0 to 50 bases.`);
    result.quantities[art.id] = n; total += n;
  }
  if (total > 100) throw Error('Use at most 100 bases per setup.');
  return result;
}

// The unfolded strip is: half foot, [front, back, full foot]..., half foot.
// Each pair doubles back at its crest; only flat feet contribute to the base span.
export function makeStrip(art, setup, copy = 1) {
  const mounted = art.kind === 'Mounted';
  const width = mounted ? 20 : 40, span = mounted ? 40 : 20;
  const count = mounted ? setup.riders : setup.ranks;
  const panelHeight = mounted ? setup.mountedHeight : setup.infantryHeight;
  const pitch = span / count, sections = [], folds = [];
  let y = 0;
  const add = (kind, height, extra = {}) => { sections.push({kind, y, height, ...extra}); y += height; };
  add('ground', pitch / 2);
  for (let rank = 0; rank < count; rank++) {
    folds.push({y, kind: 'valley'});
    add('face', panelHeight, {side: 'front', variant: 'front', rank});
    folds.push({y, kind: 'mountain'});
    add('face', panelHeight, {side: 'back', variant: mounted ? 'mirror' : setup.reverse, rank});
    folds.push({y, kind: 'valley'});
    add('ground', rank === count - 1 ? pitch / 2 : pitch);
  }
  return {art, copy, name: art.name, width, height: y, count, span, panelHeight, pitch, sections, folds};
}

export function layoutSetup(setup) {
  setup = validateSetup(setup);
  const items = catalog.flatMap(art => Array.from({length: setup.quantities[art.id]}, (_, i) => makeStrip(art, setup, i + 1)));
  return {...pack(items, setup), setup, total: items.length};
}
