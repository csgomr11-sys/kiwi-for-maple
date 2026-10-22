const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch();
  try{
    const page=await browser.newPage();
    const base=process.env.KIWI_TEST_URL||'http://127.0.0.1:8000';
    await page.goto(base+'/#quests');
    await page.locator('#db-search').fill('女神的痕跡');
    let checkbox=page.locator('[data-quest-completed="1203"]');
    await checkbox.waitFor();
    assert.equal(await checkbox.isChecked(),false);
    await checkbox.check();
    await page.locator('.quest-completion.is-complete input[data-quest-completed="1203"]').waitFor();
    await page.reload();
    await page.locator('#db-search').fill('女神的痕跡');
    await checkbox.waitFor();
    assert.equal(await checkbox.isChecked(),true);
    await page.locator('#quest-status').selectOption('incomplete');
    await checkbox.waitFor({state:'detached'});
    await page.locator('#quest-status').selectOption('completed');
    await checkbox.waitFor();
    await page.locator('#quest-status').selectOption('all');
    await checkbox.uncheck();
    await page.locator('[data-detail="quests"][data-id="1203"]').click();
    await page.locator('#detail [data-quest-completed="1203"]').check();
    await page.locator('#detail .quest-completion.is-complete').waitFor();
    assert.ok((await page.locator('#detail-body').innerText()).includes('官方V002開放公告'));
    console.log('PASS: quest check/uncheck, reload persistence, progress filters, confirmed-presence detail synchronization');
  }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
