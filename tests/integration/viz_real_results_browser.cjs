/** 真实 CFD 文件的只读引用、双视图着色、数值 Probe 和资产重开验收。 */
const {chromium, expect} = require('../../packages/ai4e-viz/frontend/node_modules/@playwright/test');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');

(async () => {
  const root = process.env.VIS_EVIDENCE_ROOT;
  const token = process.env.VIS_CONTROL_TOKEN;
  if (!root || !token) throw new Error('必须指定证据目录与本次测试服务的控制令牌');
  const base = process.env.VIS_BROWSER_URL || 'http://127.0.0.1:18093';
  const cases = JSON.parse(fs.readFileSync(path.join(root, 'inputs.json')));
  const browser = await chromium.launch();
  const results = [];
  try {
    for (const item of cases) {
      const page = await browser.newPage({viewport:{width:1920, height:1080}});
      page.setDefaultTimeout(90000);
      const errors = [], sessions = [];
      page.on('pageerror', e => errors.push(e.message));
      page.on('console', m => {if (m.type() === 'error') errors.push(m.text());});
      page.on('response', async r => {
        if (r.url().endsWith('/api/phys/sessions') && r.request().method() === 'POST' && r.ok()) sessions.push((await r.json()).session_id);
      });
      const scope = {scope_id:`real:${item.id}`, project_id:'real', task_id:item.id, root:path.join(root,'tasks',item.id,'visualizations'), writable:true};
      const ref = {asset_id:item.id, revision:item.sha256};
      // 只有测试宿主经可信控制口交接路径；工作台仍只接收不透明上下文。
      const registered = await page.request.post(`${base}/internal/contexts`, {headers:{'x-vis-control':token}, data:{scope, sources:[{id:item.id, name:item.id, ref}], bindings:[{ref,path:item.path}]}});
      expect(registered.ok(), await registered.text()).toBe(true);
      const context = (await registered.json()).context_id;
      const command = async body => {
        const response = await page.request.post(`${base}/api/phys/sessions/${sessions.at(-1)}/commands`, {data:{context_id:context,command:body},timeout:90000});
        expect(response.ok(), await response.text()).toBe(true);
        return response.json();
      };
      const menu = async (frame, title, option) => {
        await frame.getByRole('button',{name:title,exact:true}).click();
        await frame.getByText(option,{exact:true}).click();
      };
      const started = Date.now();
      try {
        await page.goto(`${base}/workspace/#/phys?embed=1&context=${context}`);
        await page.getByRole('button',{name:'新建工作区',exact:true}).click();
        const frame = page.frameLocator('iframe');
        await frame.locator('.phys-tree').getByText('基础显示',{exact:true}).waitFor();
        const initial = await command({operation:'snapshot'});
        expect(initial.datasets[`base-${item.id}`].points).toBe(item.points);
        expect(initial.datasets[`base-${item.id}`].cells).toBe(item.cells);
        expect(initial.spec.pipeline).toHaveLength(1);
        expect(initial.spec.layers[0].field).toBeFalsy();
        const loadedMs = Date.now() - started;
        await frame.getByLabel('着色物理量',{exact:true}).click();
        await frame.getByRole('option',{name:`${item.truth} (point)`,exact:true}).click();
        await frame.getByRole('button',{name:'轴测',exact:true}).click();
        await frame.getByRole('button',{name:'左右分割',exact:true}).click();
        await frame.getByLabel('着色物理量',{exact:true}).click();
        await frame.getByRole('option',{name:`${item.prediction} (point)`,exact:true}).click();
        await expect.poll(async () => (await command({operation:'snapshot'})).spec.layers.map(l=>l.field?.name),{timeout:90000}).toEqual([item.truth,item.prediction]);
        await expect(frame.getByRole('button',{name:'下一帧',exact:true})).toBeDisabled();
        await frame.getByRole('button',{name:'Probe',exact:true}).click();
        for (const [i,axis] of [...'XYZ'].entries()) await frame.getByLabel(`空间坐标 ${axis}`,{exact:true}).fill(String(item.position[i]));
        await frame.getByLabel('标签物理量（空为全部）',{exact:true}).click();
        for (const field of [item.truth,item.prediction]) await frame.getByRole('option',{name:`point:${field}`,exact:true}).click();
        await frame.getByLabel('标签物理量（空为全部）',{exact:true}).press('Escape');
        await frame.getByRole('button',{name:'应用',exact:true}).click();
        await expect.poll(async () => Object.values((await command({operation:'snapshot'})).probes).some(p=>p.valid),{timeout:90000}).toBe(true);
        const beforeSave = await command({operation:'snapshot'});
        const probe = Object.values(beforeSave.probes)[0];
        for (const [field, expected] of Object.entries(item.expected)) {
          const actual = probe.fields[`point:${field}`];
          expect(Math.abs((Array.isArray(actual)?actual[0]:actual)-expected)).toBeLessThan(1e-5);
        }
        await menu(frame,'文件','保存配置');
        const name = `真实 ${item.id} 双字段 ${Date.now()}`;
        await page.getByLabel('可视化名称').fill(name);
        const savedResponse = page.waitForResponse(r=>r.url().endsWith('/api/visualizations') && r.request().method()==='POST');
        await page.getByRole('button',{name:'确 定',exact:true}).click();
        const saved = await (await savedResponse).json();
        expect(saved.visualization_id).toBeTruthy();
        await expect(page.getByRole('dialog')).toHaveCount(0);
        const assetRoot = path.join(scope.root,saved.visualization_id);
        expect(fs.existsSync(path.join(assetRoot,'exports'))).toBe(false);
        const config = fs.readFileSync(path.join(assetRoot,'revisions','000001','spec.json'),'utf8');
        expect(Buffer.byteLength(config)).toBeLessThan(20000);
        expect(config).not.toContain(item.path);
        await page.reload();
        await page.getByRole('combobox',{name:'已保存可视化'}).fill(name);
        await page.getByText(`${name} · r1`,{exact:true}).click();
        await frame.locator('.phys-tree').getByText('Probe 1',{exact:true}).waitFor();
        const reopened = await command({operation:'snapshot'});
        expect(reopened.spec).toEqual(beforeSave.spec);
        // 核对实际浏览器裁剪面，避免仅配置相机正确而大模型仍被截断。
        await expect.poll(() => frame.locator('.phys-viewport').evaluate((el,bounds) => {
          const tracker = [...el.querySelectorAll('span')].map(s=>s.__physTracker).find(Boolean);
          const renderers = tracker?.view.renderWindow.getRenderers().filter(r=>r.getLayer()===0) || [];
          return renderers.length === 2 && renderers.every(renderer => {
            const camera = renderer.getActiveCamera(), eye = camera.getPosition(), focal = camera.getFocalPoint();
            const direction = focal.map((v,i)=>v-eye[i]), length = Math.hypot(...direction);
            const [near,far] = camera.getClippingRange();
            for (const x of [bounds[0],bounds[1]]) for (const y of [bounds[2],bounds[3]]) for (const z of [bounds[4],bounds[5]]) {
              const depth = [x,y,z].reduce((sum,v,i)=>sum+(v-eye[i])*direction[i]/length,0);
              if (!(near < depth && depth < far)) return false;
            }
            return true;
          });
        },item.bounds),{timeout:90000}).toBe(true);
        await frame.getByText('RenderView2',{exact:true}).click();
        await frame.locator('.phys-tree').getByText('Probe 1',{exact:true}).click();
        // 已保存 Probe 从输入取字段，不能因自身没有网格而清空可编辑列表。
        await frame.getByLabel('标签物理量（空为全部）',{exact:true}).click();
        await expect(frame.getByRole('option',{name:`point:${item.truth}`,exact:true})).toBeVisible();
        await expect(frame.getByRole('option',{name:`point:${item.prediction}`,exact:true})).toBeVisible();
        await frame.getByLabel('标签物理量（空为全部）',{exact:true}).press('Escape');
        await expect(frame.locator('.phys-status')).toContainText(`${item.points} 点`);
        await menu(frame,'导出','图片 / 数据');
        await page.getByRole('dialog').getByRole('button',{name:/生\s*成/}).click();
        await expect(page.getByRole('link',{name:'view.png',exact:true})).toBeVisible({timeout:90000});
        const url = new URL(await page.getByRole('link',{name:'view.png',exact:true}).getAttribute('href'),base).href;
        const image = await page.request.get(url);
        expect(image.ok()).toBe(true);
        fs.writeFileSync(path.join(root,`${item.id}-export.png`),await image.body());
        await page.screenshot({path:path.join(root,`${item.id}-workspace.png`)});
        await frame.getByRole('button',{name:'导出 CSV',exact:true}).click();
        await expect(page.getByRole('dialog').getByText('csv',{exact:true})).toBeVisible();
        await page.getByRole('dialog').getByRole('button',{name:/生\s*成/}).click();
        await expect(page.getByRole('link',{name:'probe.csv',exact:true})).toBeVisible({timeout:90000});
        const csvUrl = new URL(await page.getByRole('link',{name:'probe.csv',exact:true}).getAttribute('href'),base).href;
        const csv = await page.request.get(csvUrl);
        expect(csv.ok()).toBe(true);
        const csvText = await csv.text();
        fs.writeFileSync(path.join(root,`${item.id}-probe.csv`),csvText);
        // 本清单只有单分量数字字段，导出必须可直接作为数值列消费。
        const [header,values] = csvText.trim().split(/\r?\n/).map(line=>line.split(','));
        expect(values[header.indexOf('valid')]).toBe('True');
        for (const [field, expected] of Object.entries(item.expected)) {
          expect(Math.abs(Number(values[header.indexOf(`point:${field}`)])-expected)).toBeLessThan(1e-5);
        }
        const afterExport = await page.request.get(`${base}/api/visualizations/${saved.visualization_id}`,{params:{context_id:context}});
        expect((await afterExport.json()).content_hash).toBe(saved.content_hash);
        expect(crypto.createHash('sha256').update(fs.readFileSync(item.path)).digest('hex')).toBe(item.sha256);
        expect(errors).toEqual([]);
        results.push({id:item.id,status:'passed',points:item.points,cells:item.cells,loaded_ms:loadedMs,asset:saved.visualization_id,probe,config_bytes:Buffer.byteLength(config),source_sha256:item.sha256});
        console.log(`PASS ${item.id}: ${item.points} points, ${item.cells} cells`);
      } catch (error) {
        await page.screenshot({path:path.join(root,`${item.id}-failure.png`)});
        console.error(errors);
        throw error;
      } finally {
        for (const id of sessions) await page.request.delete(`${base}/api/phys/sessions/${id}`,{params:{context_id:context}});
        await page.close();
        fs.writeFileSync(path.join(root,'results.json'),JSON.stringify(results,null,2));
      }
    }
  } finally {await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
