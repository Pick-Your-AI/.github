from pathlib import Path
import json,html,re
out=Path(__file__).parent
s=json.loads((out/'team-snapshot.json').read_text());teams={t['slug']:t for t in s['teams']};names={t['name']:t['slug'] for t in s['teams']}
ids={slug:'team_'+str(t['id']) for slug,t in teams.items()}
actual={slug:t['parent'] for slug,t in teams.items()};parents=dict(actual)
for slug,t in teams.items():
 if t['name'].startswith('Lead Maintainers - '):
  scope=names.get(t['name'].split(' - ',1)[1])
  if scope:
   parents[slug]=actual[scope];parents[scope]=slug
if all(k in teams for k in ['research','research-maintainers','lead-maintainers-research']):
 parents['research-maintainers']='lead-maintainers-research';parents['research']='research-maintainers'
for slug in teams:
 seen=set();cur=slug
 while cur:
  assert cur not in seen,('cycle',slug);seen.add(cur);cur=parents.get(cur)
config={'maxTextSize':300000,'maxEdges':1000,'theme':'base','securityLevel':'loose','fontFamily':'Segoe UI, Arial, sans-serif','themeVariables':{'fontFamily':'Segoe UI, Arial, sans-serif','fontSize':'16px','lineColor':'#8fa5b6','primaryColor':'#f8fafc','primaryTextColor':'#163042','primaryBorderColor':'#cbd5e1','edgeLabelBackground':'#f8fafc'},'flowchart':{'htmlLabels':True,'curve':'basis','nodeSpacing':22,'rankSpacing':46,'padding':16,'useMaxWidth':False},'themeCSS':'.node rect {rx:13px;ry:13px;} .nodeLabel p {margin:0;line-height:1.5;} .label foreignObject {overflow:visible;}'}
(out/'mermaid-config.json').write_text(json.dumps(config,indent=2)+'\n',newline='\n')
classes='''
 classDef owner fill:#102f3e,stroke:#102f3e,color:#fff,stroke-width:2px;
 classDef governance fill:#edf2f7,stroke:#94a3b8,color:#243c4b;
 classDef researchLead fill:#0f766e,stroke:#0f766e,color:#fff,stroke-width:2px;
 classDef research fill:#f0fdfa,stroke:#5eead4,color:#134e4a;
 classDef webLead fill:#1d4ed8,stroke:#1d4ed8,color:#fff,stroke-width:2px;
 classDef web fill:#eff6ff,stroke:#93c5fd,color:#1e3a8a;
 classDef mobileLead fill:#6d28d9,stroke:#6d28d9,color:#fff,stroke-width:2px;
 classDef mobile fill:#f5f3ff,stroke:#c4b5fd,color:#4c1d95;
 classDef educationLead fill:#c2410c,stroke:#c2410c,color:#fff,stroke-width:2px;
 classDef education fill:#fff7ed,stroke:#fdba74,color:#7c2d12;
 classDef community fill:#fffbeb,stroke:#fbbf24,color:#78350f;
'''
def area(slug):
 ancestry=set();cur=slug
 while cur:
  ancestry.add(cur);cur=actual.get(cur)
 if slug=='early-contributors':return 'community'
 if 'education' in ancestry or slug=='lead-maintainers-education':return 'education'
 if 'websites' in ancestry:return 'web'
 if 'mobile-apps' in ancestry:return 'mobile'
 if slug in ['organization-maintainers','research-maintainers']:return 'governance'
 return 'research'
def style(slug):
 a=area(slug)
 return a+'Lead' if teams[slug]['name'].startswith('Lead Maintainers - ') else a

