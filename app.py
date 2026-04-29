import streamlit as st
import pandas as pd
from supabase import create_client, Client
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Family Vault", page_icon="🏦", layout="wide")

# ---------------- ELITE UI SYSTEM ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;900&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* BACKGROUND */
.stApp {
    background: radial-gradient(circle at 20% 20%, #0f172a, #020617 80%);
    color: #e2e8f0;
}

/* NOISE LAYER */
.stApp::before {
    content: "";
    position: fixed;
    inset: 0;
    background: url("https://grainy-gradients.vercel.app/noise.svg");
    opacity: 0.04;
    pointer-events: none;
}

/* HEADINGS */
h1 {
    font-size: 2.6rem !important;
    font-weight: 800;
    background: linear-gradient(90deg,#22d3ee,#a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* GLASS CARD */
.glass {
    background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.01));
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 22px;
    backdrop-filter: blur(18px);
    transition: 0.4s ease;
}

.glass:hover {
    transform: translateY(-8px);
    box-shadow: 0 20px 60px rgba(168,85,247,0.25);
}

/* METRICS */
div[data-testid="stMetricValue"] {
    font-size: 3rem;
    font-weight: 900;
    background: linear-gradient(90deg,#22d3ee,#a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(135deg,#6366f1,#a855f7);
    border-radius: 14px;
    border: none;
    font-weight: 600;
    transition: 0.3s;
}

.stButton>button:hover {
    transform: translateY(-3px);
    box-shadow: 0 12px 40px rgba(168,85,247,0.5);
}

/* INPUT */
input, textarea, select {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: white !important;
}

/* ANIMATION */
@keyframes fadeUp {
    from {opacity:0; transform:translateY(30px);}
    to {opacity:1; transform:translateY(0);}
}

section.main > div {
    animation: fadeUp 0.6s ease;
}

/* CLEAN */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SUPABASE ----------------
@st.cache_resource
def init_connection():
    url = st.secrets["supabase"]["url"]
    key = st.secrets["supabase"]["key"]
    return create_client(url, key)

supabase: Client = init_connection()

# ---------------- FUNCTIONS ----------------
def get_assets():
    response = supabase.table('assets').select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(response.data)

def add_asset(name, category, institution, value, notes, document_url):
    supabase.table('assets').insert({
        "name": name,
        "category": category,
        "institution": institution,
        "value": float(value),
        "notes": notes,
        "document_url": document_url
    }).execute()

def delete_asset(asset_id):
    supabase.table('assets').delete().eq('id', asset_id).execute()

def upload_file(file):
    file_ext = file.name.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_ext}"
    supabase.storage.from_("vault-documents").upload(file_name, file.getvalue())
    return supabase.storage.from_("vault-documents").get_public_url(file_name)

# ---------------- AUTH ----------------
FAMILY_PASSWORD = "familyvault"

if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='glass' style='max-width:400px;margin:120px auto;text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h2>🔐 Family Vault</h2>", unsafe_allow_html=True)
    pwd = st.text_input("Passcode", type="password")
    if st.button("Enter"):
        if pwd == FAMILY_PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong passcode")
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ---------------- HEADER ----------------
col1, col2 = st.columns([4,1])

with col1:
    st.markdown("<h1>Family Financial Command Center</h1>", unsafe_allow_html=True)
    st.markdown("<span style='color:#94a3b8;'>Everything. Organized. Accessible. Secure.</span>", unsafe_allow_html=True)

with col2:
    if st.button("🚪 Logout"):
        st.session_state.auth = False
        st.rerun()

st.divider()

# ---------------- MAIN ----------------
try:
    df = get_assets()
except Exception as e:
    st.error("Database connection error. Check if table exists.")
    st.write(e)
    st.stop()

# ---------- METRICS ----------
if not df.empty and 'name' in df.columns:
    total = df['value'].sum()

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### 💰 Net Worth")
        st.metric("", f"₹{total:,.2f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with c2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("### 📦 Assets")
        st.metric("", str(len(df)))
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### 📊 Distribution")
    st.bar_chart(df.groupby('category')['value'].sum())
    st.markdown("</div>", unsafe_allow_html=True)

# ---------- ADD ASSET ----------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("### ➕ Add Asset")

with st.form("form"):
    n = st.text_input("Name")
    c = st.selectbox("Category", ["Bank","FD","Mutual Fund","Stock","Insurance","Property","Locker"])
    i = st.text_input("Institution")
    v = st.number_input("Value", min_value=0.0)
    notes = st.text_area("Notes")
    f = st.file_uploader("Doc")

    if st.form_submit_button("Save"):
        url = upload_file(f) if f else None
        add_asset(n,c,i,v,notes,url)
        st.success("Saved")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------- ASSET CARDS ----------
if not df.empty and 'name' in df.columns:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Your Assets")

    cols = st.columns(3)

    for idx, row in df.iterrows():
        with cols[idx % 3]:
            st.markdown("<div class='glass'>", unsafe_allow_html=True)

            st.markdown(f"""
            <div style="font-weight:600">{row['name']}</div>
            <div style="color:#94a3b8;font-size:0.8rem">
            {row['category']} • {row['institution']}
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"<h3>₹{float(row['value']):,.2f}</h3>", unsafe_allow_html=True)

            b1, b2 = st.columns(2)

            with b1:
                if row.get('document_url') and str(row['document_url']).strip() not in ['None', 'nan', '']:
                    st.markdown(f"<a href='{row['document_url']}' target='_blank'>📄 View</a>", unsafe_allow_html=True)

            with b2:
                if st.button("🗑", key=row['id']):
                    delete_asset(row['id'])
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
