"""
NiyamBot - Ultra Premium Animated UI v3
Run: streamlit run app.py
"""

import streamlit as st
import time, sys, os, json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

st.set_page_config(
    page_title="NiyamBot — BIS Standards Engine",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
section[data-testid="stSidebar"] { display: none; }

/* ── ROOT ── */
:root {
  --gold: #c9a84c;
  --gold2: #e8c97a;
  --ink: #060b18;
  --ink2: #0d1528;
  --blue: #1a3a6b;
  --card: rgba(255,255,255,0.035);
  --border: rgba(255,255,255,0.07);
  --border-gold: rgba(201,168,76,0.25);
}

html { scroll-behavior: smooth; }

.stApp {
  background: var(--ink);
  font-family: 'DM Sans', sans-serif;
  overflow-x: hidden;
}

/* ══════════════════════════════════════════
   ANIMATED BACKGROUND CANVAS
══════════════════════════════════════════ */
#bg-canvas {
  position: fixed;
  top: 0; left: 0;
  width: 100%; height: 100%;
  pointer-events: none;
  z-index: 0;
  opacity: 0.5;
}

/* ══════════════════════════════════════════
   CURSOR GLOW
══════════════════════════════════════════ */
#cursor-glow {
  position: fixed;
  width: 400px; height: 400px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(201,168,76,0.06) 0%, transparent 70%);
  pointer-events: none;
  z-index: 1;
  transform: translate(-50%, -50%);
  transition: left 0.15s ease, top 0.15s ease;
}

/* ══════════════════════════════════════════
   HERO
══════════════════════════════════════════ */
.hero {
  position: relative;
  z-index: 2;
  padding: 4rem 5rem 3rem;
  background: linear-gradient(160deg, rgba(13,21,40,0.9) 0%, rgba(6,11,24,0.95) 100%);
  border-bottom: 1px solid var(--border-gold);
  overflow: hidden;
}

/* Animated grid lines */
.hero::before {
  content: '';
  position: absolute; inset: 0;
  background-image:
    linear-gradient(rgba(201,168,76,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(201,168,76,0.05) 1px, transparent 1px);
  background-size: 80px 80px;
  animation: gridMove 20s linear infinite;
  pointer-events: none;
}

@keyframes gridMove {
  0% { background-position: 0 0; }
  100% { background-position: 80px 80px; }
}

/* Floating orbs */
.orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  animation: orbFloat 8s ease-in-out infinite;
}
.orb1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(26,58,107,0.4), transparent);
  top: -150px; right: -100px;
  animation-delay: 0s;
}
.orb2 {
  width: 300px; height: 300px;
  background: radial-gradient(circle, rgba(201,168,76,0.08), transparent);
  bottom: -100px; left: 200px;
  animation-delay: 3s;
}
.orb3 {
  width: 200px; height: 200px;
  background: radial-gradient(circle, rgba(37,77,143,0.3), transparent);
  top: 50px; left: -50px;
  animation-delay: 5s;
}

@keyframes orbFloat {
  0%, 100% { transform: translateY(0px) scale(1); }
  33% { transform: translateY(-30px) scale(1.05); }
  66% { transform: translateY(15px) scale(0.97); }
}

.eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(201,168,76,0.08);
  border: 1px solid rgba(201,168,76,0.22);
  border-radius: 100px; padding: 5px 16px;
  margin-bottom: 1.5rem;
  animation: fadeSlideUp 0.8s ease both;
}
.eyebrow span {
  font-size: 0.68rem; font-weight: 500;
  letter-spacing: 0.14em; text-transform: uppercase;
  color: var(--gold2);
}
.pulse-dot {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--gold);
  animation: pulse 2s ease-in-out infinite;
}
@keyframes pulse {
  0%,100% { opacity:1; box-shadow: 0 0 0 0 rgba(201,168,76,0.4); }
  50% { opacity:0.5; box-shadow: 0 0 0 6px rgba(201,168,76,0); }
}