def node(slug):
 t=teams[slug];direct=sorted([m for m in t['members'] if not m['inherited']],key=lambda m:(m['role']!='maintainer',m['login'].lower()))
 n=t['name'];width=340 if len(direct)>8 else 218
 if n.startswith('Lead Maintainers - '):heading="<span style='font-size:10px;letter-spacing:1px'>LEAD MAINTAINERS</span><br/><b>"+html.escape(n.split(' - ',1)[1])+'</b>'
 elif ' - ' in n:heading="<span style='font-size:10px'>"+html.escape(n.split(' - ',1)[0])+"</span><br/><b>"+html.escape(n.split(' - ',1)[1])+'</b>'
 else:heading='<b>'+html.escape(n)+'</b>'
 def roster(ms):return '<br/>'.join(('★ ' if m['role']=='maintainer' else '')+html.escape(m['login']) for m in ms)
 if len(direct)>8:
  half=(len(direct)+1)//2;body="<div style='display:flex;gap:10px'><div style='width:50%'>"+roster(direct[:half])+"</div><div style='width:50%'>"+roster(direct[half:])+"</div></div>"
 else:body=roster(direct) or "<span style='font-style:italic'>No direct members</span>"
 inherited=sum(m['inherited'] for m in t['members']);tail=("<br/><span style='font-size:10px'>+ "+str(inherited)+' through child teams</span>') if inherited else ''
 if t['pending']:
  pending='<br/>'.join(('☆ ' if m['role']=='maintainer' else '○ ')+html.escape(m['login']) for m in t['pending'])
  tail+="<div style='border-top:1px dashed currentColor;margin-top:8px;padding-top:6px;font-size:12px;text-align:left'><span style='font-size:10px'>PENDING INVITATION</span><br/>"+pending+'</div>'
 label=f"<div style='width:{width}px;text-align:center;line-height:1.5'>{heading}<br/><span style='font-size:10px;letter-spacing:0.6px'>DIRECT MEMBERS</span><div style='font-size:12px;text-align:left;margin-top:5px'>{body}</div>{tail}</div>"
 return ' '+ids[slug]+'["'+label+'"]:::'+style(slug)

def descendants(root):
 found={root}
 while True:
  more={child for child,parent in parents.items() if parent in found};after=found|more
  if after==found:return sorted(found)
  found=after
catalog=[];manifest=[]
def write(filename,label,slugs,parentmap,owner=False,full=False):
 slugs=sorted(slugs);edges=[(parentmap[x],x) for x in slugs if parentmap[x] in slugs]
 lines=['%% Live GitHub snapshot '+s['captured_at_utc'],'%% Includes all direct members and pending invitees.','flowchart TB']
 if owner:lines+=[' owner["<b>Pick Your AI</b><br/>Organization owner<br/>'+html.escape(' · '.join(s['owners']))+'"]:::owner']
 lines += [node(slug) for slug in slugs]
 if owner:
  lines+=[' owner --> '+ids[slug] for slug in slugs if parentmap[slug] is None]
 lines += [' '+ids[a]+' --> '+ids[b] for a,b in edges];lines += [classes]
 lines += [' click '+ids[slug]+' "'+teams[slug]['html_url']+'" "'+html.escape(teams[slug]['name'])+'" _blank' for slug in slugs]
 (out/(filename+'.mmd')).write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
 subtitle=f"{len(slugs)} teams · every drilldown included · active and pending memberships shown"
 if full:subtitle=f"{len(slugs)} teams · {len({m['login'] for t in teams.values() for m in t['members']})} active people · {len(s['pending_invitations'])} pending invitees"
 catalog.append({'name':filename,'title':label,'subtitle':subtitle,'footer':'★ ACTIVE TEAM MANAGER · ☆ INVITED TEAM MANAGER · pending is not active'})
 manifest.append({'name':filename,'teams':slugs,'edges':edges})
write('organization-complete','The complete organization.',list(teams),parents,True,True)
write('github-team-hierarchy','The exact GitHub team hierarchy.',list(teams),actual,True,True)
for scope in ['AI Builder','AI Papers & Index','AI Tools & Platforms','Catalog Pipeline','Cloud Agents','Datasets & Benchmarks','Funding, Grants & Sustainability','Market & Competitive Intelligence','Hardware & Infrastructure','Websites','Mobile Apps','Education']:
 root=names['Lead Maintainers - '+scope] if 'Lead Maintainers - '+scope in names else names[scope]
 slug=names[scope];stem='area-'+slug
 write(stem,scope+'.',descendants(root),parents)
assert set(manifest[0]['teams'])==set(teams)
(out/'chart-catalog.json').write_text(json.dumps(catalog,indent=2)+'\n',newline='\n')
(out/'manifest.json').write_text(json.dumps({'teams':len(teams),'charts':manifest,'display_parents':parents},indent=2)+'\n',newline='\n')
print('Generated',len(manifest),'Mermaid charts covering',len(teams),'teams.')
