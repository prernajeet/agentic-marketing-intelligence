"""
dashboard/pages/50_ad_copy_writer.py
Generative AI Campaign Copy Writer — powered by the built-in LLM client.
"""

import streamlit as st
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from utils.styling import apply_premium_styling, page_header, section_header, glass_card

st.set_page_config(page_title="AI Campaign Copy Writer", page_icon="✍️", layout="wide")
page_header("✍️", "AI Campaign Copy Writer", "Generate high-converting marketing copy, email campaigns, and ad scripts using generative AI.")

# ── Sidebar settings ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Copy Settings")
    copy_type = st.selectbox("Content Type", [
        "Email Subject Line",
        "Email Body (Win-Back)",
        "SMS Message",
        "Push Notification",
        "Social Media Ad (Facebook/Instagram)",
        "Google Display Ad",
        "Landing Page Headline",
    ])
    tone = st.select_slider("Brand Tone", options=["Formal", "Professional", "Friendly", "Casual", "Playful"], value="Professional")
    urgency = st.select_slider("Urgency Level", options=["None", "Low", "Medium", "High", "Extreme"], value="Medium")
    word_limit = st.slider("Target Word Count", min_value=10, max_value=300, value=80, step=10)
    language = st.selectbox("Language", ["English", "Spanish", "French", "German", "Portuguese"])

# ── Input form ───────────────────────────────────────────────────────────────
section_header("📝", "Campaign Brief", badge="STEP 1")
glass_card("""
<p style='color:#94a3b8; margin:0;'>Fill in the details below to give the AI enough context to generate highly targeted marketing copy.
The more specific you are, the better the output.</p>
""")

col1, col2 = st.columns(2)
with col1:
    brand_name = st.text_input("Brand / Product Name", placeholder="e.g. ShopEasy Premium")
    target_audience = st.text_input("Target Audience", placeholder="e.g. Women aged 25-40 who shop online")
    offer = st.text_input("Offer / Promotion", placeholder="e.g. 20% off first order, free shipping")
with col2:
    pain_point = st.text_area("Customer Pain Point / Need", placeholder="e.g. Busy professionals who don't have time to shop in-store", height=70)
    key_benefit = st.text_area("Key Benefit / USP", placeholder="e.g. Same-day delivery, exclusive members-only deals", height=70)

churn_context = st.checkbox(
    "🎯 Tailor copy for at-risk / churning customers",
    value=True,
    help="AI will frame messaging around re-engagement and win-back strategies."
)

generate_btn = st.button("⚡ Generate Copy", use_container_width=True)

# Initialize session state for copy generation
if "copy_generated" not in st.session_state:
    st.session_state.copy_generated = False
if "copy_result_text" not in st.session_state:
    st.session_state.copy_result_text = ""
if "copy_variation_text" not in st.session_state:
    st.session_state.copy_variation_text = ""
if "copy_prompt" not in st.session_state:
    st.session_state.copy_prompt = ""

# ── Generation ────────────────────────────────────────────────────────────────
if generate_btn:
    if not brand_name or not target_audience:
        st.warning("⚠️ Please fill in at least Brand Name and Target Audience.")
        st.stop()

    churn_context_text = (
        "The customer has not purchased in over 60 days and is at HIGH risk of churning. "
        "The copy must include a re-engagement hook, create urgency, and offer a clear incentive to return."
        if churn_context else ""
    )

    prompt = f"""You are an expert marketing copywriter specializing in high-conversion campaigns for e-commerce brands.

Generate a {copy_type} for the following campaign:
- Brand/Product: {brand_name}
- Target Audience: {target_audience}
- Pain Point / Customer Need: {pain_point or 'Not specified'}
- Key Benefit / USP: {key_benefit or 'Not specified'}
- Offer / Promotion: {offer or 'Not specified'}
- Tone: {tone}
- Urgency: {urgency}
- Language: {language}
- Target Word Count: approximately {word_limit} words
{churn_context_text}

Requirements:
1. Write ONLY the copy — no explanations or meta-commentary.
2. Make it emotionally resonant and action-driven.
3. Include a clear CTA (Call to Action).
4. Optimize for high click-through and conversion rates.
5. Use power words that trigger curiosity and urgency.

Generate the {copy_type} now:"""

    with st.spinner("🤖 Generating copy…"):
        try:
            from llm.gemini_client import GeminiClient
            client = GeminiClient()
            result_text = client.generate(prompt, temperature=0.7)
        except Exception as e:
            result_text = f"[LLM Error: {e}] — Mock copy generated:\n\nDon't miss out, {target_audience}! {brand_name} is offering {offer or 'exclusive deals'} — just for you. Shop now before it's gone! 🛍️"

    st.session_state.copy_result_text = result_text
    st.session_state.copy_prompt = prompt
    st.session_state.copy_variation_text = ""  # reset variation on new generation
    st.session_state.copy_generated = True

