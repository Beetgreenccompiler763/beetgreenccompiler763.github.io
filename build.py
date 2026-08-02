# -*- coding: utf-8 -*-
"""
مولّد الموقع — يبني كل صفحات HTML من قالب واحد.
شغّله بعد أي تعديل:   python3 build.py
الهيدر والفوتر موجودين مرة واحدة في template.html — عدّل هناك وهيتطبق على كل الصفحات.
"""
import json, os, sys, io, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from projects import PROJECTS, FILTERS, TESTIMONIALS

# ⚠️ غيّر السطر ده لعنوان موقعك الحقيقي (بشرطة مائلة في الآخر)
SITE = "https://iegy.github.io/"

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = open(os.path.join(HERE, 'template.html'), encoding='utf-8').read()
OG = "og.png"

PERSON_LD = {
  "@context": "https://schema.org", "@type": "Person",
  "name": "محمد حسين", "alternateName": "Mohammed Hussein",
  "jobTitle": "مطوّر برمجيات ومصمم تجارب رقمية",
  "url": SITE, "image": SITE + "og.png",
  "email": "mailto:egyup@outlook.com", "telephone": "+201000220606",
  "knowsLanguage": ["ar", "en"],
  "knowsAbout": ["Web Development", "Mobile Apps", "Business Management Systems", "Automation", "Arabic RTL Design"],
  "sameAs": ["https://github.com/iegy", "https://www.facebook.com/iegy.net",
             "https://www.instagram.com/iegyup", "https://youtube.com/@iegy", "https://tiktok.com/@moegyup"],
}


def render(slug, page, title, desc, body, jsonld=None, ogtype="website", ogimage=OG):
    html = BASE
    for k, v in {
        "title": title, "desc": desc, "site": SITE, "slug": slug, "page": page,
        "ogtype": ogtype, "ogimage": ogimage,
        "jsonld": json.dumps(jsonld or PERSON_LD, ensure_ascii=False, indent=0).replace("\n", ""),
        "body": body,
    }.items():
        html = html.replace("{{%s}}" % k, v)
    with io.open(os.path.join(HERE, slug), 'w', encoding='utf-8') as f:
        f.write(html)
    return slug


# ---------------------------------------------------------------- icons
ICON = {
 "web": '<path d="M3 12h18M12 3a15 15 0 0 1 0 18a15 15 0 0 1 0-18z"/><circle cx="12" cy="12" r="9"/>',
 "mobile": '<rect x="6" y="2.5" width="12" height="19" rx="2.5"/><path d="M10.5 18.5h3"/>',
 "system": '<rect x="3" y="4" width="18" height="5" rx="1.4"/><rect x="3" y="12.5" width="18" height="7.5" rx="1.4"/><path d="M6.5 6.5h.01M6.5 16h.01"/>',
 "bolt": '<path d="M13 2 4.5 13.5H11l-1 8.5 8.5-11.5H12l1-8.5z"/>',
 "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.6-3.6"/>',
 "build": '<path d="M14.7 6.3a4.5 4.5 0 0 0 5.9 5.9l-8 8a2.8 2.8 0 0 1-4-4l8-8z"/><path d="M14.7 6.3 17.5 3.5"/>',
 "ship": '<path d="M12 2v13"/><path d="m5.5 8.5 6.5-6.5 6.5 6.5"/><path d="M3 20.5h18"/>',
 "shield": '<path d="M12 2.5 20 6v6c0 5-3.4 8.4-8 9.5C7.4 20.4 4 17 4 12V6l8-3.5z"/>',
 "chart": '<path d="M4 20V10M10 20V4M16 20v-7M22 20H2"/>',
 "book": '<path d="M4 4.5A2.5 2.5 0 0 1 6.5 2H20v18H6.5A2.5 2.5 0 0 0 4 22.5z"/><path d="M4 17.5A2.5 2.5 0 0 1 6.5 15H20"/>',
}
def svg(name):
    return ('<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">%s</svg>' % ICON[name])


