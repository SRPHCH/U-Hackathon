import base64
import re, json, sys
import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "tools")
orig_tpl = open(os.path.join(TOOLS, "template.original.html"), encoding="utf8").read()
css = open(os.path.join(TOOLS, "style.css"), encoding="utf8").read()
markup = open(os.path.join(TOOLS, "markup.html"), encoding="utf8").read()

# fonts block (first <style> in helmet) kept verbatim
fonts = re.search(r"<style>(/\* cyrillic-ext \*/.*?)</style>", orig_tpl, re.S).group(1)
script = orig_tpl[orig_tpl.index('<script type="text/x-dc"'):orig_tpl.rindex("</script>") + len("</script>")]

def sub(old, new, count=1):
    global script
    assert old in script, old[:60]
    script = script.replace(old, new, count)

# componentDidMount: keep the feed ticker, drop pulse/reveal effects
s = script.index("  componentDidMount() {")
e = script.index("  componentWillUnmount()")
script = script[:s] + "  componentDidMount() {\n    this.timer = setInterval(() => this.setState(s => ({ tick: s.tick + 1 })), 3200);\n  }\n" + script[e:]
sub("componentWillUnmount() { clearInterval(this.timer); this.io && this.io.disconnect(); }",
    "componentWillUnmount() { clearInterval(this.timer); }")

sub("return { label: v.label, pick: () => this.setState({ ind: k }), bg: on ? pink : '#fff', color: on ? 'oklch(0.3 0.06 355)' : ink, border: on ? pink : 'oklch(0.9 0.015 350)', shadow: on ? '0 8px 20px -8px oklch(0.84 0.09 358 / .6)' : 'none' };",
    "return { label: v.label, pick: () => this.setState({ ind: k }), on: on ? 'true' : 'false' };")
sub("c: i === 0 ? pink : i < 3 ? 'oklch(0.88 0.06 358)' : 'oklch(0.86 0.04 350)' }));",
    "top: i === 0 ? 'true' : 'false' }));")
sub("return { code: CODES[k], name: NAMES[k], pct: cur.mix[k], bg: k === top ? 'oklch(0.96 0.03 358)' : '#fff', border: inChain ? pink : 'oklch(0.93 0.012 350)', fg: inChain ? 'oklch(0.52 0.13 358)' : 'oklch(0.55 0.02 330)' };",
    "return { code: CODES[k], name: NAMES[k], pct: cur.mix[k], inChain: inChain ? 'true' : 'false', step: inChain ? String(cur.chain.indexOf(k) + 1) : '' };")
# plans
i0 = script.index("return { ...p, hot: !!p.hot, price: fmt(price)")
i1 = script.index("});\n    const tg")
script = script[:i0] + "return { ...p, hot: !!p.hot, hotS: p.hot ? 'true' : 'false', price: fmt(price), billNote: yearly ? `เรียกเก็บ ฿${fmt(price * 12)} ต่อปี` : 'เรียกเก็บรายเดือน ยกเลิกได้ทุกเมื่อ' };\n    " + script[i1:]
sub("const tg = on => ({ bg: on ? '#fff' : 'transparent', fg: on ? ink : 'oklch(0.5 0.02 330)', sh: on ? '0 2px 8px -2px oklch(0.4 0.05 350 / .2)' : 'none' });\n    const m = tg(!yearly), y = tg(yearly);\n", "")
sub("mBg: m.bg, mFg: m.fg, mSh: m.sh, yBg: y.bg, yFg: y.fg, ySh: y.sh,",
    "mOn: !yearly ? 'true' : 'false', yOn: yearly ? 'true' : 'false',")
sub("return { q, a, toggle: () => this.setState({ open: on ? -1 : i }), rows: on ? '1fr' : '0fr', rot: on ? '45deg' : '0deg', iconBg: on ? pink : 'oklch(0.96 0.02 358)', iconFg: on ? 'oklch(0.3 0.06 355)' : 'oklch(0.52 0.13 358)', border: on ? 'oklch(0.85 0.08 358)' : 'oklch(0.93 0.012 350)' };",
    "return { q, a, toggle: () => this.setState({ open: on ? -1 : i }), rows: on ? '1fr' : '0fr', on: on ? 'true' : 'false' };")
