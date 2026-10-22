const {chromium}=require('playwright');const assert=require('node:assert/strict');
const pages=['index','items','quests','maps','skills','scroll-simulator','damage-calculator','combat-analysis','avatar-maker','boss-timer','gacha-simulator','third-job','goddess-tower','exp-exchange','skill-changes','halloween','patch-notes','web-changelog'];
const routes=['source-monsters','source-items','source-quests','source-maps','source-skills',...pages.slice(5)];
(async()=>{const browser=await chromium.launch();try{
 const page=await browser.newPage({viewport:{width:1440,height:1000}});const base=process.env.KIWI_TEST_URL||'http://127.0.0.1:8000';const errors=[];page.on('pageerror',e=>errors.push(e.message));
 // In this environment Chromium cannot use the proxy CA. Fulfil only the approved
 // origin from a read-only localhost mirror fetched with normal verified TLS.
 await page.route('https://morrisrrrrrrr-svg.github.io/**',async route=>{const u=new URL(route.request().url());const response=await route.fetch({url:'http://127.0.0.1:8003'+u.pathname+u.search,timeout:30000});await route.fulfill({response})});
 await page.goto(base+'/#memory');await page.locator('.memory-card').last().waitFor();assert.equal(await page.locator('.memory-card').count(),18);await page.waitForFunction(()=>[...document.querySelectorAll('.memory-card img')].every(x=>x.complete&&x.naturalWidth>0));
 for(let i=0;i<routes.length;i++){
  await page.goto(base+'/#'+routes[i]);const iframe=page.locator('#memory-frame');await iframe.waitFor();assert.ok((await iframe.getAttribute('src')).endsWith('/'+pages[i]+'.html'));
  const frame=page.frameLocator('#memory-frame');await frame.locator('main').first().waitFor({timeout:30000});const child=page.frames().find(f=>f.url().includes('morrisrrrrrrr-svg.github.io/'+pages[i]+'.html'));await child.waitForFunction(()=>document.querySelector('main')?.innerText.length>80,{},{timeout:30000});
  if(pages[i]==='damage-calculator'){await frame.locator('#characterLevel').fill('39');await frame.locator('#characterLevel').dispatchEvent('input');assert.equal(await frame.locator('#characterLevel').inputValue(),'39')}
  if(pages[i]==='avatar-maker'){await frame.locator('#avatarSearch').fill('黑');await frame.locator('#flipAvatar').click();assert.equal(await frame.locator('#avatarSearch').inputValue(),'黑')}
  if(pages[i]==='exp-exchange'){await frame.locator('#expLevel').fill('39');await frame.locator('#expLevel').dispatchEvent('input');assert.equal(await frame.locator('#expLevel').inputValue(),'39')}
 }
 await page.goto(base+'/#memory');await page.setViewportSize({width:390,height:844});await page.locator('.memory-card').last().waitFor();assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);assert.deepEqual(errors,[]);
 console.log('PASS: 18 reviewed source pages, all local menu icons, embedded page navigation, calculator/avatar/EXP interactions, mobile portal');
 }finally{await browser.close()}})().catch(e=>{console.error(e);process.exit(1)});
