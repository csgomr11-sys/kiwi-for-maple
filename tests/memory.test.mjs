import test from 'node:test';
import assert from 'node:assert/strict';
import {existsSync,readFileSync} from 'node:fs';
import {MEMORY_PAGES,memoryRoute} from '../web/memory.mjs';
test('all eighteen native entries have unique routes, source provenance and vector interface symbols',()=>{
 const symbols=readFileSync(new URL('../web/icons.svg',import.meta.url),'utf8');
 assert.equal(MEMORY_PAGES.length,18);assert.equal(new Set(MEMORY_PAGES.map(memoryRoute)).size,18);
 const review=JSON.parse(readFileSync(new URL('../data/version-evidence/interface-review.json',import.meta.url)));
 for(const p of MEMORY_PAGES){assert.ok(symbols.includes('id="'+p.id+'"'),p.id);assert.ok(existsSync(new URL('../web/'+p.icon,import.meta.url)),p.icon);const record=review.pages.find(x=>x.page===p.page);assert.ok(record,p.page);assert.deepEqual(record.errors,[]);assert.ok(record.url.startsWith('https://morrisrrrrrrr-svg.github.io/'))}
});