# advisor points: drop A1/A2 labels not used in markup; fine to keep.
# footer links: real targets where a section/page exists, plain "coming soon" text otherwise
_f0 = script.index("      footCols: [")
_f1 = script.index("      ]" + chr(10) + "    };", _f0) + len("      ]" + chr(10))
_L = lambda t, h='': "{ t: %r, href: %r, on: %s, off: %s }" % (t, h, 'true' if h else 'false', 'false' if h else 'true')
script = script[:_f0] + """      footCols: [
        { h: 'ผลิตภัณฑ์', items: [%s, %s, %s, %s] },
        { h: 'แหล่งข้อมูล', items: [%s, %s, %s, %s] },
        { h: 'บริษัท', items: [%s, %s, %s] },
        { h: 'กฎหมาย', items: [%s, %s, %s] }
      ]
""" % (_L('Agent ทั้งหมด', '#agents'), _L('Secretary', '#advisor'), _L('Market & Industry Update', '#oracle'), _L('การเชื่อมต่อ'),
       _L('คู่มือเริ่มต้น'), _L('บทความ'), _L('ศูนย์ช่วยเหลือ', '#faq'), _L('สถานะระบบ'),
       _L('เกี่ยวกับเรา'), _L('ร่วมงานกับเรา'), _L('ติดต่อเรา', 'mailto:XXX@gmail.com'),
       _L('ข้อกำหนดการใช้งาน'), _L('นโยบายความเป็นส่วนตัว'), _L('ความปลอดภัย')) + script[_f1:]

# ---- content pass: plans, faq, terminology ----
_a = script.index("const base = [590, 1490, 3900];"); _b = script.index("const faqData = [")
script = script[:_a] + """const fmt = n => n.toLocaleString('en-US');
    const plans = [
      { name: 'Plan Demo', desc: 'สำหรับทดลองใช้งานก่อนตัดสินใจ', hot: false, hotS: 'true', price: '0', billNote: '',
        features: ['เอเจนท์หลักครบ 6 ตัว', 'Secretary จัดสรรโทเคนอัตโนมัติ', 'Market & Industry Update รายงานแนวโน้มรายสัปดาห์'] }
    ];
    """ + script[_b:]
_a = script.index("const faqData = ["); _b = script.index("];", _a) + 2
script = script[:_a] + """const faqData = [
      ['ทำไมต้องเลือก Antistant แทนการใช้แชตบอตเอไอทั่วไป?', 'แชตบอตทั่วไปตอบเมื่อคุณถาม แต่ Antistant มีเอเจนท์หลายตัวที่รู้จักร้านของคุณ เชื่อมกับข้อมูลยอดขายจริง และทำงานต่อเนื่องเอง เช่น เฝ้าราคาคู่แข่งหรือตรวจคำโฆษณา จากนั้นสรุปมาให้คุณตัดสินใจ คุณไม่ต้องเขียนพรอมต์ใหม่ทุกครั้ง'],
      ['เอเจนท์ทำงานตลอดเวลาโดยไม่ต้องสั่งจริงหรือไม่?', 'จริง แต่ละเอเจนท์มีรอบการทำงานของตัวเอง เช่น Market & Industry Update ตรวจข่าวและราคาทุกชั่วโมง Daily Update ส่งสรุปทุกเช้า คุณยังสั่งงานเพิ่มหรือหยุดเอเจนท์ตัวไหนก็ได้ทุกเมื่อ'],
      ['Market & Industry Update ทำนายแม่นยำแค่ไหน?', 'Market & Industry Update ใช้ข้อมูลย้อนหลังของร้าน ข้อมูลตลาด และข่าวที่เกี่ยวข้องมาสร้างคาดการณ์ ทุกผลลัพธ์แสดงระดับความมั่นใจและแหล่งข้อมูลที่ใช้ ควรใช้เป็นข้อมูลประกอบการตัดสินใจ ไม่ใช่คำรับประกันผล'],
      ['ยกเลิกได้ตลอดเวลาหรือไม่?', 'ได้ ยกเลิกได้จากหน้าตั้งค่า ไม่มีสัญญาผูกมัด']
    ];""" + script[_b:]

import re as _re
def _norm(t):
    for a, b in [("AI Advisor", "Secretary"), ("Oracle Agent", "Market & Industry Update"), ("เอเจนท์", "Agent"), ("เอไอ", "AI"), ("โทเคน", "Token")]:
        t = t.replace(a, b)
    t = _re.sub("([฀-๿])(Agent|AI|Token|Secretary)", lambda m: m.group(1) + " " + m.group(2), t)
    t = _re.sub("(Agent|AI|Token|Secretary)([฀-๿])", lambda m: m.group(1) + " " + m.group(2), t)
    t = t.replace("พ.ร.บ.คุ้มครอง", "พ.ร.บ. คุ้มครอง")
    return t
markup = _norm(markup); script = _norm(script)

head = ('<!DOCTYPE html>\n<html lang="th"><head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<title>Antistant — ทีมเอไอสำหรับธุรกิจ E‑Commerce</title>\n'
        '<script src="40a0a0f5-3946-470e-ba31-6bffefe3a835"></script>\n</head>\n<body>\n<x-dc>\n<helmet>\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Anuphan:wght@400;500;600;700&display=swap">\n<style>' + fonts + '</style>\n<style>\n' + css + '\n</style>\n</helmet>\n')