# ---------------------------------------------------------------- shared blocks
def work_card(p, idx=None):
    tags = "".join('<span class="tag">%s</span>' % t for t in p["tags"][:3])
    return f'''      <article class="work" data-cat="{p['cats']}">
        <a class="work-shot" href="work-{p['slug']}.html" aria-label="تفاصيل مشروع {p['short']}">
          <span class="work-idx">&lt;{p['n']}/&gt;</span>
          <img src="thumb-{p['slug']}.webp" alt="لقطة من مشروع {p['short']}" width="880" height="550" loading="lazy" decoding="async">
        </a>
        <div class="work-body">
          <h3><a href="work-{p['slug']}.html">{p['title']}</a></h3>
          <p>{p['teaser']}</p>
          <div>{tags}</div>
          <div class="work-foot">
            <a class="link-out" href="work-{p['slug']}.html">تفاصيل المشروع ←</a>
            <a class="link-out" href="{p['url']}" target="_blank" rel="noopener">زيارة الموقع ↗</a>
          </div>
        </div>
      </article>'''


CTA = '''<section class="section-alt">
  <div class="wrap reveal" style="text-align:center;max-width:620px">
    <div class="eyebrow">LET'S BUILD</div>
    <h2>عندك فكرة مشروع؟</h2>
    <p style="margin:14px auto 26px">خليني أساعدك أحوّلها لمنتج شغال — من أول استشارة الفكرة لحد التسليم والدعم بعده.</p>
    <a href="contact.html" class="btn btn-primary btn-lg">تواصل معايا الآن</a>
  </div>
</section>'''