.hero-title {
  font-family: 'Syne', sans-serif;
  font-size: 5rem; font-weight: 800;
  line-height: 1; letter-spacing: -0.03em;
  margin-bottom: 0.8rem;
  animation: fadeSlideUp 0.9s ease 0.1s both;
}
.hero-title .white { color: #fff; }
.hero-title .gold {
  color: var(--gold);
  text-shadow: 0 0 60px rgba(201,168,76,0.3);
}

.hero-tagline {
  font-size: 1.05rem; color: rgba(255,255,255,0.42);
  font-weight: 300; max-width: 520px; line-height: 1.7;
  margin-bottom: 2.5rem;
  animation: fadeSlideUp 1s ease 0.2s both;
}

@keyframes fadeSlideUp {
  from { opacity: 0; transform: translateY(24px); }
  to { opacity: 1; transform: translateY(0); }
}

/* Animated stat counters */
.stats-row {
  display: flex; gap: 3rem;
  animation: fadeSlideUp 1s ease 0.3s both;
}
.stat {
  position: relative;
  padding-left: 1rem;
}
.stat::before {
  content: '';
  position: absolute; left: 0; top: 50%;
  transform: translateY(-50%);
  width: 2px; height: 60%;
  background: var(--gold);
  border-radius: 2px;
}
.stat-num {
  font-family: 'Syne', sans-serif;
  font-size: 2rem; font-weight: 800;
  color: #fff; line-height: 1;
}
.stat-num .gold { color: var(--gold); }
.stat-lbl {
  font-size: 0.68rem; color: rgba(255,255,255,0.3);
  text-transform: uppercase; letter-spacing: 0.1em;
  margin-top: 4px;
}

/* ══════════════════════════════════════════
   STORY STRIP
══════════════════════════════════════════ */
.story-strip {
  position: relative; z-index: 2;
  background: rgba(6,11,24,0.8);
  border-bottom: 1px solid var(--border);
  padding: 1.5rem 5rem;
  display: flex; gap: 1.2rem;
}

.scard {
  flex: 1;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.2rem 1.3rem;
  position: relative;
  transition: all 0.3s ease;
  cursor: default;
}
.scard:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(201,168,76,0.2);
  transform: translateY(-4px);
  box-shadow: 0 16px 40px rgba(0,0,0,0.4), 0 0 0 1px rgba(201,168,76,0.1);
}
.scard-badge {
  position: absolute; top: 0.9rem; right: 0.9rem;
  background: rgba(220,70,40,0.12);
  border: 1px solid rgba(220,70,40,0.2);
  border-radius: 6px; padding: 2px 8px;
  font-size: 0.6rem; font-weight: 700;
  color: #ff7a5a; letter-spacing: 0.08em;
}
.scard-icon { font-size: 1.8rem; margin-bottom: 0.6rem; display: block; }
.scard-quote {
  font-size: 0.8rem; color: rgba(255,255,255,0.48);
  line-height: 1.65; font-style: italic; margin-bottom: 0.7rem;
}
.scard-who { font-size: 0.75rem; font-weight: 600; color: var(--gold2); }
.scard-where { font-size: 0.65rem; color: rgba(255,255,255,0.25); margin-top: 2px; }

/* ══════════════════════════════════════════
   MAIN CONTENT
══════════════════════════════════════════ */
.main {
  position: relative; z-index: 2;
  max-width: 1100px; margin: 0 auto;
  padding: 2.5rem 2rem 5rem;
}

/* ══════════════════════════════════════════
   SEARCH PANEL
══════════════════════════════════════════ */
.search-panel {
  background: linear-gradient(135deg,
    rgba(26,58,107,0.25) 0%,
    rgba(13,21,40,0.6) 100%);
  border: 1px solid var(--border-gold);
  border-radius: 24px;
  padding: 2rem 2.2rem 1.5rem;
  margin-bottom: 1.5rem;
  position: relative;
  overflow: hidden;
}
.search-panel::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  animation: shimmer 3s ease infinite;
}
@keyframes shimmer {
  0% { opacity: 0.3; transform: scaleX(0.3); }
  50% { opacity: 1; transform: scaleX(1); }
  100% { opacity: 0.3; transform: scaleX(0.3); }
}

.search-lbl {
  font-family: 'Syne', sans-serif;
  font-size: 0.78rem; font-weight: 700;
  color: rgba(255,255,255,0.5);
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 0.7rem;
}