tpl = head + markup + "\n</x-dc>\n" + script + "\n</body></html>"

# ---- embed the workspace (solora-app.html) so both pages live in one file ----
import re as _r2
_app = open(os.path.join(ROOT, "solora-app.html"), encoding="utf8").read()
_css = _r2.search(r"<style>(.*?)</style>", _app, _r2.S).group(1)
_body = _r2.search(r'(<div class="app" id="app".*</iframe>)', _app, _r2.S).group(1)
_js = _r2.search(r"<script>\n(\(\(\) => \{.*?)</script>", _app, _r2.S).group(1)

def _prefix_block(css):
    out = []; i = 0; n = len(css)
    while i < n:
        j = css.find("{", i)
        if j < 0: out.append(css[i:]); break
        head = css[i:j].strip()
        # find matching close brace
        depth = 1; k = j + 1
        while k < n and depth:
            if css[k] == "{": depth += 1
            elif css[k] == "}": depth -= 1
            k += 1
        inner = css[j+1:k-1]
        if head.startswith("@media") or head.startswith("@supports"):
            out.append(head + "{" + _prefix_block(inner) + "}")
        elif head.startswith("@"):
            out.append(head + "{" + inner + "}")
        else:
            sels = []
            for s_ in head.split(","):
                s_ = s_.strip()
                if s_ in ("html", "body", "html,body"): continue
                if s_ == ":root": s_ = "#ws"
                else: s_ = "#ws " + s_
                sels.append(s_)
            if sels: out.append(",".join(sels) + "{" + inner + "}")
        i = k
    return "\n".join(out)

_css = _r2.sub(r"/\*.*?\*/", "", _css, flags=_r2.S)
_css = _css.replace("body{margin:0;", "#ws-root{margin:0;")  # body rule -> root wrapper
_css = _r2.sub(r"#ws-root\{", "#ws{", _css) if False else _css
_scoped = _prefix_block(_css)
_scoped = _scoped.replace("#ws #ws-root{", "#ws{")
_scoped += """
#ws{position:fixed;inset:0;z-index:300;display:none;background:var(--bg);color:var(--text)}
html.ws-on #ws{display:block}
html.ws-on x-dc{display:none!important}
html.ws-on{overflow:hidden}
"""
_body = _body.replace('href="solora-landing.html"', 'href="#top"')
_body = _body.replace('<iframe id="avsvc" src="ant-mascot.html?snap=1"', '<iframe id="avsvc" data-src="ant-mascot.html?snap=1"')
_router = """<script>
(function(){var r=function(){var on=location.hash==='#app';document.documentElement.classList.toggle('ws-on',on);if(on)window.scrollTo(0,0)};addEventListener('hashchange',r);r();})();
(function(){
  var B = window.__boot; if(!B) return;
  var t0 = Date.now(), hero = false, ready = false;
  var WS = function(){ return window.SoloraWS || {progress:function(){return {done:0,total:1}}, start:function(){}}; };
  var inApp = function(){ return location.hash === '#app'; };
  function startPreload(){ if(hero) return; hero = true; B.set(70); setTimeout(function(){ WS().start(); }, 7000); }
  addEventListener('message', function(e){
    if(!e.data || e.data.type !== 'ant:shown') return;
    var f = document.querySelector('.hero-ant iframe');
    if(f && e.source === f.contentWindow) startPreload();
  });
  B.set(45, 'Loading Antistant...');
  function tick(){
    var age = Date.now() - t0;
    if(!hero && age > 25000) startPreload();
    var p = WS().progress(), frac = p.total ? p.done/p.total : 0;
    if(hero){ B.set(70 + 30*frac); if(p.total && p.done >= p.total) ready = true; }
    if(inApp() && age > 70000) ready = true;
    if(inApp()){
      if(hero && ready) B.hide(); else B.show('Preparing for your team...');
    } else if(hero){
      B.hide();
    }
  }
  setInterval(tick, 250); tick();
})();
</script>"""
_embed = "\n<style id=\"ws-css\">\n" + _scoped + "\n</style>\n<div id=\"ws\">" + _body + "</div>\n<script>\n" + _js + "\n</script>\n" + _router + "\n"
tpl = tpl.replace("\n</body></html>", _embed + "</body></html>")
tpl = tpl.replace('href="solora-app.html"', 'href="#app"')
# brand rename: visible name Solora -> Antistant (identifiers like SoloraWS and storage keys stay)
tpl = re.sub(r'Solora(?!WS)', 'Antistant', tpl).replace('solora.ai', 'antistant.ai')

