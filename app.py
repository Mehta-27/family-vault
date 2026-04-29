import streamlit as st
import pandas as pd
from supabase import create_client, Client
import uuid

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Family Vault", page_icon="🏦", layout="wide")

# ---------------- CLEAN UI SYSTEM ----------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

/* CENTERED LAYOUT */
.block-container {
    max-width: 1100px;
    padding-top: 2rem;
}

/* BACKGROUND */
.stApp {
    background: #020617;
    color: #e2e8f0;
}

/* GLASS CARD */
.glass {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 18px;
    margin-bottom: 20px;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(135deg,#6366f1,#a855f7);
    border-radius: 10px;
    border: none;
    color: white;
}

/* INPUT */
input, textarea, select {
    background: rgba(255,255,255,0.04) !important;
    border-radius: 8px !important;
    color: white !important;
}

/* REMOVE STREAMLIT CLUTTER */
#MainMenu, footer, header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ---------------- SUPABASE ----------------
@st.cache_resource
def init_connection():
    return create_client(
        st.secrets["supabase"]["url"],
        st.secrets["supabase"]["key"]
    )

supabase: Client = init_connection()

# ---------------- FUNCTIONS ----------------
def get_assets():
    res = supabase.table('assets').select("*").order("created_at", desc=True).execute()
    return pd.DataFrame(res.data)

def add_asset(n,c,i,v,notes,url):
    supabase.table('assets').insert({
        "name": n,
        "category": c,
        "institution": i,
        "value": float(v),
        "notes": notes,
        "document_url": url
    }).execute()

def delete_asset(id):
    supabase.table('assets').delete().eq('id', id).execute()

def upload_file(file):
    name = f"{uuid.uuid4()}.{file.name.split('.')[-1]}"
    supabase.storage.from_("vault-documents").upload(name, file.getvalue())
    return supabase.storage.from_("vault-documents").get_public_url(name)

# ---------------- AUTH ----------------
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.markdown("<div class='glass' style='max-width:400px;margin:120px auto;text-align:center;'>", unsafe_allow_html=True)
    st.markdown("## 🔐 Family Vault")
    email = st.text_input("Email", placeholder="admin@family.com")
    password = st.text_input("Password", type="password")
    if st.button("Secure Login"):
        if email and password:
            try:
                # Attempt to authenticate with Supabase
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                if res.user:
                    st.session_state.auth = True
                    st.rerun()
            except Exception as e:
                # Provide generic error for security
                st.error("Invalid email or password.")
        else:
            st.warning("Please enter your email and password.")
    st.stop()

# ---------------- HEADER ----------------
c1, c2 = st.columns([6,1])

with c1:
    st.markdown("## Family Financial Command Center")
    st.caption("Everything organized. Zero confusion.")

with c2:
    if st.button("Logout"):
        st.session_state.auth = False
        st.rerun()

st.divider()

# ---------------- DATA ----------------
try:
    df = get_assets()
except Exception as e:
    st.error("Database connection error. Check if table exists.")
    df = pd.DataFrame()

# ---------------- DASHBOARD ----------------
if not df.empty and 'value' in df.columns:
    total = df['value'].sum()

    m1, m2 = st.columns(2)

    with m1:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("**Net Worth**")
        st.markdown(f"### ₹{total:,.0f}")
        st.markdown("</div>", unsafe_allow_html=True)

    with m2:
        st.markdown("<div class='glass'>", unsafe_allow_html=True)
        st.markdown("**Assets**")
        st.markdown(f"### {len(df)}")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.markdown("### Distribution")
    st.bar_chart(df.groupby('category')['value'].sum())
    st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("No assets yet.")

# ---------------- ADD ASSET ----------------
st.markdown("<div class='glass'>", unsafe_allow_html=True)
st.markdown("### Add Asset")

with st.form("f"):
    n = st.text_input("Name")
    c = st.selectbox("Category", ["Bank","FD","Mutual Fund","Stock","Insurance","Property","Locker"])
    i = st.text_input("Institution")
    v = st.number_input("Value", min_value=0.0)
    notes = st.text_area("Notes")
    f = st.file_uploader("Document")

    if st.form_submit_button("Save"):
        url = upload_file(f) if f else None
        add_asset(n,c,i,v,notes,url)
        st.success("Saved")
        st.rerun()

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- ASSETS ----------------
if not df.empty and 'name' in df.columns:
    st.markdown("### Your Assets")

    cols = st.columns(3)

    for i, row in df.iterrows():
        with cols[i % 3]:

            st.markdown("<div class='glass'>", unsafe_allow_html=True)

            st.markdown(f"""
            <b>{row['name']}</b><br>
            <span style="color:#94a3b8;font-size:0.8rem;">
            {row['category']} • {row['institution']}
            </span>
            """, unsafe_allow_html=True)

            st.markdown(f"### ₹{float(row['value']):,.0f}")

            b1, b2 = st.columns(2)

            with b1:
                if row.get("document_url"):
                    st.markdown(f"<a href='{row['document_url']}' target='_blank'>View</a>", unsafe_allow_html=True)

            with b2:
                if st.button("Delete", key=row['id']):
                    delete_asset(row['id'])
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