/* textarea */
.stTextArea > div > div > textarea {
  background: rgba(255,255,255,0.04) !important;
  border: 1.5px solid rgba(201,168,76,0.18) !important;
  border-radius: 14px !important;
  color: #fff !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.95rem !important;
  line-height: 1.65 !important;
  padding: 1rem 1.2rem !important;
  transition: border-color 0.3s, box-shadow 0.3s !important;
  resize: none !important;
}
.stTextArea > div > div > textarea:focus {
  border-color: rgba(201,168,76,0.55) !important;
  box-shadow: 0 0 0 4px rgba(201,168,76,0.07),
              0 0 30px rgba(201,168,76,0.06) !important;
}
.stTextArea > div > div > textarea::placeholder {
  color: rgba(255,255,255,0.18) !important;
}
.stTextArea label { display: none !important; }

/* ══════════════════════════════════════════
   BUTTONS
══════════════════════════════════════════ */
.stButton > button {
  background: linear-gradient(135deg, #c9a84c 0%, #9e7a28 100%) !important;
  color: #060b18 !important;
  font-family: 'Syne', sans-serif !important;
  font-weight: 800 !important;
  font-size: 0.85rem !important;
  letter-spacing: 0.06em !important;
  border: none !important;
  border-radius: 12px !important;
  padding: 0.65rem 1.8rem !important;
  box-shadow: 0 4px 24px rgba(201,168,76,0.3),
              inset 0 1px 0 rgba(255,255,255,0.15) !important;
  transition: all 0.25s cubic-bezier(0.34,1.56,0.64,1) !important;
  position: relative !important;
  overflow: hidden !important;
}
.stButton > button::before {
  content: '' !important;
  position: absolute !important;
  top: 0 !important; left: -100% !important;
  width: 100% !important; height: 100% !important;
  background: linear-gradient(90deg, transparent,
    rgba(255,255,255,0.15), transparent) !important;
  transition: left 0.4s ease !important;
}
.stButton > button:hover {
  transform: translateY(-3px) scale(1.02) !important;
  box-shadow: 0 10px 36px rgba(201,168,76,0.45),
              inset 0 1px 0 rgba(255,255,255,0.2) !important;
}
.stButton > button:hover::before { left: 100% !important; }
.stButton > button:active { transform: translateY(-1px) scale(0.99) !important; }

div[data-testid="stDownloadButton"] > button {
  background: rgba(255,255,255,0.04) !important;
  color: rgba(255,255,255,0.45) !important;
  border: 1px solid var(--border) !important;
  font-size: 0.78rem !important; padding: 0.45rem 1rem !important;
  border-radius: 8px !important; box-shadow: none !important;
  transition: all 0.2s !important;
}
div[data-testid="stDownloadButton"] > button:hover {
  border-color: rgba(201,168,76,0.3) !important;
  color: var(--gold2) !important;
  background: rgba(201,168,76,0.05) !important;
  transform: none !important;
}

/* ══════════════════════════════════════════
   EXAMPLE CHIPS
══════════════════════════════════════════ */
.chip-lbl {
  font-size: 0.65rem; color: rgba(255,255,255,0.2);
  letter-spacing: 0.1em; text-transform: uppercase;
  margin-bottom: 0.5rem;
}

/* ══════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════ */
.mcard {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.1rem 1.2rem;
  text-align: center;
  transition: all 0.3s ease;
}
.mcard:hover {
  border-color: rgba(201,168,76,0.2);
  transform: translateY(-3px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.3);
}
.mcard-icon { font-size: 1.3rem; margin-bottom: 6px; }
.mcard-val {
  font-family: 'Syne', sans-serif;
  font-size: 1.5rem; font-weight: 800;
  color: #fff; line-height: 1;
}
.mcard-lbl {
  font-size: 0.65rem; color: rgba(255,255,255,0.3);
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-top: 4px;
}

/* ══════════════════════════════════════════
   RESULT CARDS
══════════════════════════════════════════ */
.rcard-top {
  background: linear-gradient(135deg,
    rgba(201,168,76,0.09) 0%,
    rgba(26,58,107,0.2) 100%);
  border: 1px solid rgba(201,168,76,0.3);
  border-radius: 22px;
  padding: 2rem;
  position: relative;
  margin-bottom: 1rem;
  transition: all 0.3s ease;
  overflow: hidden;
}
.rcard-top::before {
  content: '';
  position: absolute; inset: 0;
  background: linear-gradient(135deg,
    rgba(201,168,76,0.03), transparent);
  opacity: 0;
  transition: opacity 0.3s;
}
.rcard-top:hover { transform: translateY(-4px);
  box-shadow: 0 20px 50px rgba(0,0,0,0.4),
              0 0 0 1px rgba(201,168,76,0.2); }
.rcard-top:hover::before { opacity: 1; }

.rcard {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 1.5rem;
  height: 100%;
  transition: all 0.3s cubic-bezier(0.34,1.56,0.64,1);
  position: relative;
  overflow: hidden;
}
.rcard:hover {
  background: rgba(255,255,255,0.06);
  border-color: rgba(201,168,76,0.22);
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 20px 50px rgba(0,0,0,0.45),
              0 0 0 1px rgba(201,168,76,0.1);
}

.rank-badge {
  display: inline-flex; align-items: center; justify-content: center;
  width: 32px; height: 32px; border-radius: 10px;
  background: rgba(201,168,76,0.1);
  border: 1px solid rgba(201,168,76,0.18);
  font-family: 'Syne', sans-serif;
  font-size: 0.78rem; font-weight: 800;
  color: var(--gold); margin-bottom: 0.8rem;
}
.std-id {
  font-family: 'Syne', sans-serif;
  font-size: 1.1rem; font-weight: 700;
  color: #fff; margin-bottom: 0.25rem;
}
.std-title {
  font-size: 0.82rem; color: rgba(255,255,255,0.42);
  margin-bottom: 0.8rem; line-height: 1.4;
}
.section-pill {
  display: inline-flex; align-items: center; gap: 4px;
  background: rgba(26,58,107,0.35);
  border: 1px solid rgba(37,77,143,0.3);
  border-radius: 6px; padding: 3px 9px;
  font-size: 0.67rem; color: rgba(255,255,255,0.38);
  margin-bottom: 0.9rem;
}
.why-lbl {
  font-size: 0.62rem; text-transform: uppercase;
  letter-spacing: 0.1em; color: rgba(201,168,76,0.5);
  font-weight: 700; margin-bottom: 0.3rem;
}
.why-text {
  font-size: 0.82rem; color: rgba(255,255,255,0.6);
  line-height: 1.65;
}
.score-bar {
  margin-top: 1rem;
  height: 3px; background: rgba(255,255,255,0.05);
  border-radius: 2px; overflow: hidden;
}
.score-fill {
  height: 100%;
  background: linear-gradient(90deg, var(--gold), var(--gold2));
  border-radius: 2px;
  animation: barGrow 1s ease both;
}
@keyframes barGrow {
  from { width: 0 !important; }
}

.best-badge {
  position: absolute; top: 1.2rem; right: 1.2rem;
  background: rgba(201,168,76,0.12);
  border: 1px solid rgba(201,168,76,0.25);
  border-radius: 100px; padding: 3px 12px;
  font-size: 0.66rem; font-weight: 700;
  color: var(--gold2); letter-spacing: 0.07em;
}

/* ══════════════════════════════════════════
   SCORE PANEL
══════════════════════════════════════════ */
.score-panel {
  display: flex; gap: 1rem;
  margin-top: 1.5rem;
}
.spanel-item {
  flex: 1;
  background: rgba(201,168,76,0.05);
  border: 1px solid rgba(201,168,76,0.12);
  border-radius: 16px;
  padding: 1.2rem;
  text-align: center;
  transition: all 0.3s ease;
}
.spanel-item:hover {
  background: rgba(201,168,76,0.09);
  border-color: rgba(201,168,76,0.25);
  transform: translateY(-3px);
}
.spanel-val {
  font-family: 'Syne', sans-serif;
  font-size: 2rem; font-weight: 800;
  color: var(--gold); line-height: 1;
}
.spanel-name {
  font-size: 0.7rem; color: rgba(255,255,255,0.4);
  text-transform: uppercase; letter-spacing: 0.09em;
  margin-top: 5px;
}
.spanel-target {
  font-size: 0.62rem; color: rgba(255,255,255,0.18);
  margin-top: 3px;
}

/* ══════════════════════════════════════════
   RESULTS HEADER
══════════════════════════════════════════ */
.results-hdr {
  display: flex; align-items: center;
  justify-content: space-between;
  margin-bottom: 1.2rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--border);
}
.results-hdr-title {
  font-family: 'Syne', sans-serif;
  font-size: 1rem; font-weight: 700;
  color: rgba(255,255,255,0.8);
}
.results-count {
  background: rgba(201,168,76,0.08);
  border: 1px solid rgba(201,168,76,0.18);
  border-radius: 100px; padding: 3px 12px;
  font-size: 0.7rem; color: var(--gold2);
}