# ---------------------------------------------------------------- pages
def home():
    cards = "\n".join(work_card(p) for p in PROJECTS[:3])
    services = [
      ("web", "تطوير مواقع الويب", "مواقع تعريفية وأنظمة إدارة مخصصة، بأداء سريع وتصميم يعكس هوية نشاطك."),
      ("mobile", "تطبيقات الموبايل", "تطبيقات أندرويد و iOS بواجهة عربية سلسة ودعم كامل لـ RTL."),
      ("system", "أنظمة إدارة الأعمال", "فوترة، مخزون، عملاء وموردين، وتقارير أرباح دقيقة بالمليم."),
      ("bolt", "أدوات وأتمتة مخصصة", "سكربتات بتلغي المهام المتكررة تمامًا — من إكسل لتقارير كاملة."),
    ]
    scards = "\n".join(f'''      <div class="card">
        <div class="card-icon">{svg(i)}</div>
        <h3>{t}</h3><p>{d}</p>
      </div>''' for i, t, d in services)

    if TESTIMONIALS:
        qs = "\n".join(f'''      <blockquote class="quote">
        <p>{txt}</p>
        <footer><span class="avatar">{who[0]}</span><span><cite>{who}</cite><small>{role}</small></span></footer>
      </blockquote>''' for txt, who, role in TESTIMONIALS)
        quotes = f'''<section>
  <div class="wrap">
    <div class="section-head reveal">
      <div class="eyebrow">CLIENTS</div>
      <h2>اللي العملاء قالوه</h2>
    </div>
    <div class="stagger grid-3">
{qs}
    </div>
  </div>
</section>'''
    else:
        quotes = ""

    body = f'''
<section style="padding-block:clamp(52px,8vw,104px) clamp(40px,6vw,76px)">
  <div class="wrap hero-split">
    <div class="reveal">
      <div class="eyebrow">DEVELOPER · DESIGNER · PROBLEM SOLVER</div>
      <h1>محمد حسين<br>يبني منتجات رقمية تُستخدم فعلًا،<br>مش مجرد أفكار على الورق.</h1>
      <p class="lead" style="margin-top:20px;max-width:520px">
        مواقع، تطبيقات موبايل، وأنظمة إدارة أعمال مصمّمة من الصفر لتناسب طبيعة شغلك —
        بأحدث الأدوات، وبعين حريصة على كل تفصيلة في الواجهة والتجربة.
      </p>
      <div style="display:flex;gap:14px;margin-top:30px;flex-wrap:wrap">
        <a href="contact.html" class="btn btn-primary btn-lg">ابدأ مشروعك</a>
        <a href="portfolio.html" class="btn btn-outline btn-lg">شاهد أعمالي</a>
      </div>
    </div>

    <div class="reveal terminal">
      <div class="term-dots">
        <span style="background:#E4894B"></span><span style="background:#D6C3A9"></span><span style="background:#9DA287"></span>
      </div>
      <div class="term-body">
        <span style="color:#9DA287">$</span> <span data-typing='["npm run build-idea", "function ابدأ() {{\\n  return مشروعك;\\n}}", "✓ deployed — جاهز للإطلاق"]'></span>
      </div>
    </div>
  </div>
</section>

<div class="wrap">
  <div class="stats stagger">
    <div class="stat"><b><span data-count="6" data-suffix="">0</span></b><span>مشاريع منشورة أونلاين</span></div>
    <div class="stat"><b><span data-count="4" data-suffix="">0</span></b><span>مجالات شغل أساسية</span></div>
    <div class="stat"><b><span data-count="100" data-suffix="%">0</span></b><span>واجهات عربية RTL</span></div>
    <div class="stat"><b><span data-count="1" data-suffix="">0</span></b><span>يوم عمل للرد عليك</span></div>
  </div>
</div>

<div class="wrap"><div class="divider">&lt;/&gt; ماذا أقدّم</div></div>

<section class="tight">
  <div class="wrap">
    <div class="section-head reveal">
      <h2>من الفكرة إلى منتج جاهز</h2>
      <p>أربعة مجالات أشتغل فيها بعمق، مش بشكل سطحي.</p>
    </div>
    <div class="stagger grid-4">
{scards}
    </div>
    <div style="margin-top:32px">
      <a href="services.html" class="btn btn-outline">كل الخدمات بالتفصيل ←</a>
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="eyebrow">SELECTED WORK</div>
      <h2>مشاريع اشتغلت عليها فعلًا</h2>
      <p>كل مشروع منهم شغّال أونلاين دلوقتي — تقدر تفتحه وتجربه بنفسك.</p>
    </div>
    <div class="stagger work-grid">
{cards}
    </div>
    <div style="margin-top:32px">
      <a href="portfolio.html" class="btn btn-outline">كل الأعمال ←</a>
    </div>
  </div>
</section>

{quotes}

{CTA}
'''
    return render("index.html", "home", "محمد حسين — مطوّر ومصمم رقمي",
        "محمد حسين، مطوّر برمجيات يبني مواقع وتطبيقات موبايل وأنظمة إدارة أعمال بواجهات عربية — من الفكرة إلى منتج يعمل.",
        body)


