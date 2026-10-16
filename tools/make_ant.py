import os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import re
src = open(os.path.join(ROOT, "source", "ant-studio.html"), encoding="utf8").read()
s = src

def rep(old, new, count=1):
    global s
    assert old in s, old[:70]
    s = s.replace(old, new, count)

# ---- head injection: transparent chrome-free mascot view ----
head = '''<style>
html,body{background:transparent!important;overflow:hidden}
.viewer .stage{background:transparent!important;box-shadow:none!important;--heat:0;--mx:0;--ab:0;--hs:0;--hr:0rad}
.viewer .stage-tools,.viewer .stage-foot,.viewer .stage-tag,.viewer .hint,.viewer .toast,.viewer .busy{display:none!important}
.viewer .stage canvas.gl{cursor:default;touch-action:manipulation;filter:saturate(calc(1 + var(--heat)*.55)) brightness(calc(1 - var(--heat)*.05)) hue-rotate(calc(var(--heat)*-6deg))}
.viewer .stage.over canvas.gl{cursor:pointer}
.fx{position:absolute;inset:0;pointer-events:none;z-index:2;overflow:hidden}
.fx .glow{position:absolute;left:50%;bottom:6%;width:78%;aspect-ratio:1;transform:translateX(-50%);border-radius:50%;background:radial-gradient(circle,oklch(0.7 0.22 28 / .55) 0,oklch(0.7 0.2 28 / 0) 68%);opacity:calc(var(--heat)*.8)}
.fx .steam{position:absolute;left:50%;top:22%;width:0;height:0;opacity:var(--heat)}
.fx .steam i{position:absolute;width:9vmin;height:9vmin;border-radius:50%;background:radial-gradient(circle at 40% 40%,#fff,oklch(0.93 0.01 20) 70%);filter:blur(1.5px);opacity:0;animation:puff 1.1s ease-out infinite;box-shadow:0 2px 8px oklch(0.5 0.1 20 / .18)}
.fx .steam i:nth-child(1){left:-18vmin;top:6vmin;animation-delay:0s}
.fx .steam i:nth-child(2){left:13vmin;top:6vmin;animation-delay:.28s}
.fx .steam i:nth-child(3){left:-12vmin;top:2vmin;animation-delay:.55s;width:7vmin;height:7vmin}
.fx .steam i:nth-child(4){left:9vmin;top:2vmin;animation-delay:.82s;width:7vmin;height:7vmin}
@keyframes puff{0%{opacity:0;transform:translateY(3vmin) scale(.5)}25%{opacity:.95}100%{opacity:0;transform:translateY(-16vmin) scale(1.5)}}
.fx .vein{position:absolute;left:61%;top:14%;width:15%;max-width:74px;opacity:var(--heat);transform:scale(calc(.6 + var(--heat)*.4));transform-origin:center;animation:throb .32s ease-in-out infinite alternate}
@keyframes throb{to{transform:scale(1.12) rotate(6deg)}}
.fx .money{position:absolute;left:87%;bottom:-6vmin;width:22vmin;display:flex;flex-direction:column;align-items:center;transform:translateX(-50%) translateY(calc((1 - var(--mx))*90vmin + var(--ab)*-9vmin)) scale(calc(1 - var(--ab)*.55));transform-origin:50% 6%;opacity:calc(var(--mx)*(1 - var(--ab)))}
.fx .money .bill{width:100%;filter:drop-shadow(0 6px 10px oklch(0.4 0.08 160 / .3));transform:rotate(-7deg);position:relative;z-index:1}
.fx .money .hand{width:46%;margin-top:-5vmin;position:relative;z-index:2}
.fx .money .arm{width:42%;height:42vmin;margin-top:-3vmin;border-radius:10px 10px 0 0;background:linear-gradient(180deg,#fff 0 9vmin,oklch(0.26 0.03 350) 9vmin)}
.av-mode .fx{display:none!important}
.fx .wave{position:absolute;left:13%;top:34%;font-size:15vmin;line-height:1;transform-origin:78% 88%;transform:scale(var(--hs)) rotate(var(--hr));opacity:min(1,calc(var(--hs)*3));font-family:'Segoe UI Emoji','Apple Color Emoji','Noto Color Emoji',sans-serif}
@media (prefers-reduced-motion:reduce){.fx .steam i,.fx .vein{animation:none}.fx .steam i{opacity:.8}}
</style>
<script>if(new URLSearchParams(location.search).get("av")==="1")document.documentElement.classList.add("av-mode");</script>
<script>(function(){var q=new URLSearchParams(location.search);window.DOT_VIEW={shape:"ant",color:q.get("color")||"#E2513F",material:"plush",style:q.get("style")||"gentleman",gender:"male",yaw:0.28,motion:true};})();</script>
<script type="module">'''
rep('<script type="module">', head)

