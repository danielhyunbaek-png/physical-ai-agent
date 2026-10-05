// mt_reader.js -- Monkeytype page reader -> keyboard_v1 over Web Serial (brief 09)
// Physical AI Agent, Oct 3 2026.
//
// Reads Monkeytype's upcoming words from the DOM (#words .word[data-wordindex])
// and streams them to the Mega with the keyboard_v1 fast-TYPE protocol:
//   Q <text>  -> Mega replies "K <free>"  (one line in flight = flow control)
//   GO / END / STOP, and DONE ... stats when a run finishes.
// The Mega types them on the real Nuphy; Monkeytype sees real key presses.
// DEMO ONLY: never submit an automated result to the leaderboard.
//
// HOW TO RUN (Chrome or Edge on the Mac; Safari has no Web Serial):
//   1. Close the Arduino Serial Monitor (only one program can hold the port).
//   2. monkeytype.com -> time 15, english, no punctuation/numbers.
//   3. DevTools (Cmd+Opt+J) -> paste this whole file into the Console -> Enter.
//      (First paste ever: Chrome asks you to type "allow pasting".)
//      Better: DevTools > Sources > Snippets > New snippet, paste once, then
//      run it any time with Cmd+Enter.
//   4. Panel (top-right) -> Connect -> pick /dev/cu.usbmodem11401.
//      Opening the port RESETS the Mega -> RAM-only MAPs are gone; the
//      "setup" box is re-sent after every connect (put MAP 0 J etc. there).
//   5. Arm & Go. Hands off the mouse/keyboard. STOP button aborts.
//
// Dry run without the Mega: run  window.MTR_FAKE = true  in the console first.