def about():
    steps = [
      ("01", "search", "أسمع المشكلة الحقيقية",
       "قبل أي سطر كود، بفهم طبيعة شغلك واحتياجك الفعلي — لأن نص المشاريع اللي بتفشل مش بتفشل في التنفيذ، بتفشل لأن حد فهم الطلب غلط من الأول."),
      ("02", "build", "أبني بأحدث الأدوات",
       "كود نظيف وقابل للتطوير، ومناسب لحجم مشروعك — من غير تعقيد زيادة ولا اختصارات هتوجعك بعد ستة شهور."),
      ("03", "ship", "تسليم واضح ومتابعة",
       "منتج جاهز للاستخدام فعليًا، مع شرح للاستخدام ودعم بعد التسليم — مش تسليم ملفات وسلام."),
    ]
    stepshtml = "\n".join(f'''      <div class="step">
        <div class="step-n">{n}</div>
        <div><h3>{t}</h3><p style="margin:6px 0 0">{d}</p></div>
      </div>''' for n, i, t, d in steps)

    skills = [
      ("web", "الواجهات الأمامية", ["HTML5", "CSS3", "JavaScript", "React"]),
      ("bolt", "البرمجة الخلفية والأتمتة", ["Python", "Node.js", "openpyxl"]),
      ("mobile", "تطبيقات الموبايل", ["React Native", "Flutter"]),
      ("system", "بيانات وتخزين", ["SQL", "localStorage", "Cloud Sync"]),
    ]
    skillshtml = "\n".join('''      <div class="card">
        <div class="card-icon">%s</div>
        <h3 style="font-size:1rem;margin-bottom:12px">%s</h3>
        <div>%s</div>
      </div>''' % (svg(i), t, "".join('<span class="tag">%s</span>' % x for x in xs))
      for i, t, xs in skills)

    body = f'''
<section>
  <div class="wrap about-split">
    <div class="reveal">
      <div style="clip-path:polygon(0 0,calc(100% - 34px) 0,100% 34px,100% 100%,0 100%);background:var(--sand);padding:14px">
        <img src="logo.webp" alt="محمد حسين" width="1040" height="714" fetchpriority="high"
             style="clip-path:polygon(0 0,calc(100% - 24px) 0,100% 24px,100% 100%,0 100%)">
      </div>
    </div>
    <div class="reveal">
      <div class="eyebrow">ABOUT</div>
      <h1 style="font-size:clamp(1.85rem,3.9vw,2.55rem)">مطوّر بيهتم بالتفاصيل،<br>وكاتب بيهتم باللغة.</h1>
      <p class="lead" style="margin-top:18px">
        أنا محمد حسين، مطوّر برمجيات بابني أدوات رقمية بتحل مشاكل حقيقية —
        من أنظمة إدارة مبيعات كاملة، لتطبيقات إدارة أموال شخصية، لتجربة قراءة رقمية مصممة لرواية عربية.
      </p>
      <p>
        بجانب البرمجة، عندي اهتمام خاص بالكتابة الأدبية العربية، وده بينعكس في شغلي كمطوّر:
        احترام اللغة، ترتيب الأفكار، والاهتمام بإيقاع الواجهة مش بس شكلها.
        النتيجة: منتجات واضحة، منظمة، وسهلة الاستخدام من أول لحظة.
      </p>
      <div style="margin-top:26px;display:flex;gap:14px;flex-wrap:wrap">
        <a href="portfolio.html" class="btn btn-primary">شوف أعمالي</a>
        <a href="mohammed-hussein-cv.pdf" class="btn btn-outline" download>حمّل السيرة الذاتية (PDF)</a>
      </div>
    </div>
  </div>
</section>

<div class="wrap"><div class="divider">&lt;/&gt; كيف بشتغل</div></div>

<section class="tight">
  <div class="wrap" style="max-width:860px">
    <div class="steps stagger">
{stepshtml}
    </div>
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="eyebrow">SKILLS</div>
      <h2>الأدوات اللي بشتغل بيها</h2>
      <p>مش قايمة تقنيات للزينة — دي الأدوات اللي المشاريع اللي تحت اتبنت بيها فعلًا.</p>
    </div>
    <div class="stagger grid-2">
{skillshtml}
    </div>
  </div>
</section>

{CTA}
'''
    return render("about.html", "about", "عني — محمد حسين",
        "محمد حسين: مطوّر برمجيات ومصمم تجارب رقمية، بيبني أدوات بتحل مشاكل حقيقية بواجهات عربية مضبوطة.",
        body, ogtype="profile")


