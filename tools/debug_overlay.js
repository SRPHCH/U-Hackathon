/* Optional diagnostics: open the page with ?debug=1 to see viewport / overflow info in the corner. */
(function () {
  if (!/[?&]debug\b/.test(location.search)) return;
  var box = document.createElement('pre');
  box.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:2147483647;margin:0;padding:8px 10px;max-width:92vw;max-height:46vh;overflow:auto;background:rgba(0,0,0,.82);color:#7CFC9A;font:11px/1.4 ui-monospace,Consolas,monospace;border-radius:8px;white-space:pre-wrap;pointer-events:auto';
  function scan() {
    var de = document.documentElement, off = [];
    document.querySelectorAll('body *').forEach(function (e) {
      if (e.closest('#__bundler_thumbnail') || e === box) return;
      var r = e.getBoundingClientRect(); if (!r.width) return;
      if (r.right > de.clientWidth + 1 || r.left < -1) {
        var cs = getComputedStyle(e); if (cs.display === 'none' || cs.visibility === 'hidden') return;
        var cn = typeof e.className === 'string' ? e.className.split(' ')[0] : e.tagName;
        off.push((e.id ? '#' + e.id : '') + '.' + cn + ' [' + Math.round(r.left) + '..' + Math.round(r.right) + '] ' + cs.position + (e.closest('#ws') ? ' (ws)' : ''));
      }
    });
    var vv = window.visualViewport;
    box.textContent = 'inner ' + innerWidth + 'x' + innerHeight + '  dpr ' + devicePixelRatio + '  outer ' + outerWidth + 'x' + outerHeight + '  screen ' + screen.width + 'x' + screen.height +
      '\nclientW ' + de.clientWidth + '  scrollW ' + de.scrollWidth + '  scrollX ' + Math.round(scrollX) + '  visualViewport ' + (vv ? Math.round(vv.width) + 'x' + Math.round(vv.height) + ' @' + vv.scale.toFixed(2) : '-') +
      '\nhash ' + location.hash + '  ws-on ' + de.classList.contains('ws-on') +
      '\noffenders ' + off.length + '\n' + off.slice(0, 14).join('\n');
  }
  function start() { document.body.appendChild(box); scan(); setInterval(scan, 700); }
  if (document.readyState === 'complete') start(); else addEventListener('load', start);
})();