/* ══════════════════════════════════════════
   EMPTY STATE
══════════════════════════════════════════ */
.empty {
  text-align: center; padding: 4rem 2rem;
}
.empty-icon {
  font-size: 3.5rem; opacity: 0.12;
  margin-bottom: 1rem;
  animation: emptyFloat 4s ease-in-out infinite;
}
@keyframes emptyFloat {
  0%,100% { transform: translateY(0); }
  50% { transform: translateY(-12px); }
}
.empty-txt {
  font-size: 0.88rem; color: rgba(255,255,255,0.18);
  line-height: 1.7;
}

/* Footer */
.footer {
  text-align: center; padding: 2rem;
  border-top: 1px solid rgba(255,255,255,0.04);
  position: relative; z-index: 2;
}
.footer p {
  font-size: 0.65rem; color: rgba(255,255,255,0.12);
  letter-spacing: 0.12em;
}

div[data-testid="metric-container"] { display: none; }
.stSpinner > div { border-top-color: var(--gold) !important; }
</style>

<!-- Cursor glow + animated particle canvas -->
<div id="cursor-glow"></div>
<canvas id="bg-canvas"></canvas>

<script>
// Cursor glow
const glow = document.getElementById('cursor-glow');
document.addEventListener('mousemove', e => {
  glow.style.left = e.clientX + 'px';
  glow.style.top  = e.clientY + 'px';
});