import html as _h
_ant = open(os.path.join(ROOT, "ant-mascot.html"), encoding="utf8").read()
_ifr = 'src="ant-mascot.html?v=5"'
assert _ifr in tpl
pass  # keep src= (srcdoc variant broke the module script)

src = open(os.path.join(ROOT, "source", "solora-landing.orig.html"), encoding="utf8").read()
m = re.search(r'(<script type="__bundler/template">\s*)(.*?)(\s*</script>)', src, re.S)
js = json.dumps(tpl, ensure_ascii=False).replace("</", "<\\/")

_gif = base64.b64encode(open(os.path.join(TOOLS, "boot-ant.png"), "rb").read()).decode()
_loader = """<div id="__bundler_thumbnail" role="status" aria-live="polite">
    <style>
      #__bundler_thumbnail{position:fixed;inset:0;z-index:99999;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:20px;background:#fff;transition:opacity .5s ease,visibility .5s}
      #__bundler_thumbnail.done{opacity:0;visibility:hidden;pointer-events:none}
      #__bundler_thumbnail .bt-ant{position:relative;height:200px;display:flex;align-items:flex-end;justify-content:center}
      #__bundler_thumbnail .bt-ant img{height:150px;width:auto;display:block;position:relative;z-index:1;transform-origin:50% 100%;will-change:transform;animation:bt-hop 1.1s cubic-bezier(.3,0,.3,1) infinite}
      #__bundler_thumbnail .bt-ant b{position:absolute;bottom:-6px;left:50%;width:96px;height:14px;margin-left:-48px;border-radius:50%;background:rgba(60,30,30,.22);filter:blur(3px);will-change:transform,opacity;animation:bt-sh 1.1s cubic-bezier(.3,0,.3,1) infinite}
      @keyframes bt-hop{0%,100%{transform:translateY(0) scale(1.08,.9)}12%{transform:translateY(0) scale(.96,1.05)}50%{transform:translateY(-34px) scale(1,1)}88%{transform:translateY(0) scale(.97,1.04)}}
      @keyframes bt-sh{0%,100%{transform:scale(1.05);opacity:.9}50%{transform:scale(.7);opacity:.45}}
      #__bundler_thumbnail .bt-bar{width:min(260px,64vw);height:6px;border-radius:99px;background:#fbe3ec;overflow:hidden}
      #__bundler_thumbnail .bt-bar i{display:block;height:100%;width:8%;border-radius:99px;background:#f06c9b;transition:width .45s ease}
      #__bundler_thumbnail .bt-txt{font:500 14px/1.4 'Anuphan','IBM Plex Sans Thai','Noto Sans Thai',system-ui,sans-serif;color:#6a5560}
    </style>
    <div class="bt-ant"><b></b><img alt="" src="data:image/png;base64,""" + _gif + """"></div>
    <div class="bt-bar"><i></i></div>
    <div class="bt-txt">Loading Antistant...</div>
  </div>
  <script>
    window.__boot = {pct: 0,
      el: function(){ return document.getElementById('__bundler_thumbnail'); },
      set: function(p, txt){ var e = this.el(); if(!e) return; this.pct = Math.max(this.pct, p); e.querySelector('.bt-bar i').style.width = Math.min(100, this.pct) + '%'; if(txt) e.querySelector('.bt-txt').textContent = txt; },
      show: function(txt){ var e = this.el(); if(!e) return; e.classList.remove('done'); if(txt) e.querySelector('.bt-txt').textContent = txt; },
      hide: function(){ var e = this.el(); if(e) e.classList.add('done'); }
    };
    window.__boot.set(8);
  </script>"""
_shell_pat = re.compile(r'<div id="__bundler_thumbnail">.*?</div>\s*<div id="__bundler_loading">.*?</div>', re.S)
assert _shell_pat.search(src)
src2 = _shell_pat.sub(lambda m_: _loader, src, count=1)
_swap = "document.documentElement.replaceWith(doc.documentElement);"
assert _swap in src2
src2 = src2.replace(_swap, "var __keep = document.getElementById('__bundler_thumbnail');\n    " + _swap + "\n    if (__keep) document.body.appendChild(__keep);\n    if (window.__boot) window.__boot.set(40);", 1)
src2 = src2.replace("setStatus('Rendering...');", "setStatus('Rendering...'); if (window.__boot) window.__boot.set(25);", 1)
m = re.search(r'(<script type="__bundler/template">\s*)(.*?)(\s*</script>)', src2, re.S)
out = src2[:m.start(2)] + js + src2[m.end(2):]
open(os.path.join(ROOT, "solora-landing.html"), "w", encoding="utf8").write(out)
print("ok", len(out))
