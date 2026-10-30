const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { execFileSync } = require('node:child_process');
const out = __dirname;
const suffix = process.env.CHART_EXPORT_SUFFIX || "";
const cacheRoot = process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, 'npm-cache') : execFileSync('npm', ['config','get','cache'], {encoding:'utf8'}).trim();
const cache = path.join(cacheRoot, '_npx');
const candidates = fs.readdirSync(cache).map(p => path.join(cache, p, 'node_modules')).filter(p => fs.existsSync(path.join(p, '@mermaid-js', 'mermaid-cli', 'package.json'))).sort((a,b) => fs.statSync(b).mtimeMs - fs.statSync(a).mtimeMs);
const puppeteer = require(require.resolve('puppeteer', { paths: candidates }));
(async () => {
  const browser = await puppeteer.launch(JSON.parse(fs.readFileSync(process.env.CHART_PUPPETEER_CONFIG, 'utf8').replace(/^\uFEFF/, '')));
  try {
    const entries = JSON.parse(fs.readFileSync(path.join(out, 'render-metadata.json'), 'utf8'));
    for (const entry of entries) {
      const width = ['organization-complete','github-team-hierarchy'].includes(entry.name) ? 16000 : 5000;
      const height = Math.ceil(width * entry.svg_height / entry.svg_width);
      const page = await browser.newPage();
      await page.setViewport({width, height, deviceScaleFactor:1});
      await page.goto(pathToFileURL(path.join(out, entry.name + '.svg')).href);
      await page.evaluate(({width,height}) => {
        const svg = document.documentElement;
        svg.setAttribute('width', width);
        svg.setAttribute('height', height);
        svg.style.display = 'block';
      }, {width,height});
      await page.evaluate(() => document.fonts.ready);
      await page.screenshot({path:path.join(out, entry.name + suffix + '.png'), clip:{x:0,y:0,width,height}});
      entry.png_width=width;entry.png_height=height;entry.png_file=entry.name+suffix+".png";
      await page.setViewport({width:1800,height:Math.ceil(1800*entry.svg_height/entry.svg_width),deviceScaleFactor:1});
      await page.evaluate(({width,height})=>{document.documentElement.setAttribute('width',width);document.documentElement.setAttribute('height',height);},{width:1800,height:Math.ceil(1800*entry.svg_height/entry.svg_width)});
      await page.screenshot({path:path.join(out, entry.name + suffix + '.preview.png'),clip:{x:0,y:0,width:1800,height:Math.ceil(1800*entry.svg_height/entry.svg_width)}});
      console.log(entry.name + ': ' + width + ' x ' + height + ' PNG');
      await page.close();
    }
    fs.writeFileSync(path.join(out, 'render-metadata.json'),JSON.stringify(entries,null,2)+'\n');
  } finally { await browser.close(); }
})();
