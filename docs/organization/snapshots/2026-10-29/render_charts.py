from pathlib import Path
import xml.etree.ElementTree as E
import json,subprocess,concurrent.futures,os,shutil,tempfile
from datetime import datetime
OUT=Path(__file__).parent
NS='http://www.w3.org/2000/svg';E.register_namespace('',NS);E.register_namespace('xhtml','http://www.w3.org/1999/xhtml')
def tag(name):return '{'+NS+'}'+name
META={x['name']:(x['title'],x['subtitle'],x['footer']) for x in json.loads((OUT/'chart-catalog.json').read_text())}

def frame(name):
 raw=E.parse(OUT/(name+'.raw.svg')).getroot();vx,vy,w,h=map(float,raw.attrib['viewBox'].split())
 width=max(w+112,1180);left=(width-w)/2;top=204;height=h+292
 svg=E.Element(tag('svg'),{'xmlns:xlink':'http://www.w3.org/1999/xlink','id':raw.get('id','my-svg'),'width':str(width),'height':str(height),'viewBox':f'0 0 {width} {height}','role':'img','aria-labelledby':'chart-title chart-desc'})
 title,subtitle,footer=META[name]
 E.SubElement(svg,tag('title'),{'id':'chart-title'}).text='Pick Your AI — '+title
 E.SubElement(svg,tag('desc'),{'id':'chart-desc'}).text=subtitle+'. '+footer+'. Each team card links to GitHub.'
 defs=E.SubElement(svg,tag('defs'))
 pattern=E.SubElement(defs,tag('pattern'),{'id':'paper-grid','x':'0','y':'0','width':'26','height':'26','patternUnits':'userSpaceOnUse'})
 E.SubElement(pattern,tag('circle'),{'cx':'1','cy':'1','r':'0.7','fill':'#dce7eb'})
 E.SubElement(svg,tag('rect'),{'width':'100%','height':'100%','fill':'#f5f9fa'})
 E.SubElement(svg,tag('rect'),{'width':'100%','height':'100%','fill':'url(#paper-grid)','opacity':'0.52'})
 E.SubElement(svg,tag('rect'),{'x':'0','y':'0','width':str(width),'height':'7','fill':'#0f766e'})
 def text(x,y,value,size=16,fill='#526777',weight='400',spacing=None):
  a={'x':str(x),'y':str(y),'font-family':'Segoe UI, Arial, sans-serif','font-size':str(size),'fill':fill,'font-weight':weight}
  if spacing:a['letter-spacing']=str(spacing)
  E.SubElement(svg,tag('text'),a).text=value
 text(48,51,'PICK YOUR AI',15,'#0f766e','700',2.3)
 E.SubElement(svg,tag('circle'),{'cx':'190','cy':'45','r':'4','fill':'#f59e0b'})
 text(48,103,title,38,'#102f3e','700')
 text(48,136,subtitle,16,'#526777')
 for i,(label,color) in enumerate([('Research','#0f766e'),('Websites','#2563eb'),('Mobile','#7c3aed'),('Community','#d97706'),('Education','#c2410c')]):
  xx=48+i*154
  E.SubElement(svg,tag('circle'),{'cx':str(xx+5),'cy':'166','r':'5','fill':color})
  text(xx+18,171,label,13,'#526777','600')
 E.SubElement(svg,tag('rect'),{'x':'28','y':'188','width':str(width-56),'height':str(h+40),'rx':'22','fill':'#ffffff','stroke':'#dbe7eb','stroke-width':'1.25'})
 g=E.SubElement(svg,tag('g'),{'transform':f'translate({left-vx},{top-vy})'})
 for child in list(raw):g.append(child)
 text(48,height-35,footer,12,'#526777','600',0.35)
 date=datetime.fromisoformat(json.loads((OUT/'team-snapshot.json').read_text(encoding='utf-8'))['captured_at_utc']).strftime('%d %b %Y UTC').upper()
 text(width-48,height-35,date,12,'#526777','600',0.8)
 svg[-1].set('text-anchor','end')
 E.ElementTree(svg).write(OUT/(name+'.svg'),encoding='utf-8',xml_declaration=True)
 target=OUT/(name+'.svg')
 target.write_bytes(target.read_bytes().replace(b'\r\n',b'\n'))
 return {'name':name,'svg_width':width,'svg_height':height,'teams':len(E.parse(OUT/(name+'.raw.svg')).getroot().findall('.//'+tag('a')))}
def render(name):
 env=dict(os.environ,PUPPETEER_SKIP_DOWNLOAD='true')
 args=[shutil.which('npm.cmd') or shutil.which('npm') or 'npm','exec','--yes','--package=@mermaid-js/mermaid-cli@12.0.0','--','mmdc','-i',name+'.mmd','-o',name+'.raw.svg','-c','mermaid-config.json','-p',os.environ['CHART_PUPPETEER_CONFIG'],'-b','transparent']
 p=subprocess.run(args,cwd=OUT,env=env,capture_output=True,text=True,encoding='utf-8')
 if p.returncode:raise RuntimeError(p.stdout+p.stderr)
 raw=E.parse(OUT/(name+'.raw.svg')).getroot()
 expected=next(c for c in json.loads((OUT/'manifest.json').read_text())['charts'] if c['name']==name)
 count=sum(1 for el in raw.iter() if el.tag.endswith('}a'))
 if count!=len(expected['teams']):raise RuntimeError(f'{name}: rendered {count} team links, expected {len(expected["teams"])}')
 return frame(name)
if __name__=='__main__':
 chrome=os.environ.get('CHROME_PATH') or next((p for p in [shutil.which('google-chrome'),shutil.which('chromium'),shutil.which('chromium-browser'),r'C:\Program Files\Google\Chrome\Application\chrome.exe',r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe','/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'] if p and Path(p).is_file()),None)
 if not chrome:raise SystemExit('Set CHROME_PATH to an installed Chrome or Chromium executable.')
 with tempfile.TemporaryDirectory(prefix='pick-your-ai-charts-') as runtime:
  config=Path(runtime)/'puppeteer.json'
  config.write_text(json.dumps({'executablePath':chrome,'args':['--disable-gpu','--no-first-run']}),encoding='utf-8',newline='\n')
  os.environ['CHART_PUPPETEER_CONFIG']=str(config)
  with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:items=list(pool.map(render,META))
  (OUT/'render-metadata.json').write_text(json.dumps(items,indent=2)+'\n',newline='\n')
  p=subprocess.run(['node',str(OUT/'export_png.cjs')],cwd=OUT)
 if p.returncode:raise SystemExit(p.returncode)
 print('Rendered all current Mermaid charts to SVG and high-definition PNG.')
