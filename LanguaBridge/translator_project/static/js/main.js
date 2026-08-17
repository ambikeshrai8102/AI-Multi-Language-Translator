/* LinguaBridge — Main JS v2 */

// ── State ──
let currentTranslationId = null;

// ── Elements ──
const $ = id => document.getElementById(id);
const sourceText    = $('sourceText');
const resultArea    = $('resultArea');
const sourceLang    = $('sourceLang');
const targetLang    = $('targetLang');
const translateBtn  = $('translateBtn');
const charCount     = $('charCount');
const clearBtn      = $('clearBtn');
const swapBtn       = $('swapBtn');
const copyBtn       = $('copyBtn');
const favoriteBtn   = $('favoriteBtn');
const pastBtn       = $('pastBtn');
const speakSrcBtn   = $('speakSourceBtn');
const speakTgtBtn   = $('speakTargetBtn');
const detectedLang  = $('detectedLang');
const detectedLangTxt = $('detectedLangText');
const translationMeta = $('translationMeta');

// ── Toast ──
function showToast(msg, ms=3000) {
  const t = $('toast');
  if (!t) return;
  t.textContent = msg;
  t.classList.add('show');
  clearTimeout(t._timer);
  t._timer = setTimeout(() => t.classList.remove('show'), ms);
}

// ── Char counter ──
if (sourceText) {
  sourceText.addEventListener('input', () => {
    const n = sourceText.value.length;
    if (charCount) { charCount.textContent = `${n} / 5000`; charCount.style.color = n > 4500 ? 'var(--warning)' : ''; }
  });
}

// ── Lang labels ──
function updateLabels() {
  const sEl = $('sourceLangLabel'), tEl = $('targetLangLabel');
  if (sEl && sourceLang) sEl.textContent = sourceLang.options[sourceLang.selectedIndex]?.text || 'Source Text';
  if (tEl && targetLang) tEl.textContent = targetLang.options[targetLang.selectedIndex]?.text || 'Translation';
}
if (sourceLang) sourceLang.addEventListener('change', updateLabels);
if (targetLang) targetLang.addEventListener('change', updateLabels);
updateLabels();

// ── Swap ──
if (swapBtn) swapBtn.addEventListener('click', () => {
  if (!sourceLang || sourceLang.value === 'auto') return showToast('⚠️ Cannot swap with Auto Detect');
  [sourceLang.value, targetLang.value] = [targetLang.value, sourceLang.value];
  const res = resultArea?.textContent.trim();
  if (res && res !== 'Translation will appear here…' && sourceText) {
    sourceText.value = res;
    sourceText.dispatchEvent(new Event('input'));
    resultArea.innerHTML = '<span class="placeholder-text">Translation will appear here…</span>';
  }
  updateLabels();
});

// ── Quick lang buttons ──
document.querySelectorAll('.quick-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    if (targetLang) targetLang.value = btn.dataset.lang;
    document.querySelectorAll('.quick-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    updateLabels();
  });
});

// ── Clear ──
if (clearBtn) clearBtn.addEventListener('click', () => {
  if (sourceText) { sourceText.value = ''; sourceText.dispatchEvent(new Event('input')); sourceText.focus(); }
  if (resultArea) resultArea.innerHTML = '<span class="placeholder-text">Translation will appear here…</span>';
  if (detectedLang) detectedLang.style.display = 'none';
  if (translationMeta) translationMeta.style.display = 'none';
  currentTranslationId = null;
});

// ── Paste ──
if (pastBtn) pastBtn.addEventListener('click', async () => {
  try {
    const t = await navigator.clipboard.readText();
    if (sourceText) { sourceText.value = t; sourceText.dispatchEvent(new Event('input')); }
  } catch { showToast('⚠️ Clipboard access denied'); }
});

// ── Copy ──
if (copyBtn) copyBtn.addEventListener('click', () => {
  const t = resultArea?.textContent.trim();
  if (!t || t === 'Translation will appear here…') return showToast('Nothing to copy');
  navigator.clipboard.writeText(t).then(() => showToast('📋 Copied!'));
});