# ---- background: transparent ----
rep("sc.background = gradientTexture();", "sc.background = null; r.setClearColor(0x000000, 0);")
# ---- frame with headroom for hops ----
rep("const FRAME = VIEW ? 1.4 : 1.5;", "const AVM = new URLSearchParams(location.search).get('av') === '1';\nconst FRAME = AVM ? 1.34 : 1.85;")
rep("const MAIN_RES = 132, THUMB_RES = 70,", "const MAIN_RES = new URLSearchParams(location.search).get('av') === '1' ? 64 : 132, THUMB_RES = 70,")
# ---- tiny idle sway (director owns the choreography) ----
rep("const sway = Math.sin(T0*.45)*.3*live;", "const sway = Math.sin(T0*.45)*.05*live;")

# ---- interaction: no dragging; click/tap on the ant teases it ----
a = s.index("  cv.addEventListener('pointerdown'")
b = s.index("  cv.addEventListener('dblclick', () => resetView());") + len("  cv.addEventListener('dblclick', () => resetView());")
s = s[:a] + '''  const ray = new THREE.Raycaster(), ndc = new THREE.Vector2();
  const hit = e => { const r = cv.getBoundingClientRect(); ndc.set(((e.clientX-r.left)/r.width)*2-1, -((e.clientY-r.top)/r.height)*2+1);
    ray.setFromCamera(ndc, main.camera); return ray.intersectObject(main.puppet, true).length > 0; };
  cv.addEventListener('pointermove', e => { stage.classList.toggle('over', hit(e)); });
  cv.addEventListener('pointerleave', () => stage.classList.remove('over'));
  cv.addEventListener('click', e => { if(!AVM && hit(e)) DIR.poke(); });
  cv.addEventListener('keydown', e => { if(e.key === 'Enter' || e.key === ' ') DIR.poke(); });''' + s[b:]

