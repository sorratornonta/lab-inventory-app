import streamlit as st
import pandas as pd
from supabase import create_client
from datetime import datetime
import uuid
from PIL import Image
import base64
from io import BytesIO
from collections import defaultdict
from html import escape


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(
    page_title="Lab Inventory",
    page_icon="🧰",
    layout="wide"
)


# -----------------------------
# Styling
# -----------------------------
st.markdown("""
<style>
    /* =============================
       GLOBAL THEME
    ============================= */
    .stApp {
        background: #f5f7fb !important;
        color: #0f172a !important;
    }

    header[data-testid="stHeader"] {
    background: transparent !important;
    height: 0rem !important;
    }

div[data-testid="stToolbar"] {
    display: none !important;
    }
    .block-container {
        max-width: 1320px;
        padding-top: 2.2rem !important;
        padding-bottom: 3rem;
    }

    html, body, [class*="css"] {
        font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", sans-serif;
    }

    h1, h2, h3, h4, h5, h6,
    p, span, label, div {
        color: #0f172a !important;
    }

    [data-testid="stCaptionContainer"] p {
        color: #64748b !important;
    }

    /* =============================
       HEADER
    ============================= */
    .app-shell {
        background: #ffffff !important;
        border: 1px solid #d8e0ec;
        border-radius: 22px;
        padding: 1.15rem 1.35rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.06);
        margin-top: 0.4rem;
        margin-bottom: 1rem;
        overflow: visible !important;
    }

    .app-brand-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
    }

    .brand-left {
        display: flex;
        align-items: center;
        gap: 0.9rem;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        background: #2563eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        color: #ffffff !important;
        box-shadow: 0 8px 18px rgba(37, 99, 235, 0.24);
    }

    .brand-title {
        font-size: 1.45rem;
        font-weight: 900;
        color: #0f172a !important;
        line-height: 1.1;
    }

    .brand-subtitle {
        color: #64748b !important;
        font-size: 0.92rem;
        margin-top: 0.2rem;
    }

    .brand-badge {
        padding: 0.42rem 0.75rem;
        border-radius: 999px;
        background: #eff6ff !important;
        border: 1px solid #bfdbfe;
        color: #1d4ed8 !important;
        font-weight: 750;
        font-size: 0.82rem;
        white-space: nowrap;
    }

    /* =============================
       NAVIGATION
    ============================= */
    .nav-wrapper {
        background: #ffffff !important;
        border: 1px solid #d8e0ec;
        border-radius: 18px;
        padding: 0.45rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.045);
    }

    div[data-testid="stButton"] > button {
        border-radius: 12px !important;
        border: 1px solid #d8e0ec !important;
        background: #ffffff !important;
        color: #0f172a !important;
        font-weight: 750 !important;
        min-height: 2.6rem;
        box-shadow: none !important;
        transition: 0.12s ease-in-out;
    }

    div[data-testid="stButton"] > button p {
        color: #0f172a !important;
        font-weight: 750 !important;
    }

    div[data-testid="stButton"] > button:hover {
        background: #f1f5f9 !important;
        border-color: #94a3b8 !important;
        transform: translateY(-1px);
    }

    button[kind="primary"] {
        background: #2563eb !important;
        border-color: #2563eb !important;
        color: #ffffff !important;
        box-shadow: 0 8px 16px rgba(37, 99, 235, 0.18) !important;
    }

    button[kind="primary"] p,
    button[kind="primary"] span,
    button[kind="primary"] div {
        color: #ffffff !important;
    }

    /* =============================
       PAGE HEADER
    ============================= */
    .page-hero {
        background: #ffffff !important;
        border: 1px solid #d8e0ec;
        border-radius: 22px;
        padding: 1.2rem 1.35rem;
        margin-bottom: 1.1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
    }

    .page-title {
        font-size: 1.8rem;
        font-weight: 900;
        color: #0f172a !important;
        margin-bottom: 0.25rem;
        letter-spacing: -0.03em;
    }

    .page-desc {
        color: #64748b !important;
        font-size: 0.98rem;
    }

    /* =============================
       STREAMLIT CONTAINERS / CARDS
    ============================= */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background: #ffffff !important;
        border: 1px solid #d8e0ec !important;
        border-radius: 20px !important;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.045) !important;
    }

    div[data-testid="stVerticalBlockBorderWrapper"] * {
        color: #0f172a !important;
    }

    /* =============================
       METRIC CARDS
    ============================= */
    div[data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1px solid #d8e0ec !important;
        border-radius: 20px !important;
        padding: 1rem 1.1rem !important;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.055) !important;
    }

    div[data-testid="stMetric"] label,
    div[data-testid="stMetric"] label p {
        color: #475569 !important;
        font-size: 0.86rem !important;
        font-weight: 800 !important;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }

    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] div {
        color: #0f172a !important;
        font-size: 2rem !important;
        font-weight: 900 !important;
    }

    /* =============================
       INPUTS / DROPDOWNS
    ============================= */
    input, textarea {
        color: #0f172a !important;
        background: #ffffff !important;
    }

    div[data-baseweb="input"],
    div[data-baseweb="textarea"],
    div[data-baseweb="select"] {
        background: #ffffff !important;
        border: 1px solid #d8e0ec !important;
        border-radius: 12px !important;
        color: #0f172a !important;
    }

    div[data-baseweb="input"] *,
    div[data-baseweb="textarea"] *,
    div[data-baseweb="select"] * {
        color: #0f172a !important;
        background: transparent !important;
    }

    ul[role="listbox"],
    li[role="option"] {
        background: #ffffff !important;
        color: #0f172a !important;
    }

    li[role="option"] *,
    ul[role="listbox"] * {
        color: #0f172a !important;
    }

    span[data-baseweb="tag"] {
        background: #dbeafe !important;
        color: #0f172a !important;
        border-radius: 999px !important;
    }

    span[data-baseweb="tag"] * {
        color: #0f172a !important;
    }

    /* =============================
       PILLS
    ============================= */
    .current-label {
        margin-top: 0.7rem;
        margin-bottom: 0.4rem;
        color: #64748b !important;
        font-size: 0.76rem;
        font-weight: 850;
        text-transform: uppercase;
        letter-spacing: 0.045em;
    }

    .holder-badge-row {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem;
        margin-top: 0.15rem;
        margin-bottom: 0.25rem;
        max-width: 100%;
    }

    .holder-badge {
        display: inline-flex;
        align-items: center;
        padding: 0.34rem 0.68rem;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 850;
        border: 1px solid #cbd5e1;
        background: #f8fafc !important;
        color: #0f172a !important;
        white-space: nowrap;
        line-height: 1.2;
    }

    .holder-location {
        background: #ecfdf5 !important;
        border-color: #a7f3d0 !important;
        color: #065f46 !important;
    }

    .holder-person {
        background: #fff7ed !important;
        border-color: #fed7aa !important;
        color: #9a3412 !important;
    }

    .inventory-card-inner {
        padding-top: 0.15rem;
        padding-bottom: 0.35rem;
    }

    .inventory-stat-box {
        display: flex;
        flex-direction: column;
        gap: 0.42rem;
        align-items: flex-start;
        padding-top: 0.25rem;
    }

    .inventory-stat-box .pill-dark {
        margin-top: 0 !important;
    }

    .pill {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border: 1px solid #bfdbfe;
        border-radius: 999px;
        background: #eff6ff !important;
        color: #1e3a8a !important;
        font-size: 0.8rem;
        font-weight: 800;
        margin-right: 0.25rem;
        margin-top: 0.25rem;
    }

    .pill-dark {
        display: inline-block;
        padding: 0.28rem 0.65rem;
        border: 1px solid #cbd5e1;
        border-radius: 999px;
        background: #f1f5f9 !important;
        color: #0f172a !important;
        font-size: 0.8rem;
        font-weight: 800;
        margin-right: 0.25rem;
        margin-top: 0.25rem;
    }

    .status-available {
        background: #ecfdf5 !important;
        border-color: #a7f3d0 !important;
        color: #065f46 !important;
    }

    .status-borrowed {
        background: #fff7ed !important;
        border-color: #fed7aa !important;
        color: #9a3412 !important;
    }

    /* =============================
       GROUP CARD TEXT
    ============================= */
    .group-title {
        font-weight: 900;
        font-size: 1.08rem;
        margin-bottom: 0.15rem;
        color: #0f172a !important;
        line-height: 1.25;
    }

    .group-subtitle {
        color: #64748b !important;
        font-size: 0.88rem;
        margin-bottom: 0.45rem;
        font-weight: 650;
    }

    .selection-box {
        padding: 1.1rem;
        border: 1px solid #d8e0ec;
        border-radius: 20px;
        background: #ffffff !important;
        margin-top: 0.9rem;
        margin-bottom: 1rem;
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.045);
    }

    .selection-box * {
        color: #0f172a !important;
    }

    .location-header {
        padding: 0.6rem 0.8rem;
        border-radius: 14px;
        background: #eff6ff !important;
        border: 1px solid #bfdbfe;
        margin-top: 0.8rem;
        margin-bottom: 0.6rem;
        font-weight: 900;
        color: #1e3a8a !important;
    }

    .location-section-title {
    margin-top: 0.8rem;
    margin-bottom: 0.8rem;
    padding: 0.75rem 0.95rem;
    border-radius: 16px;
    background: #eff6ff !important;
    border: 1px solid #bfdbfe;
    color: #1e3a8a !important;
    font-size: 1.08rem;
    font-weight: 900;
    }

    .location-item-card {
        margin-bottom: 0.55rem;
    }

    .location-meta {
        color: #64748b !important;
        font-size: 0.86rem;
        font-weight: 700;
        margin-top: 0.15rem;
    }

    /* =============================
       CUSTOM HTML TABLE
    ============================= */
    .clean-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
        background: #ffffff;
        border: 1px solid #d8e0ec;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 6px 18px rgba(15, 23, 42, 0.045);
        margin-top: 0.7rem;
        margin-bottom: 1.2rem;
        font-size: 0.93rem;
    }

    .clean-table thead th {
        background: #f1f5f9 !important;
        color: #334155 !important;
        font-weight: 850;
        text-align: left;
        padding: 0.75rem 0.85rem;
        border-bottom: 1px solid #d8e0ec;
        white-space: nowrap;
    }

    .clean-table tbody td {
        background: #ffffff !important;
        color: #0f172a !important;
        padding: 0.72rem 0.85rem;
        border-bottom: 1px solid #edf2f7;
        font-weight: 600;
    }

    .clean-table tbody tr:nth-child(even) td {
        background: #f8fafc !important;
    }

    .clean-table tbody tr:last-child td {
        border-bottom: none;
    }

    .clean-table tbody tr:hover td {
        background: #eff6ff !important;
    }

    .empty-card {
        background: #ffffff;
        border: 1px dashed #cbd5e1;
        border-radius: 16px;
        padding: 1rem;
        color: #64748b !important;
        font-weight: 650;
        margin: 0.8rem 0;
    }

    /* =============================
       EXPANDERS / ALERTS
    ============================= */
    details {
        background: #ffffff !important;
        color: #0f172a !important;
        border-radius: 16px;
        border: 1px solid #d8e0ec;
        padding: 0.4rem 0.7rem;
    }

    details * {
        color: #0f172a !important;
    }

    div[data-testid="stAlert"] {
        border-radius: 16px !important;
    }

    div[data-testid="stAlert"] * {
        color: #0f172a !important;
    }

    hr {
        margin-top: 1rem;
        margin-bottom: 1rem;
        border-color: #d8e0ec;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------
# Supabase connection
# -----------------------------
@st.cache_resource
def get_supabase():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)


supabase = get_supabase()

# -----------------------------
# Simple access gate
# -----------------------------
# -----------------------------
# Simple access gate
# -----------------------------
def login_gate():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return

    st.markdown("""
    <div class="app-shell">
        <div class="app-brand-row">
            <div class="brand-left">
                <div class="brand-icon">🧰</div>
                <div>
                    <div class="brand-title">Lab Inventory System</div>
                    <div class="brand-subtitle">Please enter the lab access code to continue</div>
                </div>
            </div>
            <div class="brand-badge">Private Access</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.1, 1])

    with col2:
        with st.container(border=True):
            st.subheader("Lab Access")

            with st.form("login_form", clear_on_submit=False):
                password = st.text_input(
                    "Access Code",
                    type="password",
                    placeholder="Enter lab access code"
                )

                submitted = st.form_submit_button(
                    "Enter",
                    type="primary",
                    use_container_width=True
                )

            if submitted:
                expected_password = st.secrets.get("LAB_PASSWORD", "").strip()

                if not expected_password:
                    st.error("LAB_PASSWORD is not set in Streamlit Secrets.")
                elif password.strip() == expected_password:
                    st.session_state.logged_in = True
                    st.rerun()
                else:
                    st.error("Incorrect access code")

    st.stop()

