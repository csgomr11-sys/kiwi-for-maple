const {chromium}=require('playwright');
const assert=require('node:assert/strict');
(async()=>{
  const browser=await chromium.launch();
  try{
    const page=await browser.newPage();
    const base=process.env.KIWI_TEST_URL||'http://127.0.0.1:8000';
    await page.goto(base+'/#quests');
    await page.locator('#db-search').fill('酋長蓋房子');
    let checkbox=page.locator('[data-quest-completed="2001"]');
    await checkbox.waitFor();
    assert.equal(await checkbox.isChecked(),false);
    await checkbox.check();
    await page.locator('.quest-completion.is-complete input[data-quest-completed="2001"]').waitFor();
    await page.reload();
    await page.locator('#db-search').fill('酋長蓋房子');
    await checkbox.waitFor();
    assert.equal(await checkbox.isChecked(),true);
    await page.locator('#quest-status').selectOption('incomplete');
    await checkbox.waitFor({state:'detached'});
    await page.locator('#quest-status').selectOption('completed');
    await checkbox.waitFor();
    await page.locator('[data-plan="2001"]').click();
    await page.goto(base+'/#plan');
    await page.getByRole('heading',{name:'我的材料清單'}).waitFor();
    checkbox=page.locator('[data-quest-completed="2001"]');
    assert.equal(await checkbox.isChecked(),true);
    await checkbox.uncheck();
    await page.locator('.quest-completion:not(.is-complete) input[data-quest-completed="2001"]').waitFor();
    assert.ok((await page.locator('main').innerText()).includes('石塊'));
    await page.goto(base+'/#quests');
    await page.locator('#quest-status').selectOption('all');
    await page.locator('#db-search').fill('酋長蓋房子');
    await page.locator('[data-detail="quests"][data-id="2001"]').click();
    await page.locator('#detail [data-quest-completed="2001"]').check();
    await page.locator('#detail .quest-completion.is-complete').waitFor();
    console.log('PASS: quest check/uncheck, reload persistence, progress filters, material plan and detail synchronization');
  }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exit(1)});