# ---- director ----
director = r'''
/* ---------- Solora mascot director: intro, self-playing idle, tease sequence ---------- */
const DIR = main ? (() => {
  const R = .38;
  const fx = document.createElement('div'); fx.className = 'fx'; fx.setAttribute('aria-hidden', 'true');
  fx.innerHTML = '<div class="wave">\ud83d\udc4b</div><div class="glow"></div><div class="steam"><i></i><i></i><i></i><i></i></div>'
    + '<svg class="vein" viewBox="0 0 40 40" fill="none" stroke="oklch(0.55 0.24 25)" stroke-width="4.5" stroke-linecap="round"><path d="M6 14c6 0 8-2 8-8"/><path d="M34 14c-6 0-8-2-8-8"/><path d="M6 26c6 0 8 2 8 8"/><path d="M34 26c-6 0-8 2-8 8"/></svg>'
    + '<div class="money"><svg class="bill" viewBox="0 0 120 64"><rect x="2" y="2" width="116" height="60" rx="8" fill="oklch(0.9 0.08 150)" stroke="oklch(0.55 0.1 150)" stroke-width="3"/><rect x="10" y="10" width="100" height="44" rx="5" fill="none" stroke="oklch(0.6 0.1 150)" stroke-width="1.5" stroke-dasharray="3 4"/><circle cx="60" cy="32" r="17" fill="oklch(0.97 0.03 150)" stroke="oklch(0.55 0.1 150)" stroke-width="2"/><text x="60" y="40" text-anchor="middle" font-size="22" font-weight="700" fill="oklch(0.4 0.1 150)" font-family="sans-serif">\u0e3f</text></svg><svg class="hand" viewBox="0 0 80 70"><rect x="14" y="16" width="52" height="60" rx="22" fill="oklch(0.86 0.06 55)"/><ellipse cx="29" cy="14" rx="11" ry="10" fill="oklch(0.89 0.06 55)"/><ellipse cx="53" cy="12" rx="10" ry="10" fill="oklch(0.89 0.06 55)"/></svg><div class="arm"></div></div>';
  stage.appendChild(fx);
  main.root.rotation.order = 'ZYX';


  /* ---- avatar mode: small live profile that looks at the composer and works with a role prop ---- */
  const Q = new URLSearchParams(location.search), AV_LOOK = Q.get('look') === 'diag' ? 'diag' : 'down';
  let AV_ROLE = Q.get('role') || 'secretary';
  const AVPOSE = {
    secretary:t => ({y:0, rz:.17 + .03*Math.sin(t*1.7), yaw:.1*Math.sin(t*1.1), rx:.05 + .05*Math.sin(t*2.6), sq:0}),
    finance:t => ({y:0, rz:.02*Math.sin(t*2), yaw:.05*Math.sin(t*1.3), rx:.34 + .05*Math.sin(t*4.5), sq:0}),
    marketing:t => ({y:0, rz:.08*Math.sin(t*3.6), yaw:.25*Math.sin(t*1.9), rx:.04, sq:0}),
    legal:t => ({y:0, rz:0, yaw:-.12, rx:.1 + .1*Math.pow(Math.max(0, Math.sin(t*3)), 2), sq:0}),
    market:t => ({y:0, rz:.05*Math.sin(t*1.6), yaw:.5*Math.sin(t*1.6), rx:.08, sq:0}),
    daily:t => ({y:0, rz:.05*Math.sin(t*1.3), yaw:.05, rx:.06 + .18*(.5 + .5*Math.sin(t*1.3)), sq:0}),
    ops:t => ({y:.01*Math.abs(Math.sin(t*3)), rz:.03*Math.sin(t*3), yaw:0, rx:.24, sq:0}),
    support:t => ({y:0, rz:.1*Math.sin(t*2), yaw:.16*Math.sin(t*1.2), rx:.06, sq:0}),
    analyst:t => ({y:0, rz:0, yaw:.28*Math.sin(t*1.1) + .2, rx:.25, sq:0})
  };
  function buildProp(role){
    const g = new THREE.Group(); g.visible = false; g.position.y = -.152; main.root.add(g);
    const M = (c, o = {}) => new THREE.MeshStandardMaterial(Object.assign({color:c, roughness:.5, metalness:.05}, o));
    const add = (geo, mat, x = 0, y = 0, z = 0, parent = g) => { const m = new THREE.Mesh(geo, mat); m.position.set(x, y, z); parent.add(m); return m; };
    let upd = () => {};
    if(role === 'secretary'){
      const k = M(0x101014, {roughness:.22, metalness:.35});
      const bar = add(new THREE.CapsuleGeometry(.034, .2, 6, 12), k, -.42, .5, .06);
      const ear = add(new THREE.SphereGeometry(.072, 16, 12), k, -.38, .68, .06);
      add(new THREE.SphereGeometry(.066, 16, 12), k, -.37, .33, .1);
      for(let i = 0; i < 4; i++){ const c = add(new THREE.TorusGeometry(.045, .011, 6, 16), k, -.44 - i*.03, .24 - i*.055, .1); c.rotation.x = Math.PI/2; }
      upd = t => { bar.scale.y = 1 + .035*Math.sin(t*10); ear.position.y = .68 + .006*Math.sin(t*10); };
    } else if(role === 'finance'){
      const bills = [0, 1, 2].map(i => { const b = add(new THREE.BoxGeometry(.25, .012, .13), M([0x58b368, 0x6cc47a, 0x4ea35e][i]), (i - 1)*.03, .2, .44); b.rotation.y = (i - 1)*.18; return b; });
      upd = t => bills.forEach((b, i) => { const p = ((t*2.6 + i*2.1) % (Math.PI*2))/(Math.PI*2); b.position.y = .2 + .13*Math.sin(p*Math.PI); b.rotation.x = -.9*Math.sin(p*Math.PI); });
    } else if(role === 'marketing'){
      const mg = new THREE.Group(); mg.position.set(.42, .46, .16); mg.rotation.z = -1.15; g.add(mg);
      add(new THREE.CylinderGeometry(.095, .035, .2, 20), M(0xff7aa8), 0, .1, 0, mg);
      add(new THREE.CylinderGeometry(.04, .04, .09, 14), M(0x2a2a33), 0, -.04, 0, mg);
      upd = t => { mg.scale.setScalar(1 + .07*Math.sin(t*8)); };
    } else if(role === 'legal'){
      const gv = new THREE.Group(); gv.position.set(.42, .22, .18); g.add(gv);
      add(new THREE.CylinderGeometry(.02, .02, .26, 10), M(0xc9a36b), 0, .13, 0, gv);
      const head = add(new THREE.CylinderGeometry(.055, .055, .16, 16), M(0x7a4a26), 0, .27, 0, gv); head.rotation.z = Math.PI/2;
      upd = t => { gv.rotation.z = -.2 - .75*Math.pow(Math.max(0, Math.sin(t*3)), 2); };
    } else if(role === 'market'){
      const mg = new THREE.Group(); mg.position.set(.38, .46, .22); g.add(mg);
      add(new THREE.TorusGeometry(.09, .017, 10, 28), M(0xdedee6, {metalness:.6, roughness:.25}), 0, 0, 0, mg);
      add(new THREE.CircleGeometry(.085, 24), M(0xbfe6ff, {transparent:true, opacity:.4}), 0, 0, 0, mg);
      const h = add(new THREE.CylinderGeometry(.014, .014, .15, 8), M(0x3a3a46), .075, -.1, 0, mg); h.rotation.z = .6;
      upd = t => { mg.position.x = .34 + .1*Math.sin(t*1.6); mg.rotation.z = .18*Math.sin(t*1.6); };
    } else if(role === 'daily'){
      const mg = new THREE.Group(); mg.position.set(.42, .26, .2); g.add(mg);
      add(new THREE.CylinderGeometry(.058, .05, .095, 18), M(0xf6f2ee), 0, 0, 0, mg);
      add(new THREE.CircleGeometry(.05, 18), M(0x3b2417), 0, .048, 0, mg).rotation.x = -Math.PI/2;
      add(new THREE.TorusGeometry(.034, .011, 8, 14), M(0xf6f2ee), .075, 0, 0, mg);
      upd = t => { const s = .5 + .5*Math.sin(t*1.3); mg.position.y = .26 + .16*s; mg.position.x = .42 - .1*s; mg.rotation.z = .35*s; };
    } else if(role === 'ops'){
      const bx = add(new THREE.BoxGeometry(.3, .22, .22), M(0xc99a5b), 0, .2, .44);
      add(new THREE.BoxGeometry(.07, .225, .225), M(0xe6c78f), 0, 0, 0, bx);
      upd = t => { bx.position.y = .2 + .018*Math.sin(t*4); bx.rotation.z = .03*Math.sin(t*3); };
    } else if(role === 'support'){
      const k = M(0x2c2c3a, {roughness:.4});
      const band = add(new THREE.TorusGeometry(.36, .02, 8, 36, Math.PI), k, 0, .5, 0);
      for(const sx of [-1, 1]){ const c = add(new THREE.CylinderGeometry(.08, .08, .055, 18), M(0xff6fae), sx*.37, .5, 0); c.rotation.z = Math.PI/2; }
      const boom = add(new THREE.CylinderGeometry(.01, .01, .3, 8), k, -.28, .38, .17); boom.rotation.z = .5; boom.rotation.x = .9;
      add(new THREE.SphereGeometry(.03, 10, 8), k, -.19, .27, .3);
      upd = t => { band.rotation.z = .02*Math.sin(t*2); };
    } else {
      const cols = [0xb6d80b, 0xffffff, 0x00b1ff];
      const bars = cols.map((c, i) => { const geo = new THREE.BoxGeometry(.07, .1, .07); geo.translate(0, .05, 0); return add(geo, M(c), .34 + i*.095, .12, .24); });
      upd = t => bars.forEach((b, i) => { b.scale.y = .8 + 1.4*(.5 + .5*Math.sin(t*2 + i*1.4)); });
    }
    return {g, update(t, k){ g.visible = k > .12; if(g.visible){ g.scale.setScalar((.55 + .45*Math.min(1, k))*1.38); upd(t, k); } }};
  }
  let PROP = AVM ? buildProp(AV_ROLE) : null;

  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const sm = (a, b, x) => { const t = clamp((x - a)/(b - a)); return t*t*(3 - 2*t); };
  const TAU = Math.PI*2;
  // idle extras layered on top of the constant rocking
  const G = {
    hop:{dur:2.2, f:t => { const on = t > .2 && t < 2.0, h = on ? Math.abs(Math.sin(Math.PI*(t - .2)/.9)) : 0;
      return {y:.15*h, rz:0, yaw:0, sq:t < .2 ? .1*sm(0, .2, t) : on ? .1*(1 - sm(0, .4, h)) : 0}; }},
    twirl:{dur:1.3, f:t => { const u = clamp((t - .2)/.9), h = Math.sin(Math.PI*u);
      return {y:.24*h, rz:0, yaw:TAU*sm(0, 1, u), sq:t < .2 ? .12*sm(0, .2, t) : 0}; }}
  };
  const order = ['hop', 'hop', 'twirl', 'hop'];
  const CHAT = new URLSearchParams(location.search).get('chat') === '1';
  let ext = 'idle', extRole = 'secretary', look = 0, joy = 0;
  const hopS = (t, f) => Math.abs(Math.sin(t*f));
  // cheerful "thinking" dance, one per profession
  const JOY = {
    secretary:t => ({y:.07*hopS(t, 6), rz:.05*Math.sin(t*3), yaw:.25*Math.sin(t*2), rx:.22*Math.sin(t*6), sq:.05*(1 - hopS(t, 6))}),
    finance:t => ({y:.11*hopS(t, 9), rz:0, yaw:.1*Math.sin(t*3), rx:.16*Math.sin(t*9), sq:.07*(1 - hopS(t, 9))}),
    marketing:t => ({y:.12*hopS(t, 4), rz:.08*Math.sin(t*4), yaw:t*5.5, rx:0, sq:.05*(1 - hopS(t, 4))}),
    legal:t => ({y:.05*hopS(t, 2.2), rz:.18*Math.sin(t*2.2), yaw:.12*Math.sin(t*1.1), rx:.14 + .1*Math.sin(t*2.2), sq:0}),
    market:t => ({y:.03*hopS(t, 5), rz:.08*Math.sin(t*5.2), yaw:.8*Math.sin(t*2.6), rx:.05, sq:0}),
    daily:t => ({y:.18*hopS(t, 5), rz:.12*Math.sin(t*5), yaw:.2*Math.sin(t*2.5), rx:0, sq:.08*(1 - hopS(t, 5))}),
    ops:t => ({y:.08*hopS(t, 8), rz:.22*Math.sin(t*8), yaw:.28*Math.sin(t*4), rx:.1, sq:.04*(1 - hopS(t, 8))}),
    support:t => ({y:.1*hopS(t, 3), rz:.2*Math.sin(t*3), yaw:.22*Math.sin(t*1.5), rx:.05, sq:.05*(1 - hopS(t, 3))}),
    analyst:t => ({y:.07*hopS(t, 7), rz:.05*Math.sin(t*3.5), yaw:.28*Math.sin(t*1.7), rx:.2*Math.sin(t*3.5), sq:.08*Math.sin(t*7)})
  };
  let mode = 'idle', gest = 'hop', gt = 0, wait = .3, idx = 0, tt = 0, amp = 0;
  const STEPS = [['ow', .28], ['fall', .85], ['lie', 1.2], ['rise', 1.0], ['rage', 3.8], ['offer', 1.0], ['visit', .9], ['inspect', .9], ['take', .6], ['back', 1.1]];
  const INTRO = [['hops', 1.6], ['settle', .3], ['wave', 2.2]];
  let si = 0, st = 0;

  const out = {y:0, rz:0, rx:0, z:0, x:0, yaw:0, sq:0, eye:1, heat:0, mx:0, ab:0, hs:0, hr:0};
  function reset(){ Object.assign(out, {y:0, rz:0, rx:0, z:0, x:0, yaw:0, sq:0, eye:1, heat:0, mx:0, ab:0, hs:0, hr:0}); }
  function prank(name, u, t){
    const o = out;
    switch(name){
      case 'ow': { const k = Math.sin(Math.PI*u); o.sq = .22*k; o.rx = -.18*k; o.z = -.04*k; o.eye = 1 - .7*k; break; }
      case 'fall': { const e = 1 - Math.pow(1 - u, 2); o.rx = -1.55*e; o.z = -.28*e; o.y = .34*Math.sin(Math.PI*u*.9) + R*(1 - Math.cos(o.rx)); o.eye = .3; break; }
      case 'lie': { const b = Math.exp(-4.5*u); o.rx = -1.55 + .13*b*Math.abs(Math.sin(10*u)); o.z = -.28; o.y = R*(1 - Math.cos(o.rx)) + .13*b*Math.abs(Math.sin(9*u + .4)); o.eye = .15; o.yaw = Math.sin(u*20)*.05; o.heat = .25*sm(.4, 1, u); break; }
      case 'rise': { o.heat = .25 + .35*sm(.2, 1, u);
        if(u < .28){ const k = sm(0, .28, u); o.rx = -1.55 - .1*k; o.z = -.28; o.y = R*(1 - Math.cos(o.rx)); o.sq = .12*k; o.eye = .3 + .3*k; }
        else if(u < .86){ const v = (u - .28)/.58, e = 1 - Math.pow(1 - v, 2.2); o.rx = -1.65*(1 - e); o.z = -.28*(1 - e); o.y = R*(1 - Math.cos(o.rx)) + .5*Math.sin(Math.PI*v); o.yaw = Math.sin(Math.PI*v)*.4; o.eye = .7; }
        else { const v = (u - .86)/.14; o.sq = .18*Math.sin(Math.PI*v); o.eye = .6; }
        break; }
      case 'rage': { const hu = sm(0, .12, u), ph = (t % .5)/.5, h = Math.abs(Math.sin(Math.PI*ph));
        o.heat = 1; o.y = .13*h*hu; o.sq = (.09*(1 - sm(0, .3, h)) + .03)*hu; o.rz = Math.sin(t*31)*.05*hu; o.yaw = Math.sin(t*37)*.09*hu;
        o.eye = .45; o.pulse = 1 + .05*hu*(.5 + .5*Math.sin(t*14)); break; }
      case 'offer': { const e = sm(0, .8, u); o.heat = 1 - .1*e; o.mx = e; o.yaw = .5*e; o.eye = .5 + .3*e; o.y = .03*Math.abs(Math.sin(Math.PI*u*3))*(1 - e); o.rz = Math.sin(t*20)*.03*(1 - e); break; }
      case 'visit': { const e = sm(0, 1, u); o.mx = 1; o.heat = .9 - .35*u; o.x = .22*e; o.y = .26*Math.sin(Math.PI*u); o.yaw = .5; o.rz = -.08*Math.sin(Math.PI*u);
        o.sq = u > .85 ? .14*Math.sin(Math.PI*(u - .85)/.15) : 0; o.eye = .7; break; }
      case 'inspect': { o.mx = 1; o.x = .22; o.heat = .55*(1 - sm(0, .9, u)); o.yaw = .55 + .12*Math.sin(u*9); o.rx = .14*Math.sin(Math.PI*Math.min(1, u*1.3)); o.y = .02*Math.abs(Math.sin(u*14)); o.eye = .9; break; }
      case 'take': { o.mx = 1; o.ab = sm(0, .7, u); o.x = .22; o.yaw = .4*(1 - u); o.sq = .1*Math.sin(Math.PI*u); o.rx = .1*(1 - u); o.eye = .5; break; }
      case 'back': { const e = sm(0, 1, u), h = Math.abs(Math.sin(Math.PI*u*2)); o.mx = 1; o.ab = 1; o.x = .22*(1 - e); o.y = .2*h; o.yaw = .3*(1 - e);
        o.sq = .09*(1 - sm(0, .3, h)); o.eye = .5 + .5*sm(.6, 1, u); break; }
    }
  }
  // page-load greeting: facing right, hops round to face the viewer, leans and waves a hand emoji
  function intro(name, u, t){
    const o = out;
    if(name === 'hops'){ const e = sm(0, 1, u), h = Math.abs(Math.sin(Math.PI*u*2)); o.x = .26*(1 - e); o.yaw = .95*(1 - sm(.1, 1, u)); o.y = .17*h; o.sq = .1*(1 - sm(0, .3, h)); }
    else if(name === 'settle'){ o.sq = .08*Math.sin(Math.PI*u); }
    else { const e = sm(0, .15, u)*(1 - sm(.85, 1, u)), s = sm(.05, .2, u)*(1 - sm(.82, .95, u));
      o.rz = .3*e; o.y = .012*Math.abs(Math.sin(t*9))*e; o.hs = s; o.hr = Math.sin(t*13)*.45*(s > .5 ? 1 : 0); }
  }
  const api = {
    busy: true,
    poke(){ if(mode === 'prank') return; mode = 'prank'; si = 0; st = 0; reset(); },
    intro(){ mode = 'intro'; si = 0; st = 0; reset(); },
    setState(s, role){ ext = s === 'typing' || s === 'think' ? s : 'idle'; if(role && JOY[role]) extRole = role; },
    update(dt, s){
      const o = out;
      if(api.freeze){ reset(); o.pulse = 1; const fz = api.freeze; if(G[fz[0]]){ const r = G[fz[0]].f(fz[1]); o.y = r.y; o.rz = r.rz; o.yaw = r.yaw; o.sq = r.sq; } else if(INTRO.some(x => x[0] === fz[0])) intro(fz[0], fz[1], fz[1]*(fz[2]||1)); else prank(fz[0], fz[1], fz[1]*(fz[2]||1)); }
      else if(mode === 'intro'){
        st += dt; const [name, dur] = INTRO[si]; o.pulse = 1; intro(name, clamp(st/dur), st);
        if(st >= dur){ st = 0; si++; if(si >= INTRO.length){ mode = 'idle'; wait = .5; gt = 0; amp = 0; reset(); } }
      } else if(mode === 'prank'){
        st += dt; const [name, dur] = STEPS[si]; const u = clamp(st/dur);
        o.pulse = 1; prank(name, u, st);
        if(st >= dur){ st = 0; si++; if(si >= STEPS.length){ mode = 'idle'; wait = 1.4; gt = 0; gest = 'hop'; idx = 0; amp = 0; reset(); } }
      } else {
        amp = Math.min(1, amp + dt*1.6); tt += dt;
        const wv = .55 + .45*Math.sin(tt*.8); o.rz = (.15 + .14*Math.sin(tt*4.4))*wv*amp; o.yaw = Math.sin(tt*1.25)*.38*amp; o.y = .014*(1 + Math.sin(tt*4.4))*amp; o.eye = 1; o.heat = 0; o.mx = 0; o.ab = 0; o.x = 0; o.hs = 0; o.hr = 0; o.pulse = 1; o.sq = 0; o.rx = 0;
        look += ((ext === 'typing' ? 1 : 0) - look)*Math.min(1, dt*6); joy += ((ext === 'think' ? 1 : 0) - joy)*Math.min(1, dt*6);
        const busyK = Math.max(look, joy);
        if(wait > 0){ wait -= dt; if(wait <= 0) gt = 0; }
        else if(busyK < .15 && !AVM){ gt += dt; const g = G[gest], r = g.f(Math.min(gt, g.dur)); o.y += r.y; o.rz += r.rz; o.yaw += r.yaw; o.sq = r.sq;
          if(gt >= g.dur){ idx = (idx + 1) % order.length; gest = order[idx]; wait = 1 + Math.random()*2; gt = 0; } }
        if(AVM){ o.y = 0; o.rz *= .3; o.yaw *= .25; }
        if(busyK > .001){
          const tr = AVM ? (joy >= look ? (AVPOSE[AV_ROLE] || AVPOSE.secretary)(tt) : (AV_LOOK === 'diag' ? {y:.004*(1 + Math.sin(tt*4)), rz:.04*Math.sin(tt*2.6), yaw:.62 + .05*Math.sin(tt*1.3), rx:.34, sq:0} : {y:.004*(1 + Math.sin(tt*4)), rz:.035*Math.sin(tt*2.6), yaw:.05*Math.sin(tt*1.3), rx:.5, sq:0}))
            : joy >= look ? (JOY[extRole] || JOY.secretary)(tt) : {y:.012*(1 + Math.sin(tt*5)), rz:Math.sin(tt*3.2)*.05, yaw:Math.sin(tt*1.3)*.07, rx:.4, sq:0};
          o.y = o.y*(1 - busyK) + tr.y*busyK; o.rz = o.rz*(1 - busyK) + tr.rz*busyK; o.yaw = o.yaw*(1 - busyK) + tr.yaw*busyK;
          o.rx = tr.rx*busyK; o.sq = o.sq*(1 - busyK) + tr.sq*busyK; o.eye = 1 - .25*joy;
        }
        if(PROP) PROP.update(tt, joy);
      }
      // apply
      const r = main.root;
      r.position.x = o.x; r.position.y = o.y; r.position.z = o.z; r.rotation.x = o.rx; r.rotation.z = o.rz; r.rotation.y += o.yaw;
      const pl = o.pulse || 1;
      main.puppet.scale.x *= (1 + o.sq*.7)*pl; main.puppet.scale.y *= (1 - o.sq)*pl; main.puppet.scale.z *= (1 + o.sq*.7)*pl;
      for(const e of main.eyes) e.scale.y = (blinkT < 0 ? e.userData.sy : e.scale.y)*o.eye;
      stage.style.setProperty('--heat', o.heat.toFixed(3)); stage.style.setProperty('--mx', o.mx.toFixed(3)); stage.style.setProperty('--ab', o.ab.toFixed(3));
      stage.style.setProperty('--hs', o.hs.toFixed(3)); stage.style.setProperty('--hr', o.hr.toFixed(3) + 'rad');
    }
  };
  window.addEventListener('message', e => { const d = e.data; if(d && d.type === 'ant:state') api.setState(d.state, d.role); });
  if(!CHAT && !AVM) api.intro();
  if(AVM){ if(main.contact) main.contact.visible = false; if(main.ground) main.ground.visible = false; }
  window.addEventListener('message', e => { const d = e.data; if(!d || d.type !== 'ant:config') return;
    if(d.style && STYLE_IDS.includes(d.style)) state.style = d.style;
    const hx = normHex(d.color); if(hx) state.color = hx;
    state.gender = 'male'; rebuildMain();
    if(AVM){ if(PROP) main.root.remove(PROP.g); AV_ROLE = d.role || AV_ROLE; PROP = buildProp(AV_ROLE); }
    try{ parent.postMessage({type:'ant:configured', key:d.key}, '*'); }catch(err){} });
  setTimeout(() => { try{ parent.postMessage({type:'ant:built'}, '*'); }catch(err){} }, 60);
  if(new URLSearchParams(location.search).get('debug')) { window.__DIR = api; api.out = out; }
  return api;
})() : {busy:false, poke(){}, update(){}};
'''
rep("let nextBlink = 2, blinkT = -1, last = performance.now();", director + "\nlet nextBlink = 2, blinkT = -1, last = performance.now();")
rep("    const active = drag.on ||", "    if(main) DIR.update(dt, s);\n    const active = DIR.busy || drag.on ||")
rep("dirty = live > 0 || resetT >= 0", "dirty = DIR.busy || live > 0 || resetT >= 0")
rep("main.render(); announceReady();", "main.render(); announceReady(); if(!window.__shownSent){ window.__shownSent = 1; try{ parent.postMessage({type:'ant:shown'}, '*'); }catch(e){} }")

