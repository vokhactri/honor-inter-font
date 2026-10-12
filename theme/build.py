"""Pack dist/Inter-Font-Honor.hnt, a font-only theme that sets Inter as the system font.

uv run -m theme.build
"""

import shutil
import zipfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'  # Inter
BUILD = ROOT / 'build'  # staging dir and preview images
DIST = ROOT / 'dist'  # the finished .hnt

TITLE = 'Inter'
VARIABLE = DATA / 'inter/InterVariable.ttf'
WEIGHTS = range(100, 1000, 100)

DESCRIPTION = f"""<?xml version="1.0" encoding="UTF-8"?>
<HwTheme>
\t<title>{TITLE}</title>
\t<title-cn>{TITLE}</title-cn>
\t<author>trivk</author>
\t<designer>trivk</designer>
\t<screen>FHD</screen>
\t<version>3.0.2</version>
\t<font>{TITLE}</font>
\t<font-cn>{TITLE}</font-cn>
\t<transition>None</transition>
\t<type>font</type>
</HwTheme>
"""

# MagicOS reads this before fonts/DroidSansChinese.ttf: one variable file, one wght instance per weight,
# so bold text is real bold and the font weight slider in Settings keeps working
FONTS_XML = (
    '<?xml version="1.0" encoding="utf-8"?>\n<familyset>\n    <family>\n'
    + '\n'.join(
        f'        <font weight="{w}" style="normal">InterVariable.ttf\n'
        f'            <axis tag="wght" stylevalue="{w}"/>\n        </font>'
        for w in WEIGHTS
    )
    + '\n    </family>\n</familyset>\n'
)

# Layouts copied from the built-in "Android" font theme (Droidsansfallback.hwt): each line is
# (text, top y, ink height in the original, x or 'c' to centre, grey, weight). Font sizes are fitted so
# each line's ink height matches the original, so the cards sit next to the stock ones without jumping.
CARD = [
    ('ABCDEFGHIJKLMN', 283, 88, 'c', 0, 400),
    ('OPQRSTUVWXYZ', 423, 101, 'c', 0, 400),
    ('1234567890', 578, 69, 'c', 0, 400),
    (TITLE, 769, 58, 'c', 20, 400),
]
# the stock _cn card leads with Chinese, which Inter lacks
CARD_CN = [
    ('Go beyond', 154, 67, 'c', 0, 700),
    ('1234567890', 255, 46, 'c', 19, 400),
    (TITLE, 364, 38, 'c', 19, 400),
]
PREVIEW = [
    ('Go beyond', 378, 97, 200, 0, 400),
    ('Creating a new intelligent world', 673, 62, 200, 0, 400),
    ('for everyone', 760, 63, 200, 0, 400),
    (TITLE, 1359, 46, 200, 102, 400),
]


def face(px: int, wght: int) -> ImageFont.FreeTypeFont:
    ft = ImageFont.truetype(str(VARIABLE), px, layout_engine=ImageFont.Layout.BASIC)
    ft.set_variation_by_axes([14, wght])  # opsz 14, the text cut, like on the phone
    return ft


def fit(text: str, height: int, wght: int) -> ImageFont.FreeTypeFont:
    """The largest size whose ink for `text` is at most `height` px tall."""
    lo, hi = 8, 400
    while lo < hi:
        mid = (lo + hi + 1) // 2
        top, bottom = face(mid, wght).getbbox(text)[1::2]
        lo, hi = (mid, hi) if bottom - top <= height else (lo, mid - 1)
    return face(lo, wght)


def draw(size: tuple[int, int], lines: list, path: Path) -> None:
    im = Image.new('RGB', size, (255, 255, 255))
    d = ImageDraw.Draw(im)
    for text, top, height, x, grey, wght in lines:
        ft = fit(text, height, wght)
        left, t, right, _ = ft.getbbox(text)
        x0 = (size[0] - (right - left)) / 2 if x == 'c' else x
        d.text((x0 - left, top - t), text, font=ft, fill=(grey,) * 3)
    im.save(path, quality=92) if path.suffix == '.jpg' else im.save(path)


def zipdir(zf: zipfile.ZipFile, root: Path, rel: str) -> None:
    """Add a file or directory (with its directory entries, like `zip -r`)."""
    path = root / rel
    if path.is_dir():
        zf.write(path, rel + '/')
        for c in sorted(path.iterdir()):
            zipdir(zf, root, f'{rel}/{c.name}')
    else:
        zf.write(path, rel)


def main() -> None:
    stage = BUILD / 'stage'
    shutil.rmtree(stage, ignore_errors=True)
    fonts, preview = stage / 'fonts', stage / 'preview'
    fonts.mkdir(parents=True)
    preview.mkdir()
    # the Themes app drops any theme without an `icons` entry (j.isValidThemeInfo); an empty directory passes
    (stage / 'icons').mkdir()

    (stage / 'description.xml').write_text(DESCRIPTION)
    shutil.copy(VARIABLE, fonts)
    (fonts / 'online_variable_fonts.xml').write_text(FONTS_XML)
    # used only if the phone ignores online_variable_fonts.xml: one weight, faked bold
    shutil.copy(DATA / 'inter/Inter-Regular.ttf', fonts / 'DroidSansChinese.ttf')
    for n in ('pic_font_default.jpg', 'pic_font_default_en.jpg'):
        draw((1432, 1024), CARD, fonts / n)
    draw((716, 512), CARD_CN, fonts / 'pic_font_default_cn.jpg')
    for n in ('preview_fonts_0_50.png', 'preview_fonts_0_50_en.png', 'preview_fonts_0_50_cn.png'):
        draw((1440, 1616), PREVIEW, preview / n)

    DIST.mkdir(exist_ok=True)
    hnt = DIST / f'{TITLE}-Font-Honor.hnt'
    with zipfile.ZipFile(hnt, 'w', zipfile.ZIP_STORED) as zf:
        for rel in ('icons', 'description.xml', 'fonts', 'preview'):
            zipdir(zf, stage, rel)
    with zipfile.ZipFile(hnt) as zf:
        assert zf.testzip() is None
    print(f'{hnt.name}: {hnt.stat().st_size} bytes')


if __name__ == '__main__':
    main()