// ── TTS ──
function speak(text, lang) {
  if (!text || !window.speechSynthesis) return showToast('Speech not supported');
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = lang || 'en';
  speechSynthesis.speak(u);
}
if (speakSrcBtn) speakSrcBtn.addEventListener('click', () => speak(sourceText?.value.trim(), sourceLang?.value));
if (speakTgtBtn) speakTgtBtn.addEventListener('click', () => {
  const t = resultArea?.textContent.trim();
  if (t && t !== 'Translation will appear here…') speak(t, targetLang?.value);
});

// ── Favorite ──
if (favoriteBtn) favoriteBtn.addEventListener('click', () => {
  if (!currentTranslationId) return showToast('⚠️ Translate something first');
  fetch(window.FAVORITE_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN },
    body: JSON.stringify({ translation_id: currentTranslationId })
  }).then(r => r.json()).then(d => showToast(d.created ? '⭐ Saved to favorites!' : 'Already in favorites'));
});

// ════════ TRANSLATE ════════
async function translate() {
  const text = sourceText?.value.trim();
  if (!text) return showToast('⚠️ Enter some text first');

  if (translateBtn) {
    translateBtn.disabled = true;
    translateBtn.querySelector('.btn-text').textContent = 'Translating…';
    if ($('btnSpinner')) $('btnSpinner').style.display = 'inline-block';
  }
  if (resultArea) { resultArea.innerHTML = '…'; resultArea.classList.add('loading'); }

  try {
    const resp = await fetch(window.TRANSLATE_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN },
      body: JSON.stringify({
        text,
        source_lang: sourceLang?.value || 'auto',
        target_lang:  targetLang?.value  || 'es',
      })
    });
    const data = await resp.json();

    if (data.success) {
      resultArea?.classList.remove('loading');
      if (resultArea) resultArea.textContent = data.translated_text;
      currentTranslationId = data.translation_id;
      if (detectedLang && sourceLang?.value === 'auto') {
        detectedLangTxt.textContent = `Detected: ${data.detected_language_name}`;
        detectedLang.style.display = 'flex';
      }
      if (translationMeta) translationMeta.style.display = 'flex';
      refreshStats();
    } else {
      resultArea?.classList.remove('loading');
      if (resultArea) resultArea.innerHTML = `<span style="color:var(--danger)">⚠️ ${data.error}</span>`;
    }
  } catch(err) {
    resultArea?.classList.remove('loading');
    if (resultArea) resultArea.innerHTML = `<span style="color:var(--danger)">⚠️ Network error</span>`;
  } finally {
    if (translateBtn) {
      translateBtn.disabled = false;
      translateBtn.querySelector('.btn-text').textContent = 'Translate Now';
      if ($('btnSpinner')) $('btnSpinner').style.display = 'none';
    }
  }
}

if (translateBtn) translateBtn.addEventListener('click', translate);
document.addEventListener('keydown', e => { if ((e.ctrlKey||e.metaKey) && e.key === 'Enter') translate(); });

// ════════ BATCH MODE ════════
function switchMode(mode) {
  $('modeSingle').style.display = mode === 'single' ? '' : 'none';
  $('modeBatch').style.display  = mode === 'batch'  ? '' : 'none';
  $('tabSingle').classList.toggle('active', mode === 'single');
  $('tabBatch').classList.toggle('active',  mode === 'batch');
}
window.switchMode = switchMode;

const batchSrcText = $('batchSourceText');
const batchCharCnt = $('batchCharCount');
const batchBtn     = $('batchTranslateBtn');

if (batchSrcText) batchSrcText.addEventListener('input', () => {
  const n = batchSrcText.value.length;
  if (batchCharCnt) batchCharCnt.textContent = `${n} / 5000`;
});