(() => {
  if (window.__mtr) { window.__mtr.panel.remove(); window.__mtr.close?.(); }

  const CHUNK = 100;            // chars per Q line (firmware line buffer is 200)
  const ACK_TIMEOUT_MS = 1500;
  const LS_KEY = 'mtr_setup';
  const DEFAULT_SETUP = 'WPM 320\nFPULSE 50\nSAMEKEY 80\nLEAD 800';

  // ---------------- state ----------------
  const st = {
    port: null, writer: null, reader: null,
    connected: false, rxBuf: '', readyResolve: null,
    outbox: '',                 // text not yet sent to the Mega
    lastSentIdx: -1,            // highest data-wordindex already queued
    waitingAck: false, ackTimer: null, free: 1024,
    running: false, firstWordEl: null, observer: null,
    sentChars: 0, keydowns: 0, badChars: 0,
    lineWaiters: [],
  };

  // ---------------- UI ----------------
  const panel = document.createElement('div');
  panel.style.cssText = 'position:fixed;top:8px;right:8px;z-index:2147483647;width:330px;' +
    'background:#111;color:#ddd;font:12px/1.35 ui-monospace,Menlo,monospace;border:1px solid #555;' +
    'border-radius:8px;padding:8px;box-shadow:0 4px 16px #0008';
  panel.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px">
      <b style="color:#e2b714">keyboard_v1 reader</b>
      <span id="mtr-dot" style="color:#c44">● offline</span></div>
    <div style="display:flex;gap:4px;flex-wrap:wrap;margin-bottom:6px">
      <button id="mtr-connect">Connect</button>
      <button id="mtr-setup-send">Send setup</button>
      <button id="mtr-go" style="background:#2a5;color:#fff">Arm &amp; Go</button>
      <button id="mtr-stop" style="background:#c33;color:#fff">STOP</button></div>
    <label style="color:#888">setup (sent after every connect, one cmd per line)</label>
    <textarea id="mtr-setup" rows="4" style="width:100%;box-sizing:border-box;background:#000;color:#ddd;border:1px solid #444;font:inherit"></textarea>
    <div style="display:flex;gap:4px;margin:4px 0">
      <input id="mtr-cmd" placeholder="raw command, Enter to send" style="flex:1;background:#000;color:#ddd;border:1px solid #444;font:inherit">
    </div>
    <div id="mtr-stats" style="color:#9cf;margin:4px 0">sent 0 · typed 0 · Mega queue free 1024</div>
    <div id="mtr-focus" style="color:#c44;display:none">⚠ Monkeytype NOT focused — keys will be lost</div>
    <pre id="mtr-log" style="height:140px;overflow:auto;background:#000;margin:4px 0 0;padding:4px;white-space:pre-wrap"></pre>`;
  document.body.appendChild(panel);
  panel.querySelectorAll('button').forEach(b => b.style.cssText += ';font:inherit;padding:3px 8px;border-radius:4px;border:1px solid #555;cursor:pointer');
  const $ = id => panel.querySelector('#' + id);
  let saved = null; try { saved = localStorage.getItem(LS_KEY); } catch (_) {}
  $('mtr-setup').value = saved ?? DEFAULT_SETUP;
  $('mtr-setup').addEventListener('input', () => { try { localStorage.setItem(LS_KEY, $('mtr-setup').value); } catch (_) {} });

  const log = (s, color) => {
    const el = $('mtr-log');
    const line = document.createElement('div');
    line.textContent = s;
    if (color) line.style.color = color;
    el.appendChild(line);
    while (el.childNodes.length > 300) el.removeChild(el.firstChild);
    el.scrollTop = el.scrollHeight;
  };
  const setDot = (on) => { $('mtr-dot').textContent = on ? '● connected' : '● offline'; $('mtr-dot').style.color = on ? '#2c5' : '#c44'; };
  const refreshStats = () => {
    $('mtr-stats').textContent = `sent ${st.sentChars} · typed ${st.keydowns} · ahead ${st.sentChars - st.keydowns} · Mega free ${st.free}` +
      (st.badChars ? ` · ⚠ ${st.badChars} non a-z/space chars` : '');
  };

  // ---------------- Monkeytype DOM ----------------
  const wordsEl = () => document.querySelector('#words');
  const wordText = (w) => [...w.querySelectorAll('letter')].filter(l => !l.classList.contains('extra')).map(l => l.textContent).join('');
  const testFinished = () => {
    const r = document.querySelector('#result');
    return !!r && !r.classList.contains('hidden');
  };
  const isFocused = () => { const w = wordsEl(); return !!w && !w.classList.contains('blurred'); };
  const testStarted = () => {
    const inp = document.querySelector('#wordsInput');
    return !!document.querySelector('#words .word.typed') || (inp && inp.value.trim().length > 0);
  };

  function collectNewWords() {
    const ws = [...document.querySelectorAll('#words .word[data-wordindex]')];
    let added = 0;
    for (const w of ws) {
      const idx = +w.dataset.wordindex;
      if (idx <= st.lastSentIdx) continue;
      if (idx !== st.lastSentIdx + 1) { log(`gap: word ${st.lastSentIdx + 1} missing, got ${idx}`, '#fa0'); }
      const t = wordText(w);
      if (/[^a-z]/.test(t)) st.badChars += (t.match(/[^a-z]/g) || []).length;
      st.outbox += t + ' ';
      st.lastSentIdx = idx;
      added++;
    }
    return added;
  }

  // ---------------- serial ----------------
  function makeFakePort() {            // dry-run stand-in for the Mega
    let q = 0, ctrl = null, running = false, timer = null;
    const enc = new TextEncoder();
    const say = s => ctrl && ctrl.enqueue(enc.encode(s + '\r\n'));
    return {
      async open() {},
      readable: new ReadableStream({ start(c) { ctrl = c; setTimeout(() => say('keyboard_v1 ready  cells=11 (FAKE)'), 300); } }),
      writable: new WritableStream({ write(chunk) {
        for (const line of new TextDecoder().decode(chunk).split('\n')) {
          if (!line) continue;
          if (line.startsWith('Q ')) { q += line.length - 2; say('K ' + (1024 - q)); }
          else if (line === 'GO') { running = true; say('OK GO in 800 ms (FAKE)'); timer = setInterval(() => { if (q > 0) q--; }, 36); }
          else if (line === 'STOP') { q = 0; clearInterval(timer); say(running ? 'DONE stopped (FAKE)' : 'OK STOP'); running = false; say('K 1024'); }
          else say('OK ' + line + ' (FAKE)');
        }
      } }),
      async close() { clearInterval(timer); },
    };
  }

  async function connect() {
    try {
      if (st.port) await disconnect();
      st.port = window.MTR_FAKE ? makeFakePort() : await navigator.serial.requestPort();
      await st.port.open({ baudRate: 115200 });
      st.writer = st.port.writable.getWriter();
      st.connected = true; setDot(true);
      log('port open — waiting for Mega reset/banner…');
      readLoop();
      const ready = new Promise(res => (st.readyResolve = res));
      await Promise.race([ready, new Promise(res => setTimeout(res, 4000))]);
      st.readyResolve = null;
      await sendSetup();
    } catch (e) { log('connect failed: ' + e.message, '#f66'); setDot(false); }
  }

  async function disconnect() {
    try { st.reader && await st.reader.cancel(); } catch (_) {}
    try { st.writer && st.writer.releaseLock(); } catch (_) {}
    try { st.port && await st.port.close(); } catch (_) {}
    st.port = st.writer = st.reader = null; st.connected = false; setDot(false);
  }

  async function readLoop() {
    const dec = new TextDecoder();
    st.reader = st.port.readable.getReader();
    try {
      for (;;) {
        const { value, done } = await st.reader.read();
        if (done) break;
        st.rxBuf += dec.decode(value, { stream: true });
        let i;
        while ((i = st.rxBuf.indexOf('\n')) >= 0) {
          const line = st.rxBuf.slice(0, i).replace(/\r$/, '');
          st.rxBuf = st.rxBuf.slice(i + 1);
          onLine(line);
        }
      }
    } catch (e) { log('serial read ended: ' + e.message, '#f66'); }
    finally { try { st.reader.releaseLock(); } catch (_) {} st.connected = false; setDot(false); }
  }

  function onLine(line) {
    const k = line.match(/K (\d+)\s*$/);           // "K n" or "ERR qfull K n" or "OK STOP  K n"
    if (k) {
      st.free = +k[1];
      if (/^ERR qfull/.test(line)) log(line, '#fa0');
      if (st.waitingAck) { st.waitingAck = false; clearTimeout(st.ackTimer); }
      refreshStats();
      pump();
      if (!/^K /.test(line)) { log(line); st.lineWaiters.splice(0).forEach(f => f(line)); }
      return;
    }
    if (/keyboard_v1 ready/.test(line) && st.readyResolve) st.readyResolve();
    if (/^DONE/.test(line)) { log(line, '#2c5'); st.running = false; }
    else log(line, /^ERR|^WARN/.test(line) ? '#f66' : undefined);
    st.lineWaiters.splice(0).forEach(f => f(line));
  }

  async function writeLine(s) {
    if (!st.connected) { log('not connected', '#f66'); return; }
    await st.writer.write(new TextEncoder().encode(s + '\n'));
  }
  const nextLine = (ms = 1500) => new Promise(res => { st.lineWaiters.push(res); setTimeout(() => res(null), ms); });

  async function sendSetup() {
    const lines = $('mtr-setup').value.split('\n').map(s => s.trim()).filter(Boolean);
    for (const l of lines) {
      if (/^SAVE$/i.test(l)) { log('skipped SAVE (RAM-only test rule)', '#fa0'); continue; }
      log('> ' + l, '#888');
      await writeLine(l);
      await nextLine(800);
    }
  }

  // one Q line in flight; never send more than the Mega says it has room for
  function pump() {
    if (!st.connected || st.waitingAck || !st.outbox) return;
    const room = st.free - 8;
    if (room < 10) return;                        // wait for the Mega to drain
    const n = Math.min(CHUNK, room, st.outbox.length);
    const chunk = st.outbox.slice(0, n);
    st.outbox = st.outbox.slice(n);
    st.sentChars += n;
    st.waitingAck = true;
    st.ackTimer = setTimeout(() => { st.waitingAck = false; log('ack timeout', '#fa0'); pump(); }, ACK_TIMEOUT_MS);
    writeLine('Q ' + chunk);
    refreshStats();
  }

  // ---------------- run control ----------------
  async function armAndGo() {
    if (!st.connected) { log('Connect first', '#f66'); return; }
    if (st.running) { log('already running — STOP first', '#f66'); return; }
    if (testFinished() || testStarted()) {
      log('Test not fresh: click the page, press Tab then Enter (or Esc) to restart, then Arm again.', '#f66');
      return;
    }
    await writeLine('STOP'); await nextLine(800);
    Object.assign(st, { outbox: '', lastSentIdx: -1, sentChars: 0, keydowns: 0, badChars: 0, free: 1024, waitingAck: false });
    st.firstWordEl = document.querySelector('#words .word[data-wordindex="0"]');
    collectNewWords();
    if (st.badChars) log(`⚠ ${st.badChars} chars outside a-z/space (punctuation/numbers on?) — they will be silent slots`, '#fa0');
    pump();
    // wait until the first chunk is acknowledged so typing starts with data queued
    for (let i = 0; i < 30 && st.waitingAck; i++) await new Promise(r => setTimeout(r, 50));
    watchWords();
    focusTest();
    st.running = true;
    await writeLine('GO');
    log(`GO — ${st.lastSentIdx + 1} words found, ${st.sentChars} chars queued`, '#2c5');
  }

  async function stop(why) {
    const was = st.running;
    st.running = false;
    st.outbox = '';
    if (was) log('STOP (' + why + ')', '#fa0');
    if (st.connected) await writeLine('STOP');
  }

  function focusTest() {
    document.activeElement && document.activeElement.blur && document.activeElement.blur();
    const inp = document.querySelector('#wordsInput');
    inp && inp.focus();
  }

  function watchWords() {
    st.observer && st.observer.disconnect();
    const w = wordsEl();
    if (!w) return;
    st.observer = new MutationObserver(() => {
      if (!st.running) return;
      const first = document.querySelector('#words .word[data-wordindex="0"]');
      if (first && st.firstWordEl && first !== st.firstWordEl && !testStarted()) { stop('test restarted'); return; }
      if (collectNewWords()) pump();
    });
    st.observer.observe(w, { childList: true });
  }

  // end-of-test + focus watchdog
  const tick = setInterval(() => {
    $('mtr-focus').style.display = (st.running && !isFocused()) ? 'block' : 'none';
    if (st.running && testFinished()) {
      const wpm = document.querySelector('#result .wpm .bottom')?.textContent;
      const acc = document.querySelector('#result .acc .bottom')?.textContent;
      stop('test finished');
      log(`Monkeytype result: ${wpm} wpm, ${acc} acc`, '#e2b714');
    }
    refreshStats();
  }, 50);

  const onKey = (e) => { if (st.running && e.key && (e.key.length === 1)) st.keydowns++; };
  window.addEventListener('keydown', onKey, true);

  // ---------------- wire buttons ----------------
  $('mtr-connect').onclick = connect;
  $('mtr-setup-send').onclick = sendSetup;
  $('mtr-go').onclick = armAndGo;
  $('mtr-stop').onclick = () => stop('button');
  $('mtr-cmd').addEventListener('keydown', async (e) => {
    e.stopPropagation();                         // keep Monkeytype from seeing these keys
    if (e.key === 'Enter') { const v = e.target.value.trim(); if (v) { log('> ' + v, '#888'); await writeLine(v); } e.target.value = ''; }
  });
  $('mtr-setup').addEventListener('keydown', e => e.stopPropagation());

  window.__mtr = {
    panel, st,
    close() { clearInterval(tick); window.removeEventListener('keydown', onKey, true); st.observer && st.observer.disconnect(); disconnect(); },
  };
  log(window.MTR_FAKE ? 'FAKE serial mode (no Mega)' : ('Web Serial ' + ('serial' in navigator ? 'available' : 'NOT available — use Chrome/Edge')));
})();
