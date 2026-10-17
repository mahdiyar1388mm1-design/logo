#!/usr/bin/env python3
"""Create a dependency-free, offline-capable download gallery for the 41 logos."""
from html import escape
from pathlib import Path
import json

from PIL import Image
from build_logos import filename

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "deliverables"
COUNTRIES = json.loads((ROOT / "countries.json").read_text())
DOWNLOAD_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/></svg>'


def main():
    (OUT / "thumbnails").mkdir(exist_ok=True)
    cards = []
    for i, country in enumerate(COUNTRIES, 1):
        name, code, fa = country["name"], country["code"], country["fa"]
        image_path = "logos/" + filename(i, country)
        image = Image.open(OUT / image_path)
        image.resize((440, 442), Image.Resampling.LANCZOS).save(
            OUT / "thumbnails" / f"{code}.webp", quality=86, method=6
        )
        cards.append(f'''
<article class="country-card" data-code="{code}" data-region="{country['region']}" data-name="{escape(name)}" data-fa="{fa}">
  <a class="preview-link" href="{image_path}" aria-label="نمایش لوگوی {fa}">
    <img src="thumbnails/{code}.webp" alt="لوگوی Free Recruiters {name} با پرچم {fa}" width="440" height="442" loading="{'eager' if i < 5 else 'lazy'}" decoding="async">
    <span class="edition" aria-hidden="true">{i:02d} / 41</span>
    <span class="expand" aria-hidden="true">↗</span>
  </a>
  <div class="card-details"><div><h2>{fa}</h2><p lang="en" dir="ltr">{escape(name)}</p></div>
  <a class="single-download" href="{image_path}" download aria-label="دانلود لوگوی {fa} با فرمت PNG">{DOWNLOAD_ICON}<span>PNG</span></a></div>
</article>''')

    size = (OUT / "Free_Recruiters_41_Countries.zip").stat().st_size / 1024**2
    template = '''<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#0c1421">
<title>۴۱ لوگوی کشورها | Free Recruiters</title>
<style>
:root{color-scheme:dark;--bg:#0c1421;--panel:#141e2d;--line:#2a3545;--gold:#d9b978;--text:#f4eee3;--muted:#a4afbe}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font-family:Tahoma,Arial,sans-serif;line-height:1.7}a{color:inherit;text-decoration:none}button,input{font:inherit}button,a,input{ -webkit-tap-highlight-color:transparent}button{cursor:pointer}button:focus-visible,a:focus-visible,input:focus-visible{outline:2px solid var(--gold);outline-offset:5px}svg{width:20px;height:20px;flex-shrink:0}button{color:inherit} [hidden]{display:none!important}
.container{width:min(1440px,100% - 72px);margin:auto}.topbar{border-bottom:1px solid var(--line);padding:24px 0}.topbar-inner{display:flex;align-items:center;justify-content:space-between;gap:24px}.brand{font-family:Georgia,'Times New Roman',serif;font-weight:bold;letter-spacing:2px;font-size:20px;color:var(--gold)}.topnote{font-size:12px;color:var(--muted);display:flex;align-items:center;gap:10px}.dot{width:6px;height:6px;border-radius:50%;background:var(--gold)}
.hero{padding:52px 0 38px;display:flex;align-items:center;justify-content:space-between;gap:40px}.eyebrow{font-size:12px;letter-spacing:1px;color:var(--gold);margin:0 0 14px}h1{font-size:clamp(27px,3.2vw,44px);line-height:1.5;font-weight:600;margin:0 0 16px}.intro{font-size:14px;color:var(--muted);line-height:2.1;margin:0;max-width:610px}.hero-actions{display:flex;flex-direction:column;gap:12px;min-width:254px}.primary,.secondary{display:flex;gap:12px;align-items:center;justify-content:center;border-radius:6px;font-size:14px;padding:14px 22px;font-weight:bold;transition:background .18s}.primary{background:var(--gold);color:#172031;border:1px solid var(--gold)}.primary:hover{background:#edcf95}.secondary{border:1px solid var(--line);color:var(--text);background:transparent}.secondary:hover{background:#1d293b}.size{font-size:11px;font-weight:normal;opacity:.75}.specs{display:flex;gap:9px;align-items:center;margin-top:23px;color:#c5ceda;font-size:11px;flex-wrap:wrap}.specs span{border:1px solid var(--line);border-radius:4px;padding:4px 10px}
.browser{border-top:1px solid var(--line);padding-top:25px}.toolbar{display:flex;align-items:center;justify-content:space-between;gap:24px;margin-bottom:24px;flex-wrap:wrap}.filters{display:flex;gap:7px;flex-wrap:wrap}.filter{background:transparent;border:1px solid transparent;border-radius:5px;padding:8px 14px;color:var(--muted);font-size:12px;white-space:nowrap}.filter:hover{color:var(--text);background:var(--panel)}.filter[aria-pressed=true]{border-color:#7a6744;background:#29271f;color:#efd6a6}.search{position:relative;flex:0 1 300px}.search svg{position:absolute;right:14px;top:13px;color:var(--muted)}input{color:var(--text);width:100%;padding:10px 43px 10px 14px;border-radius:5px;background:var(--panel);border:1px solid var(--line);font-size:13px}input::placeholder{color:#929eae}.result-line{display:flex;justify-content:space-between;align-items:center;color:var(--muted);font-size:11px;margin-bottom:17px}.result-line p{margin:0}.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:22px}.country-card{min-width:0;border:1px solid var(--line);border-radius:8px;background:var(--panel);overflow:hidden;transition:border-color .2s,transform .2s}.country-card:hover{border-color:#8b744b;transform:translateY(-3px)}.preview-link{display:block;position:relative;aspect-ratio:440/442;overflow:hidden}.preview-link img{display:block;width:100%;height:100%;object-fit:contain}.edition{position:absolute;top:12px;right:12px;border:1px solid #ffffff20;background:#0c1421c9;border-radius:4px;padding:2px 7px;color:#e4d5b7;font-size:10px;direction:ltr;letter-spacing:.6px}.expand{position:absolute;bottom:12px;left:12px;background:#0c1421c9;border:1px solid #ffffff20;width:30px;height:30px;line-height:28px;text-align:center;border-radius:50%;color:#e9d2a1;font-size:19px;opacity:0;transition:opacity .2s}.country-card:hover .expand,.preview-link:focus .expand{opacity:1}.card-details{display:flex;justify-content:space-between;align-items:center;padding:15px 17px}.card-details h2{font-size:14px;margin:0;font-weight:normal}.card-details p{font-size:11px;color:var(--muted);margin:1px 0 0;text-align:right;letter-spacing:.2px}.single-download{display:flex;align-items:center;gap:7px;color:var(--gold);padding:7px 9px;border:1px solid #77633d66;border-radius:4px;font-size:10px;direction:ltr}.single-download:hover{background:#d9b97812}.single-download svg{width:16px;height:16px}.empty{text-align:center;color:var(--muted);padding:60px}.empty button{background:transparent;border:0;border-bottom:1px solid var(--gold);color:var(--gold)}footer{margin-top:46px;padding:26px 0 34px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:20px;color:var(--muted);font-size:11px}footer a{color:var(--gold)}
dialog{width:min(850px,calc(100% - 32px));max-height:95dvh;padding:0;border:1px solid #6c5c40;background:#101a29;color:var(--text);border-radius:12px;overflow:auto}dialog::backdrop{background:#040912df;backdrop-filter:blur(6px)}.modal-top{display:flex;justify-content:space-between;align-items:center;padding:14px 20px;gap:20px;position:sticky;top:0;background:#101a29;z-index:2}.modal-top h2{margin:0;font-size:16px;font-weight:normal}.modal-top p{margin:0;color:var(--muted);font-size:11px;direction:ltr;text-align:right}.close{background:transparent;border:1px solid var(--line);border-radius:50%;width:36px;height:36px;font-size:24px;line-height:1;color:var(--muted)}.modal-image{display:block;max-width:100%;width:auto;max-height:70dvh;margin:auto;object-fit:contain}.modal-bottom{padding:15px 20px;display:flex;justify-content:space-between;gap:20px;align-items:center}.modal-bottom p{color:var(--muted);font-size:11px;margin:0}.modal-bottom .primary{font-size:12px;padding:10px 18px}
@media(min-width:1600px){.container{width:min(1600px,100% - 100px)}}@media(max-width:1100px){.grid{grid-template-columns:repeat(3,minmax(0,1fr))}.container{width:calc(100% - 48px)}.hero{gap:26px}.hero-actions{min-width:230px}.search{flex-basis:250px}}@media(max-width:800px){.grid{grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}.hero{display:block;padding:34px 0}.hero-actions{flex-direction:row;margin-top:28px;min-width:0;flex-wrap:wrap}.hero-actions>a{flex:1;white-space:nowrap}.search{flex-basis:100%;max-width:none}.toolbar{gap:15px}.topnote{font-size:10px}.topbar{padding:18px 0}.brand{font-size:16px;letter-spacing:1px}}@media(max-width:480px){.container{width:calc(100% - 28px)}.topnote span:last-child{display:none}.grid{gap:12px;grid-template-columns:1fr}.hero-actions{flex-direction:column}.filters{gap:2px;flex-wrap:nowrap;overflow-x:auto;width:100%}.filter{font-size:11px;padding:8px 10px}h1{font-size:28px}.intro{font-size:12px}.result-line p:last-child{display:none}footer{flex-direction:column;gap:8px}.card-details{padding:16px 18px}.card-details h2{font-size:16px}.modal-bottom p{display:none}.modal-bottom .primary{width:100%}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<header class="topbar"><div class="container topbar-inner"><a class="brand" href="./" lang="en" dir="ltr">FREE RECRUITERS</a><div class="topnote"><span class="dot"></span><span>مجموعهٔ لوگوهای کشورها</span></div></div></header>
<main class="container">
<section class="hero" aria-labelledby="page-title"><div><p class="eyebrow">مجموعهٔ بین‌المللی · ۴۱ کشور</p><h1 id="page-title">یک هویت، ۴۱ کشور.</h1><p class="intro">همان قاب طلایی و نشان اصلی؛ با نام و پرچم اختصاصی هر کشور.<br>نسخهٔ موردنظرتان را جداگانه دریافت کنید یا مجموعهٔ کامل را دانلود کنید.</p><div class="specs"><span>۴۱ فایل مجزا</span><span dir="ltr">PNG · 1024 × 1029 px</span><span>ابعاد تصویر اصلی</span></div></div><div class="hero-actions"><a class="primary" href="Free_Recruiters_41_Countries.zip" download>__DOWNLOAD__<span>دانلود همهٔ لوگوها <span class="size" dir="ltr">ZIP · __SIZE__ MB</span></span></a><a class="secondary" href="All_Countries_Preview.jpg" target="_blank" rel="noopener">نمای کلی ۴۱ لوگو <span aria-hidden="true">↗</span></a></div></section>
<section class="browser" aria-label="گالری لوگوها"><div class="toolbar"><div class="filters" role="group" aria-label="فیلتر قاره"><button class="filter" data-region="all" aria-pressed="true">همهٔ کشورها</button><button class="filter" data-region="South America" aria-pressed="false">آمریکای جنوبی</button><button class="filter" data-region="Africa" aria-pressed="false">آفریقا</button><button class="filter" data-region="Asia" aria-pressed="false">آسیا</button><button class="filter" data-region="Europe" aria-pressed="false">اروپا</button></div><label class="search"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m16 16 4.5 4.5"/></svg><input id="country-search" type="search" placeholder="جست‌وجوی نام کشور…" aria-label="جست‌وجوی کشور به فارسی یا انگلیسی" autocomplete="off"></label></div><div class="result-line"><p id="result-count" aria-live="polite">۴۱ لوگو</p><p>برای مشاهدهٔ جزئیات، روی تصویر کلیک کنید.</p></div><div class="grid">__CARDS__</div><div class="empty" hidden><p>کشوری با این نام پیدا نشد.</p><button id="clear-search">نمایش همهٔ کشورها</button></div></section>
<footer><span>نام کشورها به انگلیسی · پس‌زمینهٔ اصلی حفظ شده است · فایل‌ها شفاف نیستند</span><a href="Free_Recruiters_41_Countries.zip" download>دریافت مجموعهٔ کامل ↓</a></footer>
</main>
<dialog id="preview" aria-labelledby="preview-title"><div class="modal-top"><div><h2 id="preview-title"></h2><p id="preview-english" lang="en"></p></div><button class="close" aria-label="بستن پیش‌نمایش" type="button">×</button></div><img class="modal-image" alt="" width="1024" height="1029"><div class="modal-bottom"><p>ابعاد اصلی · <span dir="ltr">1024 × 1029 px</span></p><a class="primary modal-download" href="" download>__DOWNLOAD__ دریافت فایل PNG</a></div></dialog>
<script>
'use strict';
const cards=[...document.querySelectorAll('.country-card')];
const filters=[...document.querySelectorAll('.filter')];
const search=document.querySelector('#country-search');
const empty=document.querySelector('.empty');
const counter=document.querySelector('#result-count');
let region='all';
const normalize=s=>s.normalize('NFKD').replace(/[\u0300-\u036f\u064b-\u065f\u0670\u200c\u200d]/g,'').replace(/[يى]/g,'ی').replace(/ك/g,'ک').toLowerCase().trim();
function update(){let count=0;const terms=normalize(search.value).split(/\s+/).filter(Boolean);for(const card of cards){const haystack=normalize(card.dataset.name+' '+card.dataset.fa+' '+card.dataset.code);const match=(region==='all'||card.dataset.region===region)&&terms.every(t=>haystack.includes(t));card.hidden=!match;if(match)count++;}counter.textContent=new Intl.NumberFormat('fa-IR').format(count)+' لوگو';empty.hidden=count!==0;}
search.addEventListener('input',update);
for(const button of filters)button.addEventListener('click',()=>{region=button.dataset.region;for(const filter of filters)filter.setAttribute('aria-pressed',String(filter===button));update();});
document.querySelector('#clear-search').addEventListener('click',()=>{search.value='';filters[0].click();search.focus();});
const dialog=document.querySelector('#preview');
const fullImage=dialog.querySelector('.modal-image');
let trigger=null;
for(const link of document.querySelectorAll('.preview-link'))link.addEventListener('click',event=>{if(!dialog.showModal||event.ctrlKey||event.metaKey||event.shiftKey||event.altKey)return;event.preventDefault();trigger=link;const card=link.closest('.country-card');document.querySelector('#preview-title').textContent=card.dataset.fa;document.querySelector('#preview-english').textContent='Free Recruiters '+card.dataset.name;fullImage.src=link.getAttribute('href');fullImage.alt='لوگوی Free Recruiters '+card.dataset.name;dialog.querySelector('.modal-download').href=link.getAttribute('href');dialog.showModal();document.body.style.overflow='hidden';});
dialog.querySelector('.close').addEventListener('click',()=>dialog.close());
dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
dialog.addEventListener('close',()=>{document.body.style.overflow='';if(trigger)trigger.focus();});
</script>
</body></html>
'''
    template = template.replace("__CARDS__", "\n".join(cards))
    template = template.replace("__DOWNLOAD__", DOWNLOAD_ICON).replace("__SIZE__", f"{size:.1f}")
    (OUT / "index.html").write_text(template)
    print(f"Gallery and {len(COUNTRIES)} thumbnails created.")


if __name__ == "__main__":
    main()