# ---- snapshot service: ?snap=1 renders avatar PNGs on request via postMessage ----
rep("const PRESET = window.DOT_PRESET || null;", "const PRESET = window.DOT_PRESET || null;" + chr(10) + "const SNAP = new URLSearchParams(location.search).get('snap') === '1';")
rep("main = new Studio(cv, {main:true});", "main = SNAP ? null : new Studio(cv, {main:true});")
rep("if(!VIEW){ const tc = document.createElement('canvas');", "if(!VIEW || SNAP){ const tc = document.createElement('canvas');")
rep("function scheduleThumbs(){" + chr(10) + "  if(!thumb) return;", "function scheduleThumbs(){" + chr(10) + "  if(!thumb || SNAP) return;")
SNAP_HOOK = """if(SNAP && thumb){
  window.addEventListener('message', e => { const d = e.data; if(!d || d.type !== 'ant:render') return;
    const c = {shape:'ant', color:normHex(d.color) || '#E2513F', material:'plush', style:pick(d.style, STYLE_IDS, 'gentleman'), gender:'male'};
    thumb.build(c, d.res || (THUMB_RES + 20)); const P = d.pose || null; thumb.root.rotation.order = 'ZYX'; thumb.root.rotation.y = BASE_YAW*.6 + (P ? P.yaw || 0 : 0); thumb.root.rotation.z = P ? P.rz || 0 : 0; thumb.root.position.y = P ? P.y || 0 : 0;
    if(P){ const sc = thumb.scaleBase, q = P.sq || 0; thumb.puppet.scale.set(sc*(1 + q*.7), sc*(1 - q), sc*(1 + q*.7)); }
    thumb.elev = .1; thumb.place(d.margin || 1.16, true); thumb.render();
    try{ e.source.postMessage({type:'ant:rendered', id:d.id, url:thumb.renderer.domElement.toDataURL('image/png')}, '*'); }catch(err){} });
  try{ parent.postMessage({type:'ant:ready'}, '*'); }catch(err){}
}
"""
rep("function resize(){ if(!main) return;", SNAP_HOOK + "function resize(){ if(!main) return;")
# ---- performance (laptop jank): cheaper main render, throttle idle redraws, no always-on CSS filter ----
rep("powerPreference:'high-performance'", "powerPreference: main ? 'high-performance' : 'low-power'")
rep("r.setPixelRatio(main ? Math.min(devicePixelRatio||1, 2) : 1);", "r.setPixelRatio(main ? Math.min(devicePixelRatio||1, 1.5) : 1);")
rep("r.shadowMap.type = THREE.PCFSoftShadowMap;", "r.shadowMap.type = THREE.PCFShadowMap;")
rep("key.shadow.mapSize.set(2048,2048);", "key.shadow.mapSize.set(1024,1024);")
rep("now - lastDraw > 15.5", "now - lastDraw > 30")
rep("filter:saturate(calc(1 + var(--heat)*.55)) brightness(calc(1 - var(--heat)*.05)) hue-rotate(calc(var(--heat)*-6deg))}",
    "}" + chr(10) + ".viewer .stage.hot canvas.gl{filter:saturate(calc(1 + var(--heat)*.55)) brightness(calc(1 - var(--heat)*.05)) hue-rotate(calc(var(--heat)*-6deg))}")
rep("stage.style.setProperty('--heat', o.heat.toFixed(3));", "stage.classList.toggle('hot', o.heat > .01); stage.style.setProperty('--heat', o.heat.toFixed(3));")
open(os.path.join(ROOT, "ant-mascot.html"), "w", encoding="utf8").write(s)