def services():
    items = [
      ("01", "web", "تطوير مواقع الويب",
       "مواقع تعريفية، متاجر إلكترونية، وأنظمة إدارة مخصصة — مبنية بأداء سريع وتصميم يعكس هوية نشاطك.",
       ["HTML/CSS", "JavaScript", "React", "SEO"]),
      ("02", "mobile", "تطبيقات الموبايل",
       "تطبيقات أندرويد و iOS بواجهة عربية سلسة ودعم كامل لـ RTL، من الفكرة الأولى لحد النشر على المتاجر.",
       ["Flutter", "React Native"]),
      ("03", "system", "أنظمة إدارة الأعمال",
       "أنظمة فوترة ومخزون وعملاء وموردين، مع تقارير أرباح وخسائر دقيقة، مصممة خصيصًا لطريقة شغلك أنت.",
       ["JavaScript", "SQL", "Reporting"]),
      ("04", "bolt", "أدوات وأتمتة مخصصة",
       "سكربتات بتلغي المهام المتكررة — من معالجة ملفات إكسل لحد أتمتة تقارير كاملة تلقائيًا.",
       ["Python", "openpyxl", "Automation"]),
    ]
    cards = "\n".join(f'''      <div class="card">
        <div class="num">&lt;{n}/&gt;</div>
        <div class="card-icon">{svg(i)}</div>
        <h3>{t}</h3>
        <p style="margin:10px 0 16px">{d}</p>
        <div>{"".join('<span class="tag">%s</span>' % x for x in xs)}</div>
      </div>''' for n, i, t, d, xs in items)

    faqs = [
      ("المشروع بياخد قد إيه؟",
       "بيختلف حسب الحجم: موقع تعريفي من أسبوع لأسبوعين، ونظام إدارة كامل من شهر لشهرين. بحدد لك جدول زمني واضح قبل ما نبدأ، مش تقدير مفتوح."),
      ("بتشتغل بنظام إيه في الدفع؟",
       "دفعة مقدمة عند بدء الشغل، والباقي عند التسليم. لو المشروع كبير، بنقسمه لمراحل ولكل مرحلة تسليم ودفعة."),
      ("هل بتوفّر دعم بعد التسليم؟",
       "أيوة. التسليم بيشمل شرح للاستخدام وفترة دعم للتعديلات والمشاكل. وأي تطوير جديد بعد كده بنتفق عليه بشكل منفصل."),
      ("هل الكود بيبقى ملكي؟",
       "أيوة، الكود والملفات كلها بتبقى ملكك بالكامل بعد التسليم — من غير أي ارتباط بيا أو اشتراكات مخفية."),
    ]
    faqhtml = "\n".join(f'''      <div class="step">
        <div class="step-n">؟</div>
        <div><h3>{q}</h3><p style="margin:6px 0 0">{a}</p></div>
      </div>''' for q, a in faqs)

    faq_ld = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faqs]}

    body = f'''
<section>
  <div class="wrap section-head reveal">
    <div class="eyebrow">SERVICES</div>
    <h1 style="font-size:clamp(1.85rem,3.9vw,2.55rem)">خدمات بتحل مشاكل حقيقية،<br>مش مجرد تنفيذ.</h1>
    <p class="lead" style="margin-top:16px">كل مشروع بيتبنى من الصفر حسب طبيعة شغلك، مفيش قوالب جاهزة بتتكرر لكل عميل.</p>
  </div>
  <div class="wrap stagger grid-2">
{cards}
  </div>
</section>

<section class="section-alt">
  <div class="wrap">
    <div class="section-head reveal">
      <div class="eyebrow">PROCESS</div>
      <h2>إزاي بنمشي في المشروع</h2>
    </div>
    <div class="steps stagger" style="max-width:860px">
      <div class="step"><div class="step-n">01</div><div><h3>مكالمة أو رسالة تعريفية</h3><p style="margin:6px 0 0">تحكيلي عن المشكلة والهدف، وأسألك الأسئلة اللي توضّح الصورة.</p></div></div>
      <div class="step"><div class="step-n">02</div><div><h3>عرض بمدة وسعر واضحين</h3><p style="margin:6px 0 0">تحديد نطاق الشغل بالظبط، بجدول زمني وسعر ثابت — من غير مفاجآت.</p></div></div>
      <div class="step"><div class="step-n">03</div><div><h3>بناء على مراحل</h3><p style="margin:6px 0 0">تشوف النتيجة أول بأول بدل ما تستنى للآخر، وتقدر تعدّل في وقتها.</p></div></div>
      <div class="step"><div class="step-n">04</div><div><h3>تسليم ودعم</h3><p style="margin:6px 0 0">تسليم كامل مع شرح للاستخدام، وفترة دعم للتعديلات والمشاكل.</p></div></div>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <div class="section-head reveal">
      <div class="eyebrow">FAQ</div>
      <h2>أسئلة بتتسأل كتير</h2>
    </div>
    <div class="steps stagger" style="max-width:860px">
{faqhtml}
    </div>
  </div>
</section>

{CTA}
'''
    return render("services.html", "services", "خدماتي — محمد حسين",
        "تطوير مواقع وتطبيقات موبايل وأنظمة إدارة أعمال وأدوات أتمتة مخصصة — بمواصفات وجدول زمني واضح من البداية.",
        body, jsonld=faq_ld)