if (batchBtn) batchBtn.addEventListener('click', async () => {
  const text = batchSrcText?.value.trim();
  const checked = [...document.querySelectorAll('.batch-check:checked')].map(c => c.value);
  if (!text) return showToast('⚠️ Enter text first');
  if (!checked.length) return showToast('⚠️ Select at least one language');
  if (checked.length > 8) return showToast('⚠️ Max 8 languages at a time');

  batchBtn.disabled = true;
  batchBtn.querySelector('.btn-text').textContent = 'Translating…';
  if ($('batchBtnSpinner')) $('batchBtnSpinner').style.display = 'inline-block';

  const results = $('batchResults');
  if (results) { results.innerHTML = '<div style="padding:.5rem;color:var(--text-2)">⟳ Translating to ' + checked.length + ' languages…</div>'; results.style.display = ''; }

  try {
    const resp = await fetch(window.BATCH_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': window.CSRF_TOKEN },
      body: JSON.stringify({ text, source_lang: $('batchSourceLang')?.value || 'auto', target_langs: checked })
    });
    const data = await resp.json();

    if (data.success && results) {
      results.innerHTML = data.results.map(r => r.error
        ? `<div class="batch-result-card"><div class="batch-result-lang">${r.flag||''} ${r.lang_name}</div><div style="color:var(--danger)">Error: ${r.error}</div></div>`
        : `<div class="batch-result-card"><div class="batch-result-lang">${r.flag||''} ${r.lang_name}</div><div class="batch-result-text">${r.translated}</div><button class="batch-result-copy" onclick="navigator.clipboard.writeText('${r.translated.replace(/'/g,"\\'")}').then(()=>showToast('📋 Copied!'))">📄 Copy</button></div>`
      ).join('');
    }
  } catch(err) {
    if (results) results.innerHTML = `<div style="padding:.5rem;color:var(--danger)">Network error</div>`;
  } finally {
    batchBtn.disabled = false;
    batchBtn.querySelector('.btn-text').textContent = 'Translate to All';
    if ($('batchBtnSpinner')) $('batchBtnSpinner').style.display = 'none';
  }
});

// ════════ LOAD FROM CARD ════════
window.loadTranslation = function(text, src, tgt) {
  if (sourceText) { sourceText.value = text; sourceText.dispatchEvent(new Event('input')); }
  if (sourceLang) sourceLang.value = src;
  if (targetLang) targetLang.value = tgt;
  updateLabels();
  translate();
  window.scrollTo({ top: 0, behavior: 'smooth' });
};

// ════════ STATS REFRESH ════════
async function refreshStats() {
  if (!window.STATS_URL) return;
  try {
    const d = await fetch(window.STATS_URL).then(r => r.json());
    const el = (id, val) => { const e = $(id); if (e) e.textContent = val; };
    el('stat-translations', d.total_translations);
    el('stat-chars', d.total_characters);
    el('stat-langs', d.languages_used);
  } catch {}
}

// ════════ RE-USE FROM SESSION ════════
(function checkReuse() {
  const raw = sessionStorage.getItem('reuse');
  if (!raw) return;
  sessionStorage.removeItem('reuse');
  try {
    const { text, src, tgt } = JSON.parse(raw);
    if (sourceText) { sourceText.value = text; sourceText.dispatchEvent(new Event('input')); }
    if (sourceLang && src) sourceLang.value = src;
    if (targetLang && tgt) targetLang.value = tgt;
    updateLabels();
  } catch {}
})();

// ── Text Tools Live Analysis ──
(function() {
    const ta = document.getElementById('sourceText');
    const bar = document.getElementById('toolsBar');
    if (!ta || !bar) return;

    ta.addEventListener('input', function() {
        const text = this.value;
        if (!text.trim()) { bar.style.display = 'none'; return; }
        bar.style.display = 'flex';

        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        const chars = text.length;
        const sentences = (text.match(/[.!?]+/g) || []).length || (text.trim() ? 1 : 0);
        const readSec = Math.max(1, Math.round(words / 3.3)); // avg reading speed
        const speakSec = Math.max(1, Math.round(words / 2.3)); // avg speaking speed

        document.getElementById('toolWords').textContent = words;
        document.getElementById('toolChars').textContent = chars;
        document.getElementById('toolSentences').textContent = sentences;
        document.getElementById('toolReadTime').textContent = readSec >= 60
            ? Math.round(readSec / 60) + 'm' : readSec + 's';
        document.getElementById('toolSpeakTime').textContent = speakSec >= 60
            ? Math.round(speakSec / 60) + 'm' : speakSec + 's';
    });
})();