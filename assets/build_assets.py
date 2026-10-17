"""Resize generated sources and typeset cards. Requires Pillow; SVG stays editable.

Usage: python assets/build_assets.py SOURCE_DIRECTORY [PNGQUANT_PATH]
Source filenames correspond to the selected built-in generations in PROMPTS.md.
"""
import base64
from io import BytesIO
from pathlib import Path
import sys
import shutil
import subprocess
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
SOURCE = Path(sys.argv[1])
PNGQUANT = str(Path(sys.argv[2]).resolve()) if len(sys.argv) > 2 else shutil.which("pngquant")
if not PNGQUANT:
    raise SystemExit("Install pngquant or pass the path to its executable.")
SOURCES = {
    'hero-dark': '82934a63-c888-42b8-9c36-d4a82e1a7edd',
    'hero-light': 'd3c178c7-2c92-416f-bf18-2828f831ef53',
    't0': '2ec5d548-47e2-4bb6-b6cc-a2b5b0c7a6fc',
    't1': '9940d75a-ddf6-4a45-9be8-53c5bdb0e7bb',
    't2': '93af1c9b-0bc5-4244-b6e9-9679f71403bd',
    't3': '36e8b9d7-6ff5-407e-a9c4-fdc868f20838',
    't4': '9e372391-aff6-4912-a9da-1038dd405ba8',
    't5': '9a4171b7-f2eb-4b87-b8c1-a1aa5503e6f2',
    't6': 'f253981e-c0d9-4d3c-9709-9a5a741c2dcf',
    'pickyour.ai': '750d0cbc-ae46-4c10-a6bf-2c7556e73098',
    'pick-your-ai-research': '78ad8159-5475-4fac-9023-a30ba9825ab4',
    'pick-your-ai-leaderboard': 'cd1afb6b-f3e1-4334-97f1-f9ab317c0b56',
    '.github': '5aa1cf9e-3846-4aaa-8f35-4eca4e829fb9',
    'pick-your-ai-android': '18808ea7-8adf-418d-96ff-88c6351714a5',
    'pick-your-ai-apple': 'bcbbb9a6-a379-4adb-ac7a-4b4ebb309b59',
}

def source(key, size):
    return Image.open(SOURCE / f'exec-{SOURCES[key]}.png').resize(size, Image.Resampling.LANCZOS)

def save_rgb(im, path):
    im.convert('RGB').save(path, optimize=True)
    subprocess.run([PNGQUANT, '--quality=65-85', '--speed=1', '--strip', '--force', '--output', str(path), str(path)], check=True)

mark = (ROOT / 'favicon.svg').read_text(encoding='utf-8').split('>', 1)[1].rsplit('</svg>', 1)[0]
for theme in ('dark', 'light'):
    path = ROOT / f'hero-{theme}.png'
    save_rgb(source(f'hero-{theme}', (1600, 500)), path)
    ink = '#f0fdfa' if theme == 'dark' else '#042f2e'
    secondary = '#5eead4' if theme == 'dark' else '#0f766e'
    embedded = BytesIO()
    Image.open(path).convert('RGB').save(embedded, format='WEBP', quality=90, method=6)
    raster = base64.b64encode(embedded.getvalue()).decode()
    (ROOT / f'banner-{theme}.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1600" height="500" viewBox="0 0 1600 500" role="img" aria-labelledby="title desc">
<title id="title">Pick Your AI</title><desc id="desc">Build a compatible AI stack, part by part. Conceptual modular components in a tray.</desc>
<image width="1600" height="500" xlink:href="data:image/webp;base64,{raster}"/>
<g transform="translate(64 104) scale(2.25)">{mark}</g>
<g font-family="system-ui, -apple-system, Segoe UI, sans-serif">
<text x="64" y="249" font-size="54" font-weight="700" fill="{ink}">Pick Your AI</text>
<text x="66" y="301" font-size="24" fill="{secondary}">Build a compatible AI stack,</text>
<text x="66" y="334" font-size="24" fill="{secondary}">part by part.</text>
</g></svg>''', encoding='utf-8')

for i in range(7):
    im = source(f't{i}', (128, 128)).convert('RGBA')
    assert im.getchannel('A').getextrema()[0] == 0, 'Source must have actual transparency'
    im.save(ROOT / 'tiers' / f't{i}.png', optimize=True)

font_dir = Path('C:/Windows/Fonts')
regular = lambda size: ImageFont.truetype(str(font_dir / 'segoeui.ttf'), size)
bold = lambda size: ImageFont.truetype(str(font_dir / 'segoeuib.ttf'), size)
labels = {
    'pickyour.ai': ('pickyour.ai', 'Application preview', 'Synthetic demonstration data'),
    'pick-your-ai-research': ('pick-your-ai-\nresearch', 'Research & evidence', 'Catalogs, pricing & shared contracts'),
    'pick-your-ai-leaderboard': ('pick-your-ai-\nleaderboard', 'Contributor recognition', 'Planned capabilities'),
    '.github': ('.github', 'Community foundations', 'Profile & shared guidance'),
    'pick-your-ai-android': ('pick-your-ai-\nandroid', 'Android client', 'Planning'),
    'pick-your-ai-apple': ('pick-your-ai-\napple', 'Apple / iOS client', 'Planning'),
}
for key, (name, role, status) in labels.items():
    im = source(key, (1280, 640)).convert('RGB')
    draw = ImageDraw.Draw(im)
    draw.text((56, 65), 'Pick Your AI', font=bold(25), fill='#f0fdfa')
    draw.line((56, 120, 365, 120), fill='#14b8a6', width=2)
    draw.ellipse((362, 116, 370, 124), fill='#fbbf24')
    draw.multiline_text((52, 207), name, font=bold(49), fill='#f0fdfa', spacing=6)
    draw.text((56, 395), role, font=regular(25), fill='#5eead4')
    draw.text((56, 553), status, font=regular(20), fill='#f0fdfa')
    save_rgb(im, ROOT / 'repo-cards' / ('github.png' if key == '.github' else key + '.png'))


# Half-size WebP thumbnails of the finished cards for the profile's repository grid.
(ROOT / 'repo-cards' / 'thumbs').mkdir(exist_ok=True)
for card in sorted((ROOT / 'repo-cards').glob('*.png')):
    Image.open(card).convert('RGB').resize((640, 320), Image.Resampling.LANCZOS).save(
        ROOT / 'repo-cards' / 'thumbs' / (card.stem + '.webp'), format='WEBP', quality=82, method=6)