def portfolio():
    cards = "\n".join(work_card(p) for p in PROJECTS)
    fhtml = "\n".join('      <button class="filter" type="button" data-filter="%s" aria-pressed="%s">%s</button>'
                      % (k, "true" if k == "all" else "false", label) for k, label in FILTERS)
    ld = {"@context": "https://schema.org", "@type": "CollectionPage",
          "name": "أعمال محمد حسين", "url": SITE + "portfolio.html",
          "hasPart": [{"@type": "CreativeWork", "name": p["title"], "url": p["url"],
                       "description": p["teaser"]} for p in PROJECTS]}

    body = f'''
<section>
  <div class="wrap section-head reveal">
    <div class="eyebrow">SELECTED WORK</div>
    <h1 style="font-size:clamp(1.85rem,3.9vw,2.55rem)">مشاريع شغالة فعليًا،<br>مش تصاميم على الورق.</h1>
    <p class="lead" style="margin-top:16px">كل مشروع تحت له رابط مباشر تقدر تفتحه وتجربه، وصفحة تفاصيل تشرح المشكلة والحل.</p>
  </div>

  <div class="wrap">
    <div class="filters reveal" role="group" aria-label="تصفية المشاريع">
{fhtml}
    </div>

    <div class="stagger work-grid">
{cards}
    </div>
    <p id="no-results" hidden style="text-align:center;padding:40px 0">مفيش مشاريع في التصنيف ده حاليًا.</p>
  </div>
</section>

{CTA}
'''
    return render("portfolio.html", "portfolio", "أعمالي — محمد حسين",
        "ستة مشاريع منشورة أونلاين: أنظمة كاشير ومخزون، إدارة مالية سحابية، تتبع طلبات متعدد الفروع، مواقع شركات وأدوات عامة.",
        body, jsonld=ld)


