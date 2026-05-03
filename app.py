"""
NiyamBot - app.py
Streamlit web interface.
Run: streamlit run app.py
"""

import streamlit as st
import time, sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

st.set_page_config(page_title="NiyamBot", page_icon="⚖️", layout="wide")

st.markdown("""
<style>
.hero {
    background: linear-gradient(135deg, #0d47a1, #1565c0);
    color: white; padding: 2rem; border-radius: 14px;
    text-align: center; margin-bottom: 2rem;
}
.card {
    background: #f0f4ff;
    border-left: 5px solid #1565c0;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin: 0.8rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.07);
}
.tag {
    background: #fff3e0; color: #e65100;
    padding: 2px 10px; border-radius: 20px; font-size: 0.75rem;
}
.score {
    background: #e3f2fd; color: #1565c0;
    padding: 2px 10px; border-radius: 20px; font-size: 0.8rem; font-weight:600;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
  <h1>⚖️ NiyamBot</h1>
  <p>BIS Standards Recommendation Engine for Indian Building Materials</p>
  <small>SP 21: 2005 · Hybrid RAG · Built for Indian MSEs</small>
</div>
""", unsafe_allow_html=True)


@st.cache_resource(show_spinner="Loading NiyamBot... (first load takes ~30 seconds)")
def load_engine():
    from retriever import NiyamRetriever
    from generator import generate_rationale
    return NiyamRetriever(), generate_rationale


retriever, generate_rationale = load_engine()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    top_k      = st.slider("Standards to return", 3, 5, 5)
    show_score = st.toggle("Show scores", True)
    show_body  = st.toggle("Show standard summary", False)

    st.markdown("---")
    st.markdown("### 💡 Try These")
    examples = [
        "33 Grade Ordinary Portland Cement manufacturing",
        "Coarse and fine aggregates for structural concrete",
        "Precast concrete pipes for water mains",
        "Lightweight hollow concrete masonry blocks",
        "White Portland cement for decorative use",
        "Portland slag cement chemical requirements",
        "Supersulphated cement for marine conditions",
        "Masonry cement for mortar, not structural",
    ]
    for ex in examples:
        if st.button(ex, use_container_width=True):
            st.session_state["q"] = ex

# Query input
query = st.text_area(
    "📝 Describe your product:",
    value=st.session_state.get("q", ""),
    height=110,
    placeholder="e.g. We manufacture Portland Pozzolana Cement using calcined clay for construction...",
)

go = st.button("🔍 Find BIS Standards", type="primary")

if go and query.strip():
    with st.spinner("Searching..."):
        t0      = time.time()
        results = retriever.retrieve(query.strip(), top_k=top_k)
        results = generate_rationale(query.strip(), results)
        elapsed = time.time() - t0

    st.markdown("---")
    c1, c2, c3 = st.columns(3)
    c1.metric("Standards Found", len(results))
    c2.metric("Response Time",   f"{elapsed:.2f}s")
    c3.metric("Top Score",       f"{results[0]['score']:.3f}" if results else "—")

    st.markdown("### 📋 Recommended Standards")
    colors = ["#1565c0", "#0288d1", "#00838f", "#558b2f", "#6a1b9a"]

    for i, s in enumerate(results):
        color = colors[i % len(colors)]
        body_html = ""
        if show_body:
            body_html = f"<details><summary style='color:{color};cursor:pointer;margin-top:6px'>📄 View Summary</summary><pre style='font-size:0.78rem;white-space:pre-wrap;color:#444;'>{s.get('body','')[:600]}...</pre></details>"

        st.markdown(f"""
        <div class="card">
          <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="background:{color};color:white;border-radius:50%;
                         width:28px;height:28px;display:inline-flex;
                         align-items:center;justify-content:center;
                         font-weight:bold;font-size:0.85rem;">#{i+1}</span>
            <strong style="color:#1a237e;font-size:1.05rem;">{s['standard_id']}</strong>
            {"<span class='score'>Score: " + str(s['score']) + "</span>" if show_score else ""}
            <span class='tag'>{s['section']}</span>
          </div>
          <div style="color:#444;font-size:0.92rem;margin-bottom:4px;"><em>{s['title']}</em></div>
          <div style="color:#555;font-size:0.88rem;line-height:1.5;">💡 {s.get('rationale','')}</div>
          {body_html}
        </div>
        """, unsafe_allow_html=True)

    # Download
    st.markdown("---")
    import json
    export = [{"rank": i+1, "standard_id": s["standard_id"],
               "title": s["title"], "rationale": s.get("rationale",""),
               "score": s["score"]} for i, s in enumerate(results)]
    st.download_button("⬇️ Download Results (JSON)", json.dumps(export, indent=2),
                       "niyambot_results.json", "application/json")

elif go:
    st.warning("Please type a product description first.")

st.markdown("""
<hr>
<p style='text-align:center;color:#aaa;font-size:0.78rem;'>
NiyamBot · BIS × Sigma Squad Hackathon 2026 · Helping Indian MSEs navigate compliance
</p>
""", unsafe_allow_html=True)