login_gate()


# -----------------------------
# Session defaults
# -----------------------------
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

if "checkout_selected_ids" not in st.session_state:
    st.session_state.checkout_selected_ids = []

if "return_selected_ids" not in st.session_state:
    st.session_state.return_selected_ids = []

if "move_selected_ids" not in st.session_state:
    st.session_state.move_selected_ids = []

if "add_form_version" not in st.session_state:
    st.session_state.add_form_version = 0


# -----------------------------
# Data functions
# -----------------------------
def get_people():
    return (
        supabase.table("people")
        .select("*")
        .eq("active", True)
        .order("name")
        .execute()
        .data
        or []
    )


def get_locations():
    return (
        supabase.table("locations")
        .select("*")
        .eq("active", True)
        .order("name")
        .execute()
        .data
        or []
    )


def get_categories(include_inactive=False):
    query = supabase.table("categories").select("*").order("name")
    if not include_inactive:
        query = query.eq("active", True)
    return query.execute().data or []


def get_equipment_types(include_inactive=False):
    query = supabase.table("equipment_types").select("*").order("name")
    if not include_inactive:
        query = query.eq("active", True)
    return query.execute().data or []


def get_assets():
    return (
        supabase.table("assets")
        .select("*, equipment_types(name, category, image_data)")
        .eq("active", True)
        .order("asset_code")
        .execute()
        .data
        or []
    )


def get_available_assets():
    return (
        supabase.table("assets")
        .select("*, equipment_types(name, category, image_data)")
        .eq("active", True)
        .eq("status", "available")
        .order("asset_code")
        .execute()
        .data
        or []
    )

def get_available_assets_by_location(location_id):
    return (
        supabase.table("assets")
        .select("*, equipment_types(name, category, image_data)")
        .eq("active", True)
        .eq("status", "available")
        .eq("current_holder_type", "location")
        .eq("current_holder_id", location_id)
        .order("asset_code")
        .execute()
        .data
        or []
    )



def get_assets_by_holder(holder_type, holder_id):
    return (
        supabase.table("assets")
        .select("*, equipment_types(name, category, image_data)")
        .eq("active", True)
        .eq("current_holder_type", holder_type)
        .eq("current_holder_id", holder_id)
        .order("asset_code")
        .execute()
        .data
        or []
    )

def get_borrowed_assets_by_person(person_id):
    return (
        supabase.table("assets")
        .select("*, equipment_types(name, category, image_data)")
        .eq("active", True)
        .eq("current_holder_type", "person")
        .eq("current_holder_id", person_id)
        .order("asset_code")
        .execute()
        .data
        or []
    )


def get_assets_by_equipment_type(equipment_type_id):
    return (
        supabase.table("assets")
        .select("*")
        .eq("equipment_type_id", equipment_type_id)
        .order("asset_code")
        .execute()
        .data
        or []
    )


def create_movement_log(
    batch_id,
    asset_id,
    action,
    from_holder_type,
    from_holder_id,
    to_holder_type,
    to_holder_id,
    performed_by,
    purpose="",
    note=""
):
    supabase.table("movement_log").insert({
        "batch_id": batch_id,
        "asset_id": asset_id,
        "action": action,
        "from_holder_type": from_holder_type,
        "from_holder_id": from_holder_id,
        "to_holder_type": to_holder_type,
        "to_holder_id": to_holder_id,
        "performed_by": performed_by,
        "purpose": purpose,
        "note": note,
    }).execute()


# -----------------------------
# Helper functions
# -----------------------------
def image_to_base64(uploaded_file, max_size=(700, 700)):
    if uploaded_file is None:
        return None

    image = Image.open(uploaded_file).convert("RGB")
    image.thumbnail(max_size)

    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=80)
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/jpeg;base64,{encoded}"


