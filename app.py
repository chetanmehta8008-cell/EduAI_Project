import streamlit as st
import os
import json
from multi_agent import run_education_system
from database import get_all_topics, get_note, delete_topic

st.set_page_config(
    page_title="EduAI – Concept Visualization",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

.stApp { background: #0a0d14; color: #e8eaf0; }

[data-testid="stSidebar"] {
    background: #0f1320 !important;
    border-right: 1px solid #1e2535;
}

.hero-header {
    background: linear-gradient(135deg, #0d1b3e 0%, #0a2a4a 50%, #061a2e 100%);
    border: 1px solid #1a3a5c;
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%; right: -10%;
    width: 400px; height: 400px;
    background: radial-gradient(circle, rgba(56,182,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-badge {
    display: inline-block;
    background: rgba(56,182,255,0.12);
    color: #38b6ff;
    border: 1px solid rgba(56,182,255,0.3);
    border-radius: 100px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 0.2rem 0.8rem;
    margin-bottom: 0.8rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.4rem;
    font-weight: 800;
    color: #ffffff;
    margin: 0;
    letter-spacing: -0.02em;
}
.hero-sub {
    color: #7a9bb5;
    font-size: 0.95rem;
    margin-top: 0.4rem;
    font-weight: 300;
}
.stat-row { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-top: 1rem; }
.stat-pill {
    background: rgba(56,182,255,0.07);
    border: 1px solid rgba(56,182,255,0.18);
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    color: #7ab8d8;
    font-weight: 500;
}

.flashcard {
    background: #111827;
    border: 1px solid #1e2d45;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    position: relative;
    overflow: hidden;
    margin-bottom: 1rem;
    transition: border-color 0.2s ease;
}
.flashcard::after {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px; height: 100%;
    background: linear-gradient(180deg, #38b6ff, #6c63ff);
    border-radius: 4px 0 0 4px;
}
.flashcard-q {
    font-family: 'Syne', sans-serif;
    font-size: 0.95rem;
    font-weight: 600;
    color: #c8d8e8;
    margin-bottom: 0.8rem;
}
.flashcard-a {
    font-size: 0.875rem;
    color: #8a9bb0;
    line-height: 1.6;
    margin-bottom: 0.8rem;
}
.flashcard-hint {
    display: inline-block;
    font-size: 0.72rem;
    color: #38b6ff;
    background: rgba(56,182,255,0.08);
    border-radius: 6px;
    padding: 0.15rem 0.6rem;
    font-weight: 500;
}
.card-number {
    position: absolute;
    top: 1rem; right: 1.2rem;
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 800;
    color: rgba(56,182,255,0.08);
}

.notes-container {
    background: #0d1520;
    border: 1px solid #1a2d42;
    border-radius: 14px;
    padding: 2rem;
    line-height: 1.8;
}
.img-frame {
    border: 1px solid #1e2d45;
    border-radius: 12px;
    overflow: hidden;
    margin-bottom: 0.5rem;
}
.img-caption {
    font-size: 0.8rem;
    color: #5a7a9a;
    text-align: center;
    margin-bottom: 1rem;
    font-style: italic;
}
hr { border-color: #1e2535 !important; }
</style>
""", unsafe_allow_html=True)

# Session state
if "result" not in st.session_state:
    st.session_state.result = None
if "current_topic" not in st.session_state:
    st.session_state.current_topic = None
if "current_difficulty" not in st.session_state:
    st.session_state.current_difficulty = "Intermediate"

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='padding:0.5rem 0 1rem'>
        <div style='font-family:Syne,sans-serif;font-size:1.4rem;font-weight:800;color:#fff'>🎓 EduAI</div>
        <div style='font-size:0.75rem;color:#4a6a8a;margin-top:0.2rem'>Concept Visualization System</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### ⚙️ Settings")
    difficulty = st.selectbox("Difficulty Level", ["Beginner", "Intermediate", "Advanced"], index=1)

    st.markdown("---")
    st.markdown("### 📚 History")
    all_topics = get_all_topics()

    if all_topics:
        for row in all_topics:
            topic_name, diff, created = row
            short = topic_name[:28] + "…" if len(topic_name) > 28 else topic_name
            col_a, col_b = st.columns([5, 1])
            with col_a:
                if st.button(f"📖 {short}", key=f"load_{topic_name}", use_container_width=True):
                    content, flashcards, image_paths, d = get_note(topic_name)
                    st.session_state.result = (content, flashcards, image_paths)
                    st.session_state.current_topic = topic_name
                    st.session_state.current_difficulty = d or difficulty
                    st.rerun()
            with col_b:
                if st.button("🗑", key=f"del_{topic_name}"):
                    delete_topic(topic_name)
                    if st.session_state.current_topic == topic_name:
                        st.session_state.result = None
                        st.session_state.current_topic = None
                    st.rerun()
            st.caption(f"{diff or '—'} · {str(created)[:10] if created else ''}")
    else:
        st.caption("No saved topics yet.")

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.72rem;color:#3a5a7a;text-align:center'>
        Gemini 2.5 Flash + Imagen 3<br>CrewAI Multi-Agent Pipeline
    </div>
    """, unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-badge">Multi-Agent · Multimodal · GenAI</div>
    <div class="hero-title">EduAI Concept Visualizer</div>
    <div class="hero-sub">
        Enter any topic → Researcher + Writer + Flashcard Agent →
        Imagen generates concept visuals → Learn faster.
    </div>
    <div class="stat-row">
        <span class="stat-pill">🤖 3 Specialized Agents</span>
        <span class="stat-pill">🖼️ AI Image Generation</span>
        <span class="stat-pill">🃏 Auto Flashcards</span>
        <span class="stat-pill">💾 Persistent History</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── INPUT ─────────────────────────────────────────────────────────────────────
user_input = st.chat_input("Enter a topic… e.g. 'Gradient Descent', 'Photosynthesis', 'TCP/IP'")

if user_input:
    st.session_state.current_topic = user_input.strip()
    st.session_state.current_difficulty = difficulty
    with st.spinner("🤖 Agents researching, writing, creating flashcards & generating images…"):
        content, flashcards, image_paths = run_education_system(
            st.session_state.current_topic, difficulty
        )
        st.session_state.result = (content, flashcards, image_paths)
    st.rerun()

# ── RESULTS ───────────────────────────────────────────────────────────────────
if st.session_state.result:
    content, flashcards, image_paths = st.session_state.result
    topic = st.session_state.current_topic
    diff = st.session_state.current_difficulty

    col_title, col_diff = st.columns([7, 1])
    with col_title:
        st.markdown(f"## 📘 {topic}")
    with col_diff:
        color = {"Beginner": "#22c55e", "Intermediate": "#f59e0b", "Advanced": "#ef4444"}.get(diff, "#38b6ff")
        st.markdown(
            f"<div style='background:{color}22;border:1px solid {color}55;color:{color};"
            f"border-radius:100px;padding:0.25rem 0.8rem;font-size:0.75rem;font-weight:600;"
            f"text-align:center;margin-top:0.6rem'>{diff}</div>",
            unsafe_allow_html=True
        )

    tab_notes, tab_flashcards, tab_images = st.tabs([
        "📝 Study Notes",
        f"🃏 Flashcards ({len(flashcards)})",
        f"🖼️ Visual Gallery ({len(image_paths)})"
    ])

    # TAB 1 — NOTES
    with tab_notes:
        if content:
            st.markdown(f'<div class="notes-container">{content}</div>', unsafe_allow_html=True)
        else:
            st.warning("No notes generated.")

    # TAB 2 — FLASHCARDS
    with tab_flashcards:
        if flashcards:
            st.markdown(f"**{len(flashcards)} flashcards** for active recall:")
            pairs = [flashcards[i:i+2] for i in range(0, len(flashcards), 2)]
            for pair in pairs:
                cols = st.columns(len(pair))
                for col, card in zip(cols, pair):
                    idx = flashcards.index(card) + 1
                    with col:
                        st.markdown(f"""
                        <div class="flashcard">
                            <div class="card-number">{idx:02d}</div>
                            <div class="flashcard-q">❓ {card.get('question', '')}</div>
                            <div class="flashcard-a">{card.get('answer', '')}</div>
                            <span class="flashcard-hint">💡 {card.get('hint', '')}</span>
                        </div>
                        """, unsafe_allow_html=True)
            st.download_button(
                "⬇️ Download Flashcards (JSON)",
                data=json.dumps(flashcards, indent=2),
                file_name=f"flashcards_{topic[:30].replace(' ', '_')}.json",
                mime="application/json"
            )
        else:
            st.info("No flashcards generated.")

    # TAB 3 — IMAGES
    with tab_images:
        valid_paths = [p for p in image_paths if p and os.path.exists(p)]
        if valid_paths:
            st.markdown("### 🗺️ Concept Overview")
            st.markdown('<div class="img-frame">', unsafe_allow_html=True)
            st.image(valid_paths[0], use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="img-caption">AI-generated concept map: {topic}</div>', unsafe_allow_html=True)

            rest = valid_paths[1:]
            if rest:
                st.markdown("### 🃏 Flashcard Visuals")
                for i in range(0, len(rest), 2):
                    row_imgs = rest[i:i+2]
                    img_cols = st.columns(len(row_imgs))
                    for ic_idx, (ic, img_path) in enumerate(zip(img_cols, row_imgs)):
                        with ic:
                            if os.path.exists(img_path):
                                st.markdown('<div class="img-frame">', unsafe_allow_html=True)
                                st.image(img_path, use_container_width=True)
                                st.markdown('</div>', unsafe_allow_html=True)
                                fc_idx = i + ic_idx
                                if fc_idx < len(flashcards):
                                    q = flashcards[fc_idx].get("question", "")
                                    st.markdown(f'<div class="img-caption">{q}</div>', unsafe_allow_html=True)

            st.markdown("---")
            dl_cols = st.columns(min(len(valid_paths), 4))
            for di, (dcol, path) in enumerate(zip(dl_cols, valid_paths)):
                with dcol:
                    with open(path, "rb") as f:
                        img_bytes = f.read()
                    st.download_button(
                        f"⬇️ {'Hero' if di == 0 else f'Card {di}'}",
                        data=img_bytes,
                        file_name=os.path.basename(path),
                        mime="image/png",
                        key=f"dl_img_{di}"
                    )
        else:
            st.info("No images generated — Imagen API may need access or quota. Notes & flashcards above are complete.")

else:
    st.markdown("""
    <div style='text-align:center;padding:4rem 2rem;color:#3a5a7a'>
        <div style='font-size:4rem;margin-bottom:1rem'>🎯</div>
        <div style='font-family:Syne,sans-serif;font-size:1.3rem;font-weight:700;color:#5a8ab0;margin-bottom:0.5rem'>
            Ready to Learn
        </div>
        <div style='font-size:0.9rem;color:#2a4a6a'>
            Type any concept above — from Quantum Computing to Renaissance Art.<br>
            Three AI agents + image generation will build your complete study kit.
        </div>
        <div style='margin-top:2rem;display:flex;gap:1rem;justify-content:center;flex-wrap:wrap'>
            <span style='background:#0d1b30;border:1px solid #1a3a5c;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#4a8ab0'>💡 Gradient Descent</span>
            <span style='background:#0d1b30;border:1px solid #1a3a5c;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#4a8ab0'>🧬 DNA Replication</span>
            <span style='background:#0d1b30;border:1px solid #1a3a5c;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#4a8ab0'>⚡ Ohm's Law</span>
            <span style='background:#0d1b30;border:1px solid #1a3a5c;border-radius:8px;padding:0.5rem 1rem;font-size:0.8rem;color:#4a8ab0'>🌍 French Revolution</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")
st.markdown("""
<div style='text-align:center;font-size:0.72rem;color:#2a4a6a'>
    © 2026 EduAI · Multimodal GenAI Education System · CrewAI · Gemini 2.5 Flash · Imagen 3 · Streamlit
</div>
""", unsafe_allow_html=True)