if st.session_state.copy_generated:
    result_text = st.session_state.copy_result_text
    prompt = st.session_state.copy_prompt

    section_header("✨", "Generated Copy", badge="AI OUTPUT")
    st.markdown(f"""
    <div class="glass-card" style='border-left: 3px solid #6366f1;'>
        <pre style='white-space: pre-wrap; font-family: Inter, sans-serif; color: #e2e8f0; line-height: 1.8;'>{result_text}</pre>
    </div>
    """, unsafe_allow_html=True)

    # Download buttons
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.download_button(
            "📥 Download as .txt",
            data=result_text,
            file_name=f"campaign_copy_{copy_type.replace(' ', '_').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
        )
    with col_d2:
        st.download_button(
            "📥 Download as .md",
            data=f"# Campaign Copy: {copy_type}\n\n**Brand:** {brand_name}\n**Audience:** {target_audience}\n\n---\n\n{result_text}",
            file_name=f"campaign_copy_{copy_type.replace(' ', '_').lower()}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    # ── A/B Variation ─────────────────────────────────────────────────────────
    with st.expander("🔀 Generate A/B Variation"):
        gen_var_btn = st.button("Generate Alternative Version")
        if gen_var_btn:
            with st.spinner("Creating variation…"):
                variation_prompt = prompt.replace("Generate the", "Generate a DIFFERENT alternative version of the")
                try:
                    from llm.gemini_client import GeminiClient
                    client = GeminiClient()
                    st.session_state.copy_variation_text = client.generate(variation_prompt, temperature=0.9)
                except Exception:
                    st.session_state.copy_variation_text = f"[Variation] Act fast! {offer or 'Exclusive deals'} at {brand_name} — made for people like you. Limited time only. Click here!"
        
        if st.session_state.copy_variation_text:
            st.markdown(f"""
            <div class="glass-card" style='border-left: 3px solid #a855f7;'>
                <pre style='white-space: pre-wrap; font-family: Inter, sans-serif; color: #e2e8f0; line-height: 1.8;'>{st.session_state.copy_variation_text}</pre>
            </div>
            """, unsafe_allow_html=True)

else:
    # Tips section
    section_header("💡", "Copy Writing Tips")
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        glass_card("<h4 style='color:#6366f1;margin-top:0'>🎯 Be Specific</h4><p style='color:#94a3b8'>The more detail you give about your audience and offer, the more personalized and effective the copy will be.</p>")
    with col_t2:
        glass_card("<h4 style='color:#a855f7;margin-top:0'>⚡ Urgency Sells</h4><p style='color:#94a3b8'>High urgency copy with time-limited offers can boost click-through rates by up to 40% for win-back campaigns.</p>")
    with col_t3:
        glass_card("<h4 style='color:#06b6d4;margin-top:0'>🔀 Always A/B Test</h4><p style='color:#94a3b8'>Generate multiple variations and test them against each other. Small wording changes can have outsized conversion impacts.</p>")