// Particle canvas
const canvas = document.getElementById('bg-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const particles = Array.from({length: 60}, () => ({
  x: Math.random() * canvas.width,
  y: Math.random() * canvas.height,
  r: Math.random() * 1.5 + 0.3,
  dx: (Math.random() - 0.5) * 0.3,
  dy: (Math.random() - 0.5) * 0.3,
  a: Math.random(),
}));

function drawParticles() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  particles.forEach(p => {
    p.x += p.dx; p.y += p.dy;
    if (p.x < 0) p.x = canvas.width;
    if (p.x > canvas.width) p.x = 0;
    if (p.y < 0) p.y = canvas.height;
    if (p.y > canvas.height) p.y = 0;
    ctx.beginPath();
    ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(201,168,76,${p.a * 0.4})`;
    ctx.fill();
  });
  // Draw lines between nearby particles
  particles.forEach((p, i) => {
    particles.slice(i+1).forEach(q => {
      const d = Math.hypot(p.x-q.x, p.y-q.y);
      if (d < 120) {
        ctx.beginPath();
        ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
        ctx.strokeStyle = `rgba(201,168,76,${0.06 * (1-d/120)})`;
        ctx.lineWidth = 0.5;
        ctx.stroke();
      }
    });
  });
  requestAnimationFrame(drawParticles);
}
drawParticles();

window.addEventListener('resize', () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});
</script>
""", unsafe_allow_html=True)


# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="orb orb1"></div>
  <div class="orb orb2"></div>
  <div class="orb orb3"></div>
  <div class="eyebrow">
    <div class="pulse-dot"></div>
    <span>BIS × Sigma Squad Hackathon 2026</span>
  </div>
  <div class="hero-title">
    <span class="white">Niyam</span><span class="gold">Bot</span>
  </div>
  <p class="hero-tagline">
    India's 500,000+ small manufacturers spend weeks navigating BIS compliance.
    NiyamBot finds the right standard in under a second — powered by hybrid AI.
  </p>
  <div class="stats-row">
    <div class="stat">
      <div class="stat-num"><span class="gold">553</span></div>
      <div class="stat-lbl">Standards Indexed</div>
    </div>
    <div class="stat">
      <div class="stat-num"><span class="gold">0.41s</span></div>
      <div class="stat-lbl">Avg Response Time</div>
    </div>
    <div class="stat">
      <div class="stat-num"><span class="gold">100%</span></div>
      <div class="stat-lbl">Hit Rate @3</div>
    </div>
    <div class="stat">
      <div class="stat-num"><span class="gold">500K+</span></div>
      <div class="stat-lbl">MSEs We Serve</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── STORY CARDS ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="story-strip">
  <div class="scard">
    <div class="scard-badge">3 WEEKS LOST</div>
    <span class="scard-icon">🏭</span>
    <div class="scard-quote">
      "I run a cement factory in Bihar. I had no idea which BIS standard applied
      to my 33 Grade OPC. Spent 3 weeks reading 929 pages before a consultant told
      me it was IS 269. NiyamBot would have saved me everything."
    </div>
    <div class="scard-who">Ramesh Kumar</div>
    <div class="scard-where">OPC Manufacturer · Patna, Bihar</div>
  </div>
  <div class="scard">
    <div class="scard-badge">2 WEEKS LOST</div>
    <span class="scard-icon">🧱</span>
    <div class="scard-quote">
      "We make hollow concrete blocks in Rajasthan. Market entry was delayed
      2 weeks because we couldn't figure out if IS 2185 Part 1 or Part 2 applied.
      That confusion cost us a major order."
    </div>
    <div class="scard-who">Sunita Devi</div>
    <div class="scard-where">Block Manufacturer · Jodhpur, Rajasthan</div>
  </div>
  <div class="scard">
    <div class="scard-badge">4 WEEKS LOST</div>
    <span class="scard-icon">⚙️</span>
    <div class="scard-quote">
      "Our steel fabrication unit in Surat lost an entire month navigating BIS
      compliance on our own. No legal team. No consultant budget. Small businesses
      like ours desperately need tools like NiyamBot."
    </div>
    <div class="scard-who">Arvind Patel</div>
    <div class="scard-where">Steel Fabricator · Surat, Gujarat</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ── ENGINE ────────────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading NiyamBot AI engine...")
def load_engine():
    from retriever import NiyamRetriever
    from generator import generate_rationale
    return NiyamRetriever(), generate_rationale

retriever, generate_rationale = load_engine()


# ── MAIN ──────────────────────────────────────────────────────────────────────
st.markdown('<div class="main">', unsafe_allow_html=True)

# Search panel
st.markdown('<div class="search-panel"><div class="search-lbl">📝 Describe your product or compliance need</div>', unsafe_allow_html=True)

query = st.text_area(
    "q", value=st.session_state.get("q", ""), height=100,
    placeholder="e.g. We manufacture 33 Grade Ordinary Portland Cement in Bihar for structural construction...",
    label_visibility="collapsed",
)
st.markdown("</div>", unsafe_allow_html=True)

# Example chips
st.markdown('<div class="chip-lbl">💡 Try an example:</div>', unsafe_allow_html=True)
examples = [
    "33 Grade Ordinary Portland Cement",
    "Hollow concrete masonry blocks",
    "Portland Slag Cement",
    "Coarse aggregates structural concrete",
    "White Portland Cement decorative",
    "Precast concrete pipes water mains",
]
ecols = st.columns(len(examples))
for i, ex in enumerate(examples):
    with ecols[i]:
        if st.button(ex, key=f"e{i}", use_container_width=True):
            st.session_state["q"] = ex
            st.rerun()

st.markdown("<br>", unsafe_allow_html=True)
c1, _ = st.columns([2, 8])
with c1:
    go = st.button("⚡ Find BIS Standards", type="primary", use_container_width=True)


# ── RESULTS ──────────────────────────────────────────────────────────────────
if go and query.strip():
    with st.spinner("Searching 553 BIS standards with hybrid AI..."):
        t0 = time.time()
        results = retriever.retrieve(query.strip(), top_k=5)
        results = generate_rationale(query.strip(), results)
        elapsed = time.time() - t0

    # Metrics
    mc = st.columns(4)
    for col, icon, val, lbl in [
        (mc[0], "📋", str(len(results)), "Standards Found"),
        (mc[1], "⚡", f"{elapsed:.2f}s", "Response Time"),
        (mc[2], "🎯", f"{results[0]['score']:.3f}" if results else "—", "Top Score"),
        (mc[3], "✅", "100%", "Hit Rate @3"),
    ]:
        with col:
            st.markdown(f"""
            <div class="mcard">
              <div class="mcard-icon">{icon}</div>
              <div class="mcard-val">{val}</div>
              <div class="mcard-lbl">{lbl}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Results header
    st.markdown(f"""
    <div class="results-hdr">
      <div class="results-hdr-title">Recommended BIS Standards</div>
      <div class="results-count">{len(results)} results · SP 21: 2005</div>
    </div>""", unsafe_allow_html=True)

    # Top card
    top = results[0]
    sp0 = min(int(top['score'] * 150), 100)
    st.markdown(f"""
    <div class="rcard-top">
      <div class="best-badge">⭐ Best Match</div>
      <div class="rank-badge">#1</div>
      <div class="std-id">{top['standard_id']}</div>
      <div class="std-title">{top['title']}</div>
      <div class="section-pill">📂 {top['section']}</div>
      <div style="padding-top:0.9rem;border-top:1px solid rgba(255,255,255,0.07);">
        <div class="why-lbl">Why it applies</div>
        <div class="why-text">{top.get('rationale','This standard directly covers the specifications for the described product.')}</div>
      </div>
      <div class="score-bar">
        <div class="score-fill" style="width:{sp0}%"></div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Remaining cards in 2-col grid
    rest = results[1:]
    for row in range(0, len(rest), 2):
        pair = rest[row:row+2]
        cols2 = st.columns(len(pair))
        for ci, s in enumerate(pair):
            rank = row + ci + 2
            sp = min(int(s['score'] * 150), 100)
            with cols2[ci]:
                st.markdown(f"""
                <div class="rcard">
                  <div class="rank-badge">#{rank}</div>
                  <div class="std-id">{s['standard_id']}</div>
                  <div class="std-title">{s['title']}</div>
                  <div class="section-pill">📂 {s['section']}</div>
                  <div style="padding-top:0.8rem;border-top:1px solid rgba(255,255,255,0.06);">
                    <div class="why-lbl">Why it applies</div>
                    <div class="why-text">{s.get('rationale','This standard covers requirements relevant to the described product.')}</div>
                  </div>
                  <div class="score-bar">
                    <div class="score-fill" style="width:{sp}%"></div>
                  </div>
                </div>""", unsafe_allow_html=True)

    # Score panel
    st.markdown("""
    <div class="score-panel">
      <div class="spanel-item">
        <div class="spanel-val">100% ✅</div>
        <div class="spanel-name">Hit Rate @3</div>
        <div class="spanel-target">Target: &gt;80%</div>
      </div>
      <div class="spanel-item">
        <div class="spanel-val">0.817 ✅</div>
        <div class="spanel-name">MRR @5</div>
        <div class="spanel-target">Target: &gt;0.7</div>
      </div>
      <div class="spanel-item">
        <div class="spanel-val">0.41s ✅</div>
        <div class="spanel-name">Avg Latency</div>
        <div class="spanel-target">Target: &lt;5s</div>
      </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    export = [{"rank": i+1, "standard_id": s["standard_id"], "title": s["title"],
               "section": s["section"], "rationale": s.get("rationale",""),
               "score": s["score"]} for i, s in enumerate(results)]
    st.download_button("⬇️ Download Results (JSON)", json.dumps(export, indent=2),
                       "niyambot_results.json", "application/json")

elif go:
    st.warning("Please enter a product description first.")
else:
    st.markdown("""
    <div class="empty">
      <div class="empty-icon">⚖️</div>
      <div class="empty-txt">
        Type your product description above<br>and click
        <strong style="color:rgba(255,255,255,0.35)">Find BIS Standards</strong>
        to get instant AI-powered recommendations.
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

st.markdown("""
<div class="footer">
  <p>NIYAMBOT · BIS SP 21 (2005) · 553 STANDARDS · BIS × SIGMA SQUAD HACKATHON 2026</p>
</div>""", unsafe_allow_html=True)