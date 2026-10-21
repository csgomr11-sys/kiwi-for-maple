const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
 const browser=await chromium.launch();
 try{
  const page=await browser.newPage();page.setDefaultTimeout(8000);
  const errors=[];page.on('pageerror',e=>errors.push(e.message));
  const base=process.env.KIWI_TEST_URL||'http://127.0.0.1:8000';
  await page.goto(base+'/#monsters');
  const input=page.locator('#db-search');await input.waitFor();await input.focus();
  await page.evaluate(()=>window.originalSearch=document.querySelector('#db-search'));
  const cdp=await page.context().newCDPSession(page);
  for(const text of ['小','小幽','小幽靈']){
   await cdp.send('Input.imeSetComposition',{text,selectionStart:text.length,selectionEnd:text.length});
   assert.equal(await page.evaluate(()=>window.originalSearch===document.querySelector('#db-search')&&originalSearch.isConnected),true);
   assert.equal(await input.inputValue(),text);
  }
  await cdp.send('Input.insertText',{text:'小幽靈'});
  await page.waitForFunction(()=>document.querySelector('.dense-db tbody')?.innerText.includes('小幽靈')&&!document.querySelector('.dense-db tbody')?.innerText.includes('嫩寶'));
  assert.equal(await input.inputValue(),'小幽靈');assert.equal(await input.evaluate(el=>el===document.activeElement),true);
  // Cancel an already scheduled ASCII search before committing an IME search.
  await page.evaluate(()=>{
   const el=document.querySelector('#db-search');el.value='x';el.dispatchEvent(new InputEvent('input',{bubbles:true}));
   el.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));el.value='殭屍';
   el.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true,data:'殭屍'}));window.pendingSearch=el;
  });
  await page.waitForTimeout(50);
  assert.equal(await page.evaluate(()=>pendingSearch===document.querySelector('#db-search')&&pendingSearch.isConnected),true);
  await page.evaluate(()=>pendingSearch.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:'殭屍'})));
  await page.waitForFunction(()=>document.querySelector('.dense-db tbody')?.innerText.includes('殭屍菇菇'));
  for(const [route,id,text] of [['library','library-search','萬聖節'],['guides','guide-search','練功'],['audit','audit-search','時間神殿']]){
   await page.goto(base+'/#'+route);await page.locator('#'+id).waitFor();
   await page.evaluate(({id,text})=>{
    const el=document.getElementById(id);window.searchBefore=el;el.focus();
    el.dispatchEvent(new CompositionEvent('compositionstart',{bubbles:true}));el.value=text;
    el.dispatchEvent(new InputEvent('input',{bubbles:true,isComposing:true,data:text}));
   },{id,text});
   await page.waitForTimeout(30);
   assert.equal(await page.evaluate(id=>searchBefore===document.getElementById(id)&&searchBefore.isConnected,id),true);
   await page.evaluate(text=>searchBefore.dispatchEvent(new CompositionEvent('compositionend',{bubbles:true,data:text})),text);
   await page.waitForFunction(id=>document.getElementById(id)!==window.searchBefore,id);
   assert.equal(await page.locator('#'+id).inputValue(),text);
  }
  assert.deepEqual(errors,[]);
  console.log('PASS: Chromium IME composition, committed Chinese search, focus, pending-render cancellation, library/guide/audit Chinese input');
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exit(1)});