def render_image(image_data, width=105):
    if image_data:
        st.image(image_data, width=width)
    else:
        st.markdown(
            f"""
            <div style="
                width:{width}px;
                height:78px;
                border:1px dashed #94a3b8;
                border-radius:14px;
                display:flex;
                align-items:center;
                justify-content:center;
                color:#334155;
                font-size:0.8rem;
                font-weight:750;
                background:#f8fafc;
            ">
            No image
            </div>
            """,
            unsafe_allow_html=True
        )


def get_prefix(asset_code):
    if not asset_code:
        return "UNKNOWN"

    parts = asset_code.split("-")

    if len(parts) >= 2 and parts[-1].isdigit():
        return "-".join(parts[:-1])

    return asset_code


def next_asset_codes(prefix, quantity):
    existing_assets = (
        supabase.table("assets")
        .select("asset_code")
        .ilike("asset_code", f"{prefix.upper()}-%")
        .execute()
        .data
        or []
    )

    used_numbers = []

    for item in existing_assets:
        code = item.get("asset_code", "")
        parts = code.split("-")

        if len(parts) >= 2 and parts[-1].isdigit():
            try:
                used_numbers.append(int(parts[-1]))
            except ValueError:
                pass

    start_number = max(used_numbers) + 1 if used_numbers else 1

    return [
        f"{prefix.upper()}-{i:03d}"
        for i in range(start_number, start_number + int(quantity))
    ]


def holder_name(holder_type, holder_id, people_dict, location_dict):
    if holder_type == "person":
        return people_dict.get(holder_id, f"Person {holder_id}")
    if holder_type == "location":
        return location_dict.get(holder_id, f"Location {holder_id}")
    return "-"


def holder_name_from_asset(asset, people_dict, location_dict):
    return holder_name(
        asset.get("current_holder_type"),
        asset.get("current_holder_id"),
        people_dict,
        location_dict
    )

def group_assets_by_equipment_name(assets):
    groups = defaultdict(list)

    for asset in assets:
        eq = asset.get("equipment_types") or {}

        equipment_name = (eq.get("name") or "Unnamed Equipment").strip()
        category = (eq.get("category") or "No category").strip()

        # Normalize for grouping:
        # Same name + same category will be grouped together,
        # even if owner, prefix, or equipment_type_id are different.
        group_name = equipment_name.lower()
        group_category = category.lower()

        key = (group_name, group_category, equipment_name, category)
        groups[key].append(asset)

    return sorted(
        groups.items(),
        key=lambda item: (item[0][2], item[0][3])
    )


def build_asset_dataframe(assets, people, locations):
    people_dict = {p["id"]: p["name"] for p in people}
    location_dict = {l["id"]: l["name"] for l in locations}

    rows = []

    for a in assets:
        eq = a.get("equipment_types") or {}

        rows.append({
            "Asset Code": a.get("asset_code", ""),
            "Equipment": eq.get("name", ""),
            "Category": eq.get("category", ""),
            "Owner": a.get("owner", ""),
            "Current Holder": holder_name_from_asset(a, people_dict, location_dict),
            "Holder Type": a.get("current_holder_type", ""),
            "Note": a.get("note", "")
        })

    return pd.DataFrame(rows)

def build_location_inventory_table(assets, people, locations):
    if not assets:
        return pd.DataFrame()

    people_dict = {p["id"]: p["name"] for p in people}
    location_dict = {l["id"]: l["name"] for l in locations}

    rows = []

    for asset in assets:
        eq = asset.get("equipment_types") or {}

        current_holder = holder_name_from_asset(
            asset,
            people_dict,
            location_dict
        )

        rows.append({
            "Location / Holder": current_holder,
            "Equipment": eq.get("name", "Unnamed Equipment"),
            "Category": eq.get("category", "Uncategorized"),
            "Status": asset.get("status", ""),
            "Quantity": 1,
        })

    df = pd.DataFrame(rows)

    if df.empty:
        return df

    summary = (
        df.groupby(
            ["Location / Holder", "Category", "Equipment", "Status"],
            dropna=False
        )["Quantity"]
        .sum()
        .reset_index()
        .sort_values(["Location / Holder", "Category", "Equipment", "Status"])
    )

    return summary


def render_clean_table(df, empty_message="No data available."):
    if df is None or df.empty:
        st.markdown(
            f"<div class='empty-card'>{escape(empty_message)}</div>",
            unsafe_allow_html=True
        )
        return

    safe_df = df.copy()

    html = "<table class='clean-table'>"
    html += "<thead><tr>"

    for col in safe_df.columns:
        html += f"<th>{escape(str(col))}</th>"

    html += "</tr></thead><tbody>"

    for _, row in safe_df.iterrows():
        html += "<tr>"
        for col in safe_df.columns:
            value = row[col]
            if pd.isna(value):
                value = ""
            html += f"<td>{escape(str(value))}</td>"
        html += "</tr>"

    html += "</tbody></table>"

    st.markdown(html, unsafe_allow_html=True)


def selected_ids_set(selection_key):
    return set(st.session_state.get(selection_key, []))


def set_selected_ids(selection_key, ids):
    st.session_state[selection_key] = sorted(list(set(ids)))


def reset_selection(selection_key):
    st.session_state[selection_key] = []


def go_to_dashboard_with_message(message):
    st.session_state.last_action_message = message
    st.session_state.page = "Dashboard"
    st.rerun()


def render_inventory_by_location_view(assets, people, locations):
    if not assets:
        st.info("No equipment in the system yet.")
        return

    people_dict = {p["id"]: p["name"] for p in people}
    location_dict = {l["id"]: l["name"] for l in locations}

    grouped = {}

    for asset in assets:
        eq = asset.get("equipment_types") or {}

        holder = holder_name_from_asset(asset, people_dict, location_dict)
        holder_type = asset.get("current_holder_type", "")

        equipment_name = (eq.get("name") or "Unnamed Equipment").strip()
        category = (eq.get("category") or "Uncategorized").strip()
        image_data = eq.get("image_data")
        owner = asset.get("owner") or "Unknown"

        key = (holder, holder_type, category, equipment_name)

        if key not in grouped:
            grouped[key] = {
                "holder": holder,
                "holder_type": holder_type,
                "category": category,
                "equipment": equipment_name,
                "image_data": image_data,
                "total": 0,
                "owners": set(),
                "asset_codes": [],
            }

        grouped[key]["total"] += 1
        grouped[key]["owners"].add(owner)
        grouped[key]["asset_codes"].append(asset.get("asset_code", ""))

    holders = sorted(
        set((item["holder"], item["holder_type"]) for item in grouped.values()),
        key=lambda x: (x[1] != "location", x[0])
    )

    for holder, holder_type in holders:
        items = [
            item for item in grouped.values()
            if item["holder"] == holder and item["holder_type"] == holder_type
        ]

        if not items:
            continue

        holder_label = holder
        if holder_type == "person":
            holder_label = f"{holder} — Person"
        elif holder_type == "location":
            holder_label = f"{holder} — Location"

        st.markdown(
            f"<div class='location-section-title'>{escape(holder_label)}</div>",
            unsafe_allow_html=True
        )

        items = sorted(items, key=lambda x: (x["category"], x["equipment"]))

        for item in items:
            with st.container(border=True):
                col_img, col_main, col_stats = st.columns([0.55, 3.4, 1.05])

                with col_img:
                    render_image(item["image_data"], width=68)

                with col_main:
                    st.markdown(
                        f"<div class='group-title'>{escape(item['equipment'])}</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        f"<span class='pill'>{escape(item['category'])}</span>",
                        unsafe_allow_html=True
                    )

                    owner_text = ", ".join(sorted(item["owners"]))
                    st.markdown(
                        f"<div class='location-meta'>Owner: {escape(owner_text)}</div>",
                        unsafe_allow_html=True
                    )

                    asset_codes = sorted([code for code in item["asset_codes"] if code])
                    preview_codes = ", ".join(asset_codes[:6])

                    if len(asset_codes) > 6:
                        preview_codes += f" +{len(asset_codes) - 6}"

                    if preview_codes:
                        st.markdown(
                            f"<div class='location-meta'>Assets: {escape(preview_codes)}</div>",
                            unsafe_allow_html=True
                        )

                with col_stats:
                    st.markdown(
                        f"<span class='pill-dark'>Total {item['total']}</span>",
                        unsafe_allow_html=True
                    )