def contact():
    body = '''
<section>
  <div class="wrap contact-split">
    <div class="reveal">
      <div class="eyebrow">GET IN TOUCH</div>
      <h1 style="font-size:clamp(1.85rem,3.9vw,2.55rem)">خليني أسمع عن مشروعك.</h1>
      <p class="lead" style="margin-top:16px;max-width:430px">
        املأ النموذج، أو تواصل مباشرة عن طريق أي وسيلة تحتها. بردّ عادةً خلال يوم عمل واحد.
      </p>

      <div style="margin-top:30px">
        <a href="mailto:egyup@outlook.com" class="contact-line"><b>email →</b><span>egyup@outlook.com</span></a>
        <a href="https://wa.me/201000220606" target="_blank" rel="noopener" class="contact-line"><b>whatsapp →</b><span>01000220606</span></a>
        <a href="https://github.com/iegy" target="_blank" rel="noopener" class="contact-line"><b>github →</b><span>github.com/iegy</span></a>
      </div>
      <p style="margin-top:20px;font-size:.86rem;color:var(--muted)">
        ملحوظة: التواصل عن طريق واتساب فقط، من غير مكالمات تليفون مباشرة.
      </p>
    </div>

    <form id="contact-form" class="reveal card" style="clip-path:none;border-radius:var(--radius-lg)" novalidate
          data-access-key="dc9615a9-63f3-4806-91e3-6828f5b85ffe">
      <div class="field">
        <label for="name">الاسم</label>
        <input id="name" name="name" type="text" placeholder="اسمك الكامل" autocomplete="name" required>
        <span class="err">اكتب اسمك من فضلك.</span>
      </div>
      <div class="field">
        <label for="contact">إيميل أو رقم واتساب</label>
        <input id="contact" name="contact" type="text" placeholder="أفضل وسيلة نتواصل بيها" required>
        <span class="err">محتاج وسيلة أقدر أرد عليك بيها.</span>
      </div>
      <div class="field">
        <label for="budget">الميزانية التقريبية (اختياري)</label>
        <select id="budget" name="budget">
          <option value="">مش محدد لسه</option>
          <option>أقل من ٥٬٠٠٠ جنيه</option>
          <option>٥٬٠٠٠ – ١٥٬٠٠٠ جنيه</option>
          <option>١٥٬٠٠٠ – ٤٠٬٠٠٠ جنيه</option>
          <option>أكثر من ٤٠٬٠٠٠ جنيه</option>
        </select>
      </div>
      <div class="field">
        <label for="message">تفاصيل المشروع</label>
        <textarea id="message" name="message" placeholder="احكيلي عن فكرتك، والمدة اللي محتاجها..." required></textarea>
        <span class="err">اكتب سطرين على الأقل عن المشروع.</span>
      </div>

      <button type="submit" class="btn btn-primary" style="width:100%">إرسال بالإيميل</button>
      <button type="button" class="btn btn-outline" data-send="whatsapp" style="width:100%;margin-top:10px">
        أو ابعتها على واتساب
      </button>
      <div class="form-status" role="status" aria-live="polite"></div>
      <p class="form-note">بياناتك بتوصلني أنا بس، ومش بتتسجل في أي مكان تاني.</p>
    </form>
  </div>
</section>
'''
    ld = {"@context": "https://schema.org", "@type": "ContactPage",
          "url": SITE + "contact.html", "mainEntity": PERSON_LD}
    return render("contact.html", "contact", "تواصل معايا — محمد حسين",
        "ابعتلي تفاصيل مشروعك بالإيميل أو على واتساب — بردّ عادةً خلال يوم عمل واحد.",
        body, jsonld=ld)


