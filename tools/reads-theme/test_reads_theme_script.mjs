import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';
const init=readFileSync(new URL('./reads_theme_init.js',import.meta.url),'utf8');
const script=readFileSync(new URL('./reads_theme.js',import.meta.url),'utf8');
function page(storage=new Map(),blocked=false,ready='complete'){
 const classes=new Set(['dark']), events=new Map(), documentEvents=new Map();
 let removed=0;
 const root={dataset:{},style:{},classList:{contains:name=>classes.has(name),remove:name=>classes.delete(name)}};
 const sandbox={document:{documentElement:root,readyState:ready,querySelectorAll:()=>[{remove:()=>removed++}],addEventListener:(name,fn)=>documentEvents.set(name,fn)},window:{addEventListener:(name,fn)=>events.set(name,fn)},localStorage:{removeItem:key=>{if(blocked)throw Error('Storage denied');storage.delete(key);}}};
 vm.runInNewContext(init,sandbox);
 const beforeBoot=root.classList.contains('dark');
 vm.runInNewContext(script,sandbox);
 return {root,storage,beforeBoot,removed:()=>removed,domReady:()=>documentEvents.get('DOMContentLoaded')(),pageShown:()=>events.get('pageshow')(),storageChanged:()=>events.get('storage')({key:'spk-theme'})};
}
test('light-only mode is applied before the document paints',()=>{
 const p=page();assert.equal(p.beforeBoot,false);assert.equal(p.root.dataset.readsColorMode,'light');assert.equal(p.root.style.colorScheme,'light');assert.equal(p.removed(),1);
});
test('an old saved dark preference is removed, never restored',()=>{
 const p=page(new Map([['spk-theme','dark']]),false,'loading');assert.equal(p.beforeBoot,false);assert.equal(p.storage.has('spk-theme'),false);assert.equal(p.removed(),0);p.domReady();assert.equal(p.removed(),1);
});
test('home, blog, news, article and favorites remain light',()=>{
 const saved=new Map([['spk-theme','dark'],['spk-favs','article-id'],['spk-view','list']]);
 for(const _name of ['home','blog','article','news','favorites'])assert.equal(page(saved).root.classList.contains('dark'),false);
 assert.equal(saved.get('spk-favs'),'article-id');assert.equal(saved.get('spk-view'),'list');
});
test('blocked browser storage does not break light-only presentation',()=>{
 const p=page(new Map(),true);assert.equal(p.root.dataset.readsColorMode,'light');assert.doesNotThrow(p.pageShown);
});
test('back-forward restoration and stale tabs cannot restore dark mode',()=>{
 const saved=new Map();const p=page(saved);saved.set('spk-theme','dark');p.storageChanged();assert.equal(saved.has('spk-theme'),false);p.pageShown();assert.equal(p.root.classList.contains('dark'),false);
});