def render_inventory_category_view(assets, people, locations):
    if not assets:
        st.info("No equipment in the system yet.")
        return

    people_dict = {p["id"]: p["name"] for p in people}
    location_dict = {l["id"]: l["name"] for l in locations}

    grouped = {}

    for asset in assets:
        eq = asset.get("equipment_types") or {}

        equipment_name = (eq.get("name") or "Unnamed Equipment").strip()
        category = (eq.get("category") or "Uncategorized").strip()
        image_data = eq.get("image_data")
        holder = holder_name_from_asset(asset, people_dict, location_dict)
        holder_type = asset.get("current_holder_type", "")

        key = (category, equipment_name)

        if key not in grouped:
            grouped[key] = {
                "category": category,
                "equipment": equipment_name,
                "image_data": image_data,
                "total": 0,
                "holders": {},
                "holder_types": {},
                "owners": set(),
            }

        grouped[key]["total"] += 1
        grouped[key]["holders"][holder] = grouped[key]["holders"].get(holder, 0) + 1
        grouped[key]["holder_types"][holder] = holder_type
        grouped[key]["owners"].add(asset.get("owner") or "Unknown")

    categories = sorted(set(item["category"] for item in grouped.values()))

    for category in categories:
        st.markdown(f"### {category}")

        items = [
            item for item in grouped.values()
            if item["category"] == category
        ]

        items = sorted(items, key=lambda x: x["equipment"])

        for item in items:
            with st.container(border=True):
                st.markdown("<div class='inventory-card-inner'>", unsafe_allow_html=True)

                col_img, col_main, col_stats = st.columns([0.55, 3.4, 1.05])

                with col_img:
                    render_image(item["image_data"], width=74)

                with col_main:
                    st.markdown(
                        f"<div class='group-title'>{escape(item['equipment'])}</div>",
                        unsafe_allow_html=True
                    )

                    owner_text = ", ".join(sorted(item["owners"]))
                    st.markdown(
                        f"<div class='group-subtitle'>Owner: {escape(owner_text)}</div>",
                        unsafe_allow_html=True
                    )

                    st.markdown(
                        "<div class='current-label'>Current location / holder</div>",
                        unsafe_allow_html=True
                    )

                    holder_badges = ""

                    for holder, count in sorted(item["holders"].items()):
                        holder_safe = escape(holder)
                        holder_type = item["holder_types"].get(holder, "")

                        if holder_type == "person":
                            badge_class = "holder-badge holder-person"
                        else:
                            badge_class = "holder-badge holder-location"

                        holder_badges += (
                            f"<span class='{badge_class}'>{holder_safe} × {count}</span>"
                        )

                    st.markdown(
                        f"<div class='holder-badge-row'>{holder_badges}</div>",
                        unsafe_allow_html=True
                    )

                with col_stats:
                    st.markdown(
                        f"""
                        <div class="inventory-stat-box">
                            <span class="pill-dark">Total {item['total']}</span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)

def render_header():
    st.markdown("""
    <div class="app-shell">
        <div class="app-brand-row">
            <div class="brand-left">
                <div class="brand-icon">🧰</div>
                <div>
                    <div class="brand-title">Lab Inventory System</div>
                    <div class="brand-subtitle">Internal equipment checkout, return, and tracking dashboard</div>
                </div>
            </div>
            <div class="brand-badge">Local Prototype</div>
        </div>
    </div>
    """, unsafe_allow_html=True)



def render_navigation():
    nav_items = [
        "Dashboard",
        "Move Items",
        "Equipment",
        "People & Locations",
        "Movement Log",
    ]

    st.markdown('<div class="nav-wrapper">', unsafe_allow_html=True)

    nav_cols = st.columns(len(nav_items))

    for i, item in enumerate(nav_items):
        label = item

        if st.session_state.page == item:
            label = "● " + item

        button_type = "primary" if st.session_state.page == item else "secondary"

        if nav_cols[i].button(label, use_container_width=True, type=button_type):
            st.session_state.page = item
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

def page_header(title, description, icon=""):
    st.markdown(
        f"""
        <div class="page-hero">
            <div class="page-title">{escape(icon)} {escape(title)}</div>
            <div class="page-desc">{escape(description)}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_selected_summary(selected_ids, asset_lookup, title="Current Selection"):
    st.markdown(f"### {title}")

    if not selected_ids:
        st.info("No items selected yet.")
        return

    selected_assets = [
        asset_lookup[asset_id]
        for asset_id in selected_ids
        if asset_id in asset_lookup
    ]

    if not selected_assets:
        st.info("No valid selected items.")
        return

    rows = []

    for asset in selected_assets:
        eq = asset.get("equipment_types") or {}
        rows.append({
            "Asset Code": asset.get("asset_code"),
            "Equipment": eq.get("name"),
            "Category": eq.get("category"),
            "Owner": asset.get("owner"),
        })

    df = pd.DataFrame(rows)

    grouped = (
        df.groupby(["Equipment", "Category"], dropna=False)
        .size()
        .reset_index(name="Quantity")
        .sort_values(["Equipment", "Category"])
    )

    st.markdown("**Summary**")
    render_clean_table(grouped, "No selected items.")

    with st.expander("Show selected asset codes"):
        render_clean_table(
            df.sort_values(["Equipment", "Asset Code"]),
            "No selected asset codes."
        )


def render_group_cards(assets, selection_key, dialog_mode, people, locations):
    grouped_assets = group_assets_by_equipment_name(assets)

    if not grouped_assets:
        st.info("No assets found.")
        return

    selected = selected_ids_set(selection_key)

    for i in range(0, len(grouped_assets), 3):
        cols = st.columns(3)

        for col, ((_,_, equipment_name, category), group_items) in zip(cols, grouped_assets[i:i + 3]):
            eq = group_items[0].get("equipment_types") or {}
            image_data = eq.get("image_data")
            group_ids = [item["id"] for item in group_items]
            selected_count = len([asset_id for asset_id in group_ids if asset_id in selected])
            selected_class = "status-held" if selected_count > 0 else ""
           
            prefixes = sorted(
                set(get_prefix(item.get("asset_code", "")) for item in group_items)
            )

            owners = sorted(
                set((item.get("owner") or "Unknown") for item in group_items)
            )

            prefix_text = ", ".join(prefixes[:3])
            if len(prefixes) > 3:
                prefix_text += f" +{len(prefixes) - 3}"

            owner_text = ", ".join(owners[:2])
            if len(owners) > 2:
                owner_text += f" +{len(owners) - 2}"

            with col:
                with st.container(border=True):
                    top_cols = st.columns([0.9, 2.1])

                    with top_cols[0]:
                        render_image(image_data, width=90)

                    with top_cols[1]:
                        st.markdown(
                            f"<div class='group-title'>{escape(equipment_name or prefix)}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"<div class='group-subtitle'>Owner: {escape(owner_text)}</div>",
                            unsafe_allow_html=True
                        )

                        st.markdown(
                            f"<div class='group-subtitle'>Prefix: {escape(prefix_text)}</div>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"""
                            <span class="pill">{escape(category or "No category")}</span>
                            <span class="pill-dark">{len(group_items)} item(s)</span>
                            <span class="pill-dark {selected_class}">{selected_count} selected</span>
                            """,
                            unsafe_allow_html=True
                        )

                    button_label = "Choose asset numbers"
                    if selected_count > 0:
                        button_label = f"Selected {selected_count} / {len(group_items)}"

                    if st.button(
                        button_label,
                        key=f"{dialog_mode}_open_{equipment_name}_{category}_{i}",
                        use_container_width=True,
                        type="primary" if selected_count > 0 else "secondary"
                    ):
                        
                        asset_group_dialog(
                            group_items=group_items,
                            selection_key=selection_key,
                            title=f"{equipment_name}",
                            people=people,
                            locations=locations
                        )


# -----------------------------
# Dialogs
# -----------------------------
@st.dialog("Select asset numbers")
def asset_group_dialog(group_items, selection_key, title, people, locations):
    st.markdown(f"### {title}")
    st.caption("Select multiple asset numbers. Assets are separated by current location/holder.")

    people_dict = {p["id"]: p["name"] for p in people}
    location_dict = {l["id"]: l["name"] for l in locations}

    grouped_by_holder = defaultdict(list)

    for asset in group_items:
        holder = holder_name_from_asset(asset, people_dict, location_dict)
        grouped_by_holder[holder].append(asset)

    all_group_ids = [asset["id"] for asset in group_items]
    current_selected = selected_ids_set(selection_key)

    new_selected_in_group = set(
        [asset_id for asset_id in all_group_ids if asset_id in current_selected]
    )

    for holder in sorted(grouped_by_holder.keys()):
        assets_in_holder = grouped_by_holder[holder]

        st.markdown(
            f"<div class='location-header'>{escape(holder)}</div>",
            unsafe_allow_html=True
        )

        option_labels = []
        label_to_id = {}

        for asset in assets_in_holder:
            asset_code = asset.get("asset_code", f"Asset {asset['id']}")
            owner = asset.get("owner") or "Unknown owner"
            label = f"{asset_code} | Owner: {owner}"
            option_labels.append(label)
            label_to_id[label] = asset["id"]

        default_labels = [
            label
            for label in option_labels
            if label_to_id[label] in current_selected
        ]

        chosen_labels = st.multiselect(
            "Asset numbers",
            options=option_labels,
            default=default_labels,
            key=f"{selection_key}_{holder}_{title}",
            placeholder="Choose asset numbers",
            label_visibility="collapsed"
        )

        chosen_ids = set([label_to_id[label] for label in chosen_labels])
        holder_ids = set([asset["id"] for asset in assets_in_holder])

        new_selected_in_group.difference_update(holder_ids)
        new_selected_in_group.update(chosen_ids)

    st.divider()

    st.metric("Selected in this group", f"{len(new_selected_in_group)} / {len(group_items)}")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("Apply Selection", type="primary", use_container_width=True):
            outside_group_selected = current_selected.difference(set(all_group_ids))
            final_selection = outside_group_selected.union(new_selected_in_group)
            set_selected_ids(selection_key, final_selection)
            st.rerun()

    with col2:
        if st.button("Select All", use_container_width=True):
            final_selection = current_selected.union(set(all_group_ids))
            set_selected_ids(selection_key, final_selection)
            st.rerun()

    with col3:
        if st.button("Clear Group", use_container_width=True):
            final_selection = current_selected.difference(set(all_group_ids))
            set_selected_ids(selection_key, final_selection)
            st.rerun()


@st.dialog("Confirm checkout")
def checkout_confirm_dialog(selected_asset_ids, asset_lookup, borrower_name, borrower_id, purpose, note):
    selected_assets = [
        asset_lookup[asset_id]
        for asset_id in selected_asset_ids
        if asset_id in asset_lookup
    ]

    st.write("Please confirm this checkout action.")
    st.markdown(f"**Borrower:** {borrower_name}")
    st.markdown(f"**Purpose:** {purpose or '-'}")
    st.markdown(f"**Items:** {len(selected_assets)}")

    preview_rows = []

    for asset in selected_assets:
        eq = asset.get("equipment_types") or {}
        preview_rows.append({
            "Asset Code": asset.get("asset_code"),
            "Equipment": eq.get("name"),
        })

    render_clean_table(pd.DataFrame(preview_rows), "No items selected.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, confirm checkout", type="primary", use_container_width=True):
            batch_id = (
                "CHECKOUT-"
                + datetime.now().strftime("%Y%m%d-%H%M%S")
                + "-"
                + str(uuid.uuid4())[:6]
            )

            success_count = 0
            skipped_items = []

            for asset in selected_assets:
                latest = (
                    supabase.table("assets")
                    .select("*")
                    .eq("id", asset["id"])
                    .single()
                    .execute()
                    .data
                )

                if latest["status"] != "available":
                    skipped_items.append(asset["asset_code"])
                    continue

                supabase.table("assets").update({
                    "current_holder_type": "person",
                    "current_holder_id": borrower_id,
                }).eq("id", asset["id"]).execute()

                create_movement_log(
                    batch_id=batch_id,
                    asset_id=asset["id"],
                    action="checkout",
                    from_holder_type=latest["current_holder_type"],
                    from_holder_id=latest["current_holder_id"],
                    to_holder_type="person",
                    to_holder_id=borrower_id,
                    performed_by=borrower_id,
                    purpose=purpose,
                    note=note
                )

                success_count += 1

            reset_selection("checkout_selected_ids")

            message = f"Checkout completed: {success_count} item(s). Batch ID: {batch_id}"

            if skipped_items:
                message += f" Skipped: {', '.join(skipped_items)}"

            go_to_dashboard_with_message(message)

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Confirm return")
def return_confirm_dialog(selected_asset_ids, asset_lookup, person_name, person_id, return_location_name, return_location_id, note):
    selected_assets = [
        asset_lookup[asset_id]
        for asset_id in selected_asset_ids
        if asset_id in asset_lookup
    ]

    st.write("Please confirm this return action.")
    st.markdown(f"**Person:** {person_name}")
    st.markdown(f"**Return to:** {return_location_name}")
    st.markdown(f"**Items:** {len(selected_assets)}")

    preview_rows = []

    for asset in selected_assets:
        eq = asset.get("equipment_types") or {}
        preview_rows.append({
            "Asset Code": asset.get("asset_code"),
            "Equipment": eq.get("name"),
        })

    render_clean_table(pd.DataFrame(preview_rows), "No items selected.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, confirm return", type="primary", use_container_width=True):
            batch_id = (
                "RETURN-"
                + datetime.now().strftime("%Y%m%d-%H%M%S")
                + "-"
                + str(uuid.uuid4())[:6]
            )

            success_count = 0
            skipped_items = []

            for asset in selected_assets:
                latest = (
                    supabase.table("assets")
                    .select("*")
                    .eq("id", asset["id"])
                    .single()
                    .execute()
                    .data
                )

                is_still_held_by_person = (
                    latest["current_holder_type"] == "person"
                    and latest["current_holder_id"] == person_id
                )

                if not is_still_held_by_person:
                    skipped_items.append(asset["asset_code"])
                    continue

                supabase.table("assets").update({
                    "current_holder_type": "location",
                    "current_holder_id": return_location_id,
                    "status": "available"
                }).eq("id", asset["id"]).execute()

                create_movement_log(
                    batch_id=batch_id,
                    asset_id=asset["id"],
                    action="return",
                    from_holder_type="person",
                    from_holder_id=person_id,
                    to_holder_type="location",
                    to_holder_id=return_location_id,
                    performed_by=person_id,
                    note=note
                )

                success_count += 1

            reset_selection("return_selected_ids")

            message = f"Return completed: {success_count} item(s). Batch ID: {batch_id}"

            if skipped_items:
                message += f" Skipped: {', '.join(skipped_items)}"

            go_to_dashboard_with_message(message)

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()



@st.dialog("Confirm move")
def move_confirm_dialog(
    selected_asset_ids,
    asset_lookup,
    from_holder_label,
    from_holder_type,
    from_holder_id,
    to_holder_label,
    to_holder_type,
    to_holder_id,
    note
):
    selected_assets = [
        asset_lookup[asset_id]
        for asset_id in selected_asset_ids
        if asset_id in asset_lookup
    ]

    st.write("Please confirm this move.")
    st.markdown(f"**From:** {from_holder_label}")
    st.markdown(f"**To:** {to_holder_label}")
    st.markdown(f"**Items:** {len(selected_assets)}")
    st.markdown(f"**Note:** {note or '-'}")

    preview_rows = []

    for asset in selected_assets:
        eq = asset.get("equipment_types") or {}
        preview_rows.append({
            "Asset Code": asset.get("asset_code"),
            "Equipment": eq.get("name"),
        })

    render_clean_table(pd.DataFrame(preview_rows), "No items selected.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, move items", type="primary", use_container_width=True):
            batch_id = (
                "MOVE-"
                + datetime.now().strftime("%Y%m%d-%H%M%S")
                + "-"
                + str(uuid.uuid4())[:6]
            )

            success_count = 0
            skipped_items = []

            for asset in selected_assets:
                latest = (
                    supabase.table("assets")
                    .select("*")
                    .eq("id", asset["id"])
                    .single()
                    .execute()
                    .data
                )

                is_still_in_from_holder = (
                    latest["current_holder_type"] == from_holder_type
                    and latest["current_holder_id"] == from_holder_id
                )

                if not is_still_in_from_holder:
                    skipped_items.append(asset["asset_code"])
                    continue

                # The app no longer uses status in the UI.
                # Keep this value only for compatibility with the existing database.
                supabase.table("assets").update({
                    "current_holder_type": to_holder_type,
                    "current_holder_id": to_holder_id,
                    "status": "available"
                }).eq("id", asset["id"]).execute()

                create_movement_log(
                    batch_id=batch_id,
                    asset_id=asset["id"],
                    action="move",
                    from_holder_type=from_holder_type,
                    from_holder_id=from_holder_id,
                    to_holder_type=to_holder_type,
                    to_holder_id=to_holder_id,
                    performed_by=None,
                    purpose="Move item",
                    note=note
                )

                success_count += 1

            reset_selection("move_selected_ids")

            message = f"Move completed: {success_count} item(s). Batch ID: {batch_id}"

            if skipped_items:
                message += f" Skipped: {', '.join(skipped_items)}"

            go_to_dashboard_with_message(message)

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()

@st.dialog("Confirm add equipment")
def add_equipment_confirm_dialog(form_data):
    st.write("Please review before adding this equipment.")

    image_data = form_data.get("image_data")

    col1, col2 = st.columns([1, 2])

    with col1:
        render_image(image_data, width=140)

    with col2:
        st.markdown(f"**Equipment:** {form_data['name']}")
        st.markdown(f"**Category:** {form_data['category']}")
        st.markdown(f"**Owner:** {form_data['owner']}")
        st.markdown(f"**Home location:** {form_data['home_location_name']}")
        st.markdown(f"**Asset prefix:** {form_data['prefix'].upper()}")
        st.markdown(f"**Quantity:** {form_data['quantity']}")

    st.warning("After confirming, asset codes will be created and the form will be reset.")

    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("Yes, add equipment", type="primary", use_container_width=True):
            eq_response = supabase.table("equipment_types").insert({
                "name": form_data["name"],
                "category": form_data["category"],
                "description": form_data["description"],
                "image_data": form_data["image_data"],
            }).execute()

            eq_id = eq_response.data[0]["id"]
            home_location_id = form_data["home_location_id"]

            created_codes = []

            for i in range(1, int(form_data["quantity"]) + 1):
                code = f"{form_data['prefix'].upper()}-{i:03d}"

                existing = (
                    supabase.table("assets")
                    .select("id")
                    .eq("asset_code", code)
                    .execute()
                    .data
                )

                if existing:
                    code = f"{form_data['prefix'].upper()}-{datetime.now().strftime('%H%M%S')}-{i:03d}"

                supabase.table("assets").insert({
                    "asset_code": code,
                    "equipment_type_id": eq_id,
                    "owner": form_data["owner"],
                    "home_location_id": home_location_id,
                    "current_holder_type": "location",
                    "current_holder_id": home_location_id,
                    "status": "available",
                }).execute()

                created_codes.append(code)

            reset_add_equipment_form()
            st.session_state.last_equipment_message = f"Added {len(created_codes)} asset(s): {', '.join(created_codes)}"
            st.rerun()

    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Edit equipment")
def edit_equipment_dialog(eq, categories, locations):
    st.write("Edit saved equipment information.")

    category_names = [c["name"] for c in categories]
    location_options = {l["name"]: l["id"] for l in locations}

    current_category = eq.get("category") or category_names[0]

    if current_category not in category_names:
        category_names = [current_category] + category_names

    current_image = eq.get("image_data")

    col1, col2 = st.columns([1.2, 0.8])

    with col1:
        new_name = st.text_input(
            "Equipment Name",
            value=eq.get("name") or "",
            key=f"edit_name_{eq['id']}"
        )

        new_category = st.selectbox(
            "Category",
            category_names,
            index=category_names.index(current_category),
            key=f"edit_category_{eq['id']}"
        )

        new_description = st.text_area(
            "Description",
            value=eq.get("description") or "",
            key=f"edit_description_{eq['id']}"
        )

    with col2:
        st.markdown("Current image")
        render_image(current_image, width=160)

        uploaded_image = st.file_uploader(
            "Replace image",
            type=["png", "jpg", "jpeg"],
            key=f"edit_image_{eq['id']}"
        )

        new_image_data = image_to_base64(uploaded_image)

        image_action = st.radio(
            "Image option",
            ["Keep current image", "Replace with uploaded image", "Remove image"],
            key=f"edit_image_action_{eq['id']}"
        )

    st.divider()

    st.subheader("Batch update assets")

    assets_for_eq = get_assets_by_equipment_type(eq["id"])
    active_assets = [a for a in assets_for_eq if a.get("active") is True]
    with_people_assets = [a for a in active_assets if a.get("current_holder_type") == "person"]

    st.markdown(f"Active assets: **{len(active_assets)}**")

    update_owner = st.checkbox(
        "Update owner for all active assets",
        key=f"edit_update_owner_{eq['id']}"
    )

    new_owner = None

    if update_owner:
        current_owner = active_assets[0].get("owner", "Lab") if active_assets else "Lab"
        new_owner = st.text_input(
            "New Owner",
            value=current_owner,
            key=f"edit_owner_{eq['id']}"
        )

    update_home_location = st.checkbox(
        "Update home/current location for available assets",
        key=f"edit_update_location_{eq['id']}"
    )

    new_home_location_id = None

    if update_home_location:
        new_home_location_name = st.selectbox(
            "New Home Location",
            list(location_options.keys()),
            key=f"edit_home_location_{eq['id']}"
        )

        new_home_location_id = location_options[new_home_location_name]

        st.info(
            "This updates home_location for active assets. "
            "Available assets will also move to this location. "
            "Borrowed assets will not be moved."
        )

    st.divider()

    st.subheader("Add more assets")

    add_more = st.checkbox(
        "Add more assets to this equipment type",
        key=f"edit_add_more_{eq['id']}"
    )

    add_prefix = ""
    add_quantity = 1
    new_codes = []

    if add_more:
        add_prefix = st.text_input(
            "Asset Code Prefix",
            value=get_prefix(active_assets[0].get("asset_code", "")) if active_assets else "",
            key=f"edit_add_prefix_{eq['id']}"
        )

        add_quantity = st.number_input(
            "Quantity to Add",
            min_value=1,
            max_value=100,
            value=1,
            step=1,
            key=f"edit_add_quantity_{eq['id']}"
        )

        if add_prefix:
            new_codes = next_asset_codes(add_prefix, add_quantity)
            st.caption("New asset codes to be created:")
            st.write(", ".join(new_codes))

    st.divider()

    col_confirm, col_cancel = st.columns(2)

    with col_confirm:
        if st.button("Save changes", type="primary", use_container_width=True):
            if not new_name:
                st.error("Equipment name cannot be empty.")
                return

            final_image = current_image

            if image_action == "Replace with uploaded image":
                if not new_image_data:
                    st.error("Please upload an image first.")
                    return
                final_image = new_image_data

            if image_action == "Remove image":
                final_image = None

            supabase.table("equipment_types").update({
                "name": new_name,
                "category": new_category,
                "description": new_description,
                "image_data": final_image,
            }).eq("id", eq["id"]).execute()

            if update_owner and new_owner is not None:
                for asset in active_assets:
                    supabase.table("assets").update({
                        "owner": new_owner
                    }).eq("id", asset["id"]).execute()

            if update_home_location and new_home_location_id is not None:
                for asset in active_assets:
                    update_payload = {
                        "home_location_id": new_home_location_id
                    }

                    if asset.get("current_holder_type") == "location":
                        update_payload["current_holder_type"] = "location"
                        update_payload["current_holder_id"] = new_home_location_id

                    supabase.table("assets").update(update_payload).eq("id", asset["id"]).execute()

            if add_more:
                if not add_prefix:
                    st.error("Asset code prefix is required to add more assets.")
                    return

                owner_for_new_assets = active_assets[0].get("owner", "Lab") if active_assets else "Lab"

                if update_owner and new_owner:
                    owner_for_new_assets = new_owner

                location_for_new_assets = new_home_location_id

                if not location_for_new_assets:
                    if active_assets and active_assets[0].get("home_location_id"):
                        location_for_new_assets = active_assets[0].get("home_location_id")
                    else:
                        location_for_new_assets = list(location_options.values())[0]

                for code in new_codes:
                    supabase.table("assets").insert({
                        "asset_code": code,
                        "equipment_type_id": eq["id"],
                        "owner": owner_for_new_assets,
                        "home_location_id": location_for_new_assets,
                        "current_holder_type": "location",
                        "current_holder_id": location_for_new_assets,
                        "status": "available",
                    }).execute()

            st.session_state.last_equipment_message = f"{new_name} updated."
            st.rerun()

    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Confirm equipment deactivation")
def deactivate_equipment_dialog(eq, active_assets, borrowed_assets):
    st.write("This will hide the equipment type and all its active assets from the app.")
    st.markdown(f"**Equipment:** {eq.get('name')}")

    if borrowed_assets:
        st.error("Cannot deactivate this equipment because some assets are currently borrowed.")

        if st.button("Close"):
            st.rerun()

        return

    st.warning("This is a soft delete. Data will not be permanently removed.")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, deactivate", type="primary", use_container_width=True):
            supabase.table("equipment_types").update({
                "active": False
            }).eq("id", eq["id"]).execute()

            supabase.table("assets").update({
                "active": False
            }).eq("equipment_type_id", eq["id"]).execute()

            st.session_state.last_equipment_message = f"{eq.get('name')} deactivated."
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


@st.dialog("Confirm equipment reactivation")
def reactivate_equipment_dialog(eq):
    st.write("This will reactivate this equipment type and its assets.")
    st.markdown(f"**Equipment:** {eq.get('name')}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Yes, reactivate", type="primary", use_container_width=True):
            supabase.table("equipment_types").update({
                "active": True
            }).eq("id", eq["id"]).execute()

            supabase.table("assets").update({
                "active": True
            }).eq("equipment_type_id", eq["id"]).execute()

            st.session_state.last_equipment_message = f"{eq.get('name')} reactivated."
            st.rerun()

    with col2:
        if st.button("Cancel", use_container_width=True):
            st.rerun()


# -----------------------------
# Header and navigation
# -----------------------------
render_header()
render_navigation()

page = st.session_state.page



# -----------------------------
# Dashboard
# -----------------------------
if page == "Dashboard":
    page_header(
        "Dashboard",
        "Overview of where every lab item currently is.",
        "📊"
    )

    if "last_action_message" in st.session_state:
        st.success(st.session_state.last_action_message)
        del st.session_state.last_action_message

    people = get_people()
    locations = get_locations()
    assets = get_assets()

    df = build_asset_dataframe(assets, people, locations)

    if df.empty:
        st.info("No equipment in the system yet. Go to Equipment page to add items.")
    else:
        total_assets = len(df)
        in_locations_count = int((df["Holder Type"] == "location").sum())
        with_people_count = int((df["Holder Type"] == "person").sum())

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Assets", total_assets)
        col2.metric("At Locations", in_locations_count)
        col3.metric("With People", with_people_count)

        with st.expander("Inventory by Category", expanded=True):
            st.caption("Grouped by category and equipment type, with current location/holder.")
            render_inventory_category_view(assets, people, locations)

        with st.expander("Inventory by Location / Holder", expanded=True):
            st.caption("Shows what equipment is currently stored in each location or held by each person.")
            render_inventory_by_location_view(assets, people, locations)

        with st.expander("Items with People", expanded=True):
            st.caption("Items currently with people.")

            with_people = df[df["Holder Type"] == "person"]

            if with_people.empty:
                st.success("No items are currently with people.")
            else:
                person_summary = (
                    with_people.groupby(["Current Holder", "Equipment"], dropna=False)
                    .size()
                    .reset_index(name="Quantity")
                    .sort_values(["Current Holder", "Equipment"])
                )

                render_clean_table(person_summary, "No items with people.")

        with st.expander("Table Summary", expanded=False):
            summary = (
                df.groupby(["Equipment", "Current Holder", "Holder Type"], dropna=False)
                .size()
                .reset_index(name="Quantity")
                .sort_values(["Equipment", "Current Holder", "Holder Type"])
            )

            render_clean_table(summary, "No inventory summary yet.")

        with st.expander("Individual Asset Details", expanded=False):
            render_clean_table(
                df.sort_values(["Equipment", "Asset Code"]),
                "No individual asset details."
            )

# -----------------------------
# Move Items
# -----------------------------
elif page == "Move Items":
    page_header(
        "Move Items",
        "Move equipment from any location or person to another location or person.",
        "🔁"
    )

    people = get_people()
    locations = get_locations()

    if not people and not locations:
        st.warning("Please add at least one person or location first.")
        st.stop()

    holder_options = {}

    for location in locations:
        holder_options[f"Location — {location['name']}"] = ("location", location["id"], location["name"])

    for person in people:
        holder_options[f"Person — {person['name']}"] = ("person", person["id"], person["name"])

    with st.container(border=True):
        st.subheader("Move Information")

        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            from_label = st.selectbox(
                "From",
                list(holder_options.keys()),
                key="move_from_holder"
            )
            from_holder_type, from_holder_id, from_holder_name = holder_options[from_label]

        with col2:
            to_label = st.selectbox(
                "To",
                list(holder_options.keys()),
                key="move_to_holder"
            )
            to_holder_type, to_holder_id, to_holder_name = holder_options[to_label]

        with col3:
            note = st.text_input(
                "Note",
                placeholder="Optional"
            )

    if from_holder_type == to_holder_type and from_holder_id == to_holder_id:
        st.warning("From and To must be different.")
        st.stop()

    movable_assets = get_assets_by_holder(from_holder_type, from_holder_id)

    valid_move_ids = {asset["id"] for asset in movable_assets}
    st.session_state.move_selected_ids = [
        asset_id
        for asset_id in st.session_state.move_selected_ids
        if asset_id in valid_move_ids
    ]

    if not movable_assets:
        st.info(f"No items found in {from_label}.")
        st.stop()

    st.markdown(f"### Items in {from_label}")

    search = st.text_input(
        "Search items to move",
        placeholder="Search by prefix, asset code, name, category, or owner"
    )

    filtered_assets = []

    for asset in movable_assets:
        eq = asset.get("equipment_types") or {}
        prefix = get_prefix(asset.get("asset_code", ""))
        text = f"{prefix} {asset.get('asset_code', '')} {eq.get('name', '')} {eq.get('category', '')} {asset.get('owner', '')}".lower()

        if search.lower() in text:
            filtered_assets.append(asset)

    st.caption(f"Showing {len(filtered_assets)} asset(s) in this holder.")

    with st.container(border=True, height=520):
        render_group_cards(
            filtered_assets,
            selection_key="move_selected_ids",
            dialog_mode="move",
            people=people,
            locations=locations
        )

    asset_lookup = {asset["id"]: asset for asset in movable_assets}
    selected_asset_ids = [
        asset_id
        for asset_id in st.session_state.move_selected_ids
        if asset_id in asset_lookup
    ]

    st.markdown("<div class='selection-box'>", unsafe_allow_html=True)
    render_selected_summary(
        selected_asset_ids,
        asset_lookup,
        title="Current Move Selection"
    )
    st.markdown("</div>", unsafe_allow_html=True)

    col_confirm, col_reset, col_back = st.columns([1, 1, 4])

    with col_confirm:
        if st.button("Confirm Move", type="primary", use_container_width=True):
            if not selected_asset_ids:
                st.error("Please select at least one item.")
            else:
                move_confirm_dialog(
                    selected_asset_ids=selected_asset_ids,
                    asset_lookup=asset_lookup,
                    from_holder_label=from_label,
                    from_holder_type=from_holder_type,
                    from_holder_id=from_holder_id,
                    to_holder_label=to_label,
                    to_holder_type=to_holder_type,
                    to_holder_id=to_holder_id,
                    note=note
                )

    with col_reset:
        if st.button("Reset Selection", use_container_width=True):
            reset_selection("move_selected_ids")
            st.rerun()

    with col_back:
        if st.button("Back to Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()


            
# -----------------------------
# Equipment
# -----------------------------
elif page == "Equipment":
    page_header(
        "Equipment",
        "Add, edit, review, and deactivate lab equipment in one place.",
        "🧾"
    )

    if "last_equipment_message" in st.session_state:
        st.success(st.session_state.last_equipment_message)
        del st.session_state.last_equipment_message

    locations = get_locations()
    categories = get_categories()

    if not locations:
        st.warning("Please add at least one location first.")
        st.stop()

    if not categories:
        st.warning("Please add at least one category first.")
        st.stop()

    location_options = {l["name"]: l["id"] for l in locations}
    category_names = [c["name"] for c in categories]

    tab_add, tab_manage, tab_categories = st.tabs([
        "Add Equipment",
        "Manage Equipment",
        "Categories"
    ])

    with tab_add:
        form_version = st.session_state.add_form_version

        with st.container(border=True):
            st.subheader("Add New Equipment")

            col1, col2 = st.columns([1.2, 0.8])

            with col1:
                name = st.text_input(
                    "Equipment Name",
                    placeholder="e.g. XLR Cable 3m",
                    key=f"eq_name_{form_version}"
                )

                category = st.selectbox(
                    "Category",
                    category_names,
                    key=f"eq_category_{form_version}"
                )

                owner = st.text_input(
                    "Owner",
                    value="Lab",
                    key=f"eq_owner_{form_version}"
                )

                description = st.text_area(
                    "Description",
                    placeholder="Optional",
                    key=f"eq_description_{form_version}"
                )

            with col2:
                uploaded_image = st.file_uploader(
                    "Equipment Image",
                    type=["png", "jpg", "jpeg"],
                    help="Optional. Useful when the item name is not enough.",
                    key=f"eq_image_{form_version}"
                )

                image_data = image_to_base64(uploaded_image)

                if image_data:
                    st.image(image_data, caption="Preview", use_container_width=True)
                else:
                    st.info("No image selected.")

            col3, col4, col5 = st.columns(3)

            with col3:
                home_location_name = st.selectbox(
                    "Home Location",
                    list(location_options.keys()),
                    key=f"eq_home_location_{form_version}"
                )

            with col4:
                prefix = st.text_input(
                    "Asset Code Prefix",
                    placeholder="e.g. XLR",
                    key=f"eq_prefix_{form_version}"
                )

            with col5:
                quantity = st.number_input(
                    "Quantity",
                    min_value=1,
                    max_value=100,
                    value=1,
                    step=1,
                    key=f"eq_quantity_{form_version}"
                )

            st.caption("Example: prefix XLR + quantity 3 creates XLR-001, XLR-002, XLR-003.")

            if st.button("Add Equipment", type="primary"):
                if not name or not prefix:
                    st.error("Please enter Equipment Name and Asset Code Prefix.")
                else:
                    form_data = {
                        "name": name,
                        "category": category,
                        "description": description,
                        "owner": owner,
                        "home_location_name": home_location_name,
                        "home_location_id": location_options[home_location_name],
                        "prefix": prefix,
                        "quantity": quantity,
                        "image_data": image_data,
                    }

                    add_equipment_confirm_dialog(form_data)

    with tab_manage:
        equipment_types = get_equipment_types(include_inactive=True)

        if not equipment_types:
            st.info("No equipment types yet.")
        else:
            search = st.text_input(
                "Search equipment",
                placeholder="Type name, category, or description"
            )

            filtered_equipment = []

            for eq in equipment_types:
                text = f"{eq.get('name', '')} {eq.get('category', '')} {eq.get('description', '')}".lower()

                if search.lower() in text:
                    filtered_equipment.append(eq)

            active_only = st.toggle("Show active equipment only", value=True)

            if active_only:
                filtered_equipment = [eq for eq in filtered_equipment if eq.get("active") is True]

            st.caption(f"Showing {len(filtered_equipment)} equipment type(s).")

            for eq in filtered_equipment:
                assets_for_eq = get_assets_by_equipment_type(eq["id"])
                active_assets = [a for a in assets_for_eq if a.get("active") is True]
                with_people_assets = [a for a in active_assets if a.get("current_holder_type") == "person"]

                with st.container(border=True):
                    col_img, col_info, col_action = st.columns([0.8, 3.2, 1.2])

                    with col_img:
                        render_image(eq.get("image_data"), width=110)

                    with col_info:
                        st.markdown(f"### {eq.get('name', 'Unnamed Equipment')}")

                        category = eq.get("category") or "No category"
                        status_text = "Active" if eq.get("active") else "Inactive"
                        with_people_class = "status-held" if len(with_people_assets) > 0 else ""

                        st.markdown(
                            f"""
                            <span class="pill">{escape(category)}</span>
                            <span class="pill-dark">{escape(status_text)}</span>
                            <span class="pill-dark">{len(active_assets)} active</span>
                            <span class="pill-dark {with_people_class}">{len(with_people_assets)} with people</span>
                            """,
                            unsafe_allow_html=True
                        )

                        description = eq.get("description") or ""

                        if description:
                            st.markdown(f"<div class='muted'>{escape(description)}</div>", unsafe_allow_html=True)

                        with st.expander("Show assets"):
                            if not assets_for_eq:
                                st.info("No assets found.")
                            else:
                                asset_df = pd.DataFrame(assets_for_eq)

                                cols_to_show = [
                                    "asset_code",
                                    "owner",
                                    "current_holder_type",
                                    "current_holder_id",
                                    "active",
                                ]

                                existing_cols = [c for c in cols_to_show if c in asset_df.columns]

                                render_clean_table(
                                    asset_df[existing_cols],
                                    "No assets found."
                                )

                    with col_action:
                        if st.button(
                            "Edit",
                            key=f"edit_{eq['id']}",
                            use_container_width=True
                        ):
                            edit_equipment_dialog(
                                eq=eq,
                                categories=categories,
                                locations=locations
                            )

                        if eq.get("active"):
                            if st.button(
                                "Deactivate",
                                key=f"deactivate_{eq['id']}",
                                use_container_width=True
                            ):
                                deactivate_equipment_dialog(
                                    eq=eq,
                                    active_assets=active_assets,
                                    borrowed_assets=with_people_assets
                                )
                        else:
                            st.info("Inactive")

                            if st.button(
                                "Reactivate",
                                key=f"reactivate_{eq['id']}",
                                use_container_width=True
                            ):
                                reactivate_equipment_dialog(eq)

    with tab_categories:
        st.subheader("Manage Categories")
        st.caption("Use categories to reduce typing errors when adding equipment.")

        with st.container(border=True):
            new_category = st.text_input("New Category Name")

            if st.button("Add Category", type="primary"):
                if not new_category:
                    st.error("Please enter a category name.")
                else:
                    supabase.table("categories").insert({
                        "name": new_category.strip()
                    }).execute()
                    st.success("Category added.")
                    st.rerun()

        categories_all = get_categories(include_inactive=True)

        if not categories_all:
            st.info("No categories yet.")
        else:
            cat_df = pd.DataFrame(categories_all)

            render_clean_table(
                cat_df[["id", "name", "active"]],
                "No categories yet."
            )


# -----------------------------
# People & Locations
# -----------------------------
elif page == "People & Locations":
    page_header(
        "People & Locations",
        "Manage borrowers and storage locations used in checkout workflows.",
        "👥"
    )

    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.subheader("Add Person")
            person_name = st.text_input("Person Name")
            role = st.text_input("Role", placeholder="Student, Advisor, Staff")

            if st.button("Add Person", type="primary"):
                if person_name:
                    supabase.table("people").insert({
                        "name": person_name,
                        "role": role
                    }).execute()

                    st.success("Person added.")
                    st.rerun()
                else:
                    st.error("Please enter a name.")

        st.subheader("People")
        people_df = pd.DataFrame(get_people())

        if people_df.empty:
            st.info("No people yet.")
        else:
            render_clean_table(
                people_df[["id", "name", "role", "active"]],
                "No people yet."
            )

    with col2:
        with st.container(border=True):
            st.subheader("Add Location")
            location_name = st.text_input("Location Name")
            location_type = st.text_input(
                "Location Type",
                placeholder="Storage, Room, External"
            )

            if st.button("Add Location", type="primary"):
                if location_name:
                    supabase.table("locations").insert({
                        "name": location_name,
                        "type": location_type
                    }).execute()

                    st.success("Location added.")
                    st.rerun()
                else:
                    st.error("Please enter a location name.")

        st.subheader("Locations")
        loc_df = pd.DataFrame(get_locations())

        if loc_df.empty:
            st.info("No locations yet.")
        else:
            render_clean_table(
                loc_df[["id", "name", "type", "active"]],
                "No locations yet."
            )


# -----------------------------
# Movement Log
# -----------------------------
elif page == "Movement Log":
    page_header(
        "Movement Log",
        "Review recent checkout and return history for traceability.",
        "📝"
    )

    logs = (
        supabase.table("movement_log")
        .select("*, assets(asset_code, equipment_types(name)), people(name)")
        .order("created_at", desc=True)
        .limit(300)
        .execute()
        .data
        or []
    )

    rows = []

    for log in logs:
        asset = log.get("assets") or {}
        eq = asset.get("equipment_types") or {}
        person = log.get("people") or {}

        rows.append({
            "Time": log.get("created_at"),
            "Batch ID": log.get("batch_id"),
            "Action": log.get("action"),
            "Asset": asset.get("asset_code"),
            "Equipment": eq.get("name"),
            "Performed by": person.get("name"),
            "Purpose": log.get("purpose"),
            "Note": log.get("note"),
        })

    df = pd.DataFrame(rows)

    render_clean_table(df, "No movement log yet.")