def case(p, prev, nxt):
    meta = "\n".join(f'      <div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in p["meta"])
    points = "\n".join(f'      <li>{x}</li>' for x in p["points"])
    stack = "".join('<span class="tag">%s</span>' % t for t in p["stack"])
    nav = []
    if prev: nav.append(f'<a class="link-out" href="work-{prev["slug"]}.html">→ {prev["short"]}</a>')
    else: nav.append('<span></span>')
    if nxt: nav.append(f'<a class="link-out" href="work-{nxt["slug"]}.html">{nxt["short"]} ←</a>')
    else: nav.append('<span></span>')

    body = f'''
<div class="case-hero">
  <div class="wrap">
    <a class="link-out" href="portfolio.html" style="margin-bottom:18px">→ كل الأعمال</a>
    <div class="eyebrow">CASE {p['n']}</div>
    <h1 style="font-size:clamp(1.75rem,3.7vw,2.5rem)">{p['title']}</h1>
    <p class="lead" style="margin-top:16px;max-width:660px">{p['excerpt']}</p>
    <div style="margin-top:22px;display:flex;gap:12px;flex-wrap:wrap">
      <a href="{p['url']}" class="btn btn-primary" target="_blank" rel="noopener">زيارة المشروع ↗</a>
      <a href="contact.html" class="btn btn-outline">عايز حاجة شبه دي</a>
    </div>
    <dl class="case-meta">
{meta}
    </dl>
    <div class="case-shot reveal">
      <img src="cover-{p['slug']}.webp" alt="لقطة من واجهة {p['short']}" width="1600" height="1000" decoding="async">
    </div>
  </div>
</div>

<section>
  <div class="wrap prose reveal">
    <h2>التحدي</h2>
    <p>{p['problem']}</p>

    <h2>الحل</h2>
    <p>{p['solution']}</p>
    <ul>
{points}
    </ul>

    <div class="callout"><p><strong>النتيجة:</strong> {p['result']}</p></div>

    <h2>التقنيات</h2>
    <div>{stack}</div>

    <div style="display:flex;justify-content:space-between;gap:16px;margin-top:52px;padding-top:24px;border-top:1px solid var(--line)">
      {nav[0]}
      {nav[1]}
    </div>
  </div>
</section>

{CTA}
'''
    ld = {"@context": "https://schema.org", "@type": "CreativeWork",
          "name": p["title"], "description": p["excerpt"], "url": p["url"],
          "author": {"@type": "Person", "name": "محمد حسين"},
          "image": SITE + f"cover-{p['slug']}.webp",
          "inLanguage": "ar"}
    return render(f"work-{p['slug']}.html", "portfolio", f"{p['title']} — محمد حسين",
                  p["teaser"], body, jsonld=ld, ogtype="article",
                  ogimage=f"cover-{p['slug']}.webp")


def notfound():
    body = '''
<section style="padding-block:clamp(70px,12vw,140px);text-align:center">
  <div class="wrap" style="max-width:560px">
    <div class="eyebrow">ERROR 404</div>
    <h1 style="font-size:clamp(2rem,5vw,3rem)">الصفحة دي مش موجودة.</h1>
    <p class="lead" style="margin-top:16px">يمكن الرابط قديم، أو فيه حرف ناقص. جرّب ترجع للرئيسية أو تشوف الأعمال.</p>
    <div style="display:flex;gap:12px;justify-content:center;margin-top:26px;flex-wrap:wrap">
      <a href="index.html" class="btn btn-primary">الرئيسية</a>
      <a href="portfolio.html" class="btn btn-outline">شوف الأعمال</a>
    </div>
  </div>
</section>
'''
    return render("404.html", "", "الصفحة غير موجودة — محمد حسين",
                  "الصفحة المطلوبة غير موجودة.", body)


def extras(pages):
    # sitemap
    urls = "\n".join(
        f'  <url><loc>{SITE}{s}</loc><changefreq>monthly</changefreq>'
        f'<priority>{"1.0" if s=="index.html" else "0.8" if not s.startswith("work-") else "0.7"}</priority></url>'
        for s in pages if s != "404.html")
    open(os.path.join(HERE, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + '\n</urlset>\n')

    open(os.path.join(HERE, 'robots.txt'), 'w', encoding='utf-8').write(
        "User-agent: *\nAllow: /\n\nSitemap: %ssitemap.xml\n" % SITE)

    manifest = {
        "name": "محمد حسين — مطوّر ومصمم رقمي", "short_name": "M.HUSSEIN",
        "lang": "ar", "dir": "rtl", "start_url": "./", "display": "standalone",
        "background_color": "#FBF7F1", "theme_color": "#FBF7F1",
        "icons": [
            {"src": "favicon-192x192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "apple-touch-icon.png", "sizes": "180x180", "type": "image/png"},
        ],
    }
    open(os.path.join(HERE, 'site.webmanifest'), 'w', encoding='utf-8').write(
        json.dumps(manifest, ensure_ascii=False, indent=2))
    open(os.path.join(HERE, '.nojekyll'), 'w').write('')


if __name__ == "__main__":
    pages = [home(), about(), services(), portfolio(), contact()]
    for i, p in enumerate(PROJECTS):
        pages.append(case(p, PROJECTS[i - 1] if i > 0 else None,
                          PROJECTS[i + 1] if i < len(PROJECTS) - 1 else None))
    pages.append(notfound())
    extras(pages)
    print("✓ اتبنى %d صفحة:" % len(pages))
    for s in pages:
        print("  -", s)
