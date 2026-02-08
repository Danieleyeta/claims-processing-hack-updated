#!/usr/bin/env python3
"""
Claims Processing UI (Enterprise Edition)
Streamlit frontend for the Claims Processing REST API
"""
import os
import httpx
import streamlit as st
from dotenv import load_dotenv

# Load environment variables (safe for local/dev; ignored if path doesn't exist)
try:
    load_dotenv("/workspaces/claims-processing-hack/.env")
except Exception:
    pass

# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="Claims Processing System",
    page_icon="🛡️",
    layout="wide",
)

# -----------------------------
# Enterprise UI CSS
# -----------------------------
st.markdown(
    """
<style>
/* App background + spacing */
.block-container { padding-top: 1.2rem; padding-bottom: 2rem; }

/* Header */
.app-title { font-size: 2.0rem; font-weight: 700; color: #0F172A; margin: 0; }
.app-subtitle { font-size: 0.95rem; color: #64748B; margin-top: 0.25rem; }

/* Cards */
.card {
  background: #FFFFFF;
  border: 1px solid #E2E8F0;
  border-radius: 14px;
  padding: 16px 16px 14px 16px;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.06);
}
.card-title { font-size: 0.95rem; font-weight: 700; color: #0F172A; margin-bottom: 8px; }
.card-subtle { color: #64748B; font-size: 0.85rem; }

/* Status pills */
.pill {
  display: inline-block;
  padding: 6px 10px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.85rem;
  border: 1px solid transparent;
}
.pill-ok { background: #ECFDF5; color: #065F46; border-color: #A7F3D0; }
.pill-bad { background: #FEF2F2; color: #991B1B; border-color: #FECACA; }
.pill-warn { background: #FFFBEB; color: #92400E; border-color: #FDE68A; }
.pill-neutral { background: #F1F5F9; color: #0F172A; border-color: #E2E8F0; }

/* Section headings */
.section-h { margin-top: 0.75rem; margin-bottom: 0.25rem; font-size: 1.15rem; font-weight: 700; color: #0F172A; }
.section-p { margin-top: 0; color: #64748B; }

/* Small key/value table */
.kv { display: grid; grid-template-columns: 140px 1fr; row-gap: 10px; column-gap: 12px; margin-top: 10px; }
.k { color: #64748B; font-size: 0.85rem; }
.v { color: #0F172A; font-size: 0.95rem; font-weight: 600; }

/* Footer */
.footer { text-align:center; color:#94A3B8; font-size:12px; padding-top:14px; }
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Defaults
# -----------------------------
DEFAULT_API_URL = os.environ.get(
    "API_URL",
    "https://claims-processing-api.orangeforest-dfe25231.swedencentral.azurecontainerapps.io",
).rstrip("/")


def get_api_url() -> str:
    if "api_url" not in st.session_state:
        st.session_state.api_url = DEFAULT_API_URL
    return st.session_state.api_url.rstrip("/")


def check_health(api_url: str) -> dict:
    try:
        with httpx.Client(timeout=10.0) as client:
            r = client.get(f"{api_url}/health")
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"status": "error", "error": str(e)}


def process_claim(api_url: str, file_content: bytes, filename: str, mime: str) -> dict:
    try:
        with httpx.Client(timeout=180.0) as client:
            files = {"file": (filename, file_content, mime)}
            r = client.post(f"{api_url}/process-claim/upload", files=files)
            r.raise_for_status()
            return r.json()
    except Exception as e:
        return {"success": False, "error": str(e)}


def severity_pill(severity: str) -> str:
    s = (severity or "").strip().lower()
    if s in ["severe", "critical", "high", "significant"]:
        return '<span class="pill pill-bad">High</span>'
    if s in ["moderate", "medium"]:
        return '<span class="pill pill-warn">Medium</span>'
    if s in ["minor", "low"]:
        return '<span class="pill pill-ok">Low</span>'
    return f'<span class="pill pill-neutral">{severity or "N/A"}</span>'


def display_results(data: dict):
    if not data:
        return

    vehicle = data.get("vehicle_info", {}) or {}
    damage = data.get("damage_assessment", {}) or {}
    incident = data.get("incident_info", {}) or {}
    meta = data.get("metadata", {}) or {}

    # Summary row (enterprise "overview")
    st.markdown('<div class="section-h">Claim Summary</div>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("Vehicle", f"{vehicle.get('make','')} {vehicle.get('model','')}".strip() or "N/A")
    with c2:
        st.metric("Year", vehicle.get("year", "N/A"))
    with c3:
        st.metric("OCR Characters", meta.get("ocr_characters", "N/A"))
    with c4:
        wf = meta.get("workflow", "N/A")
        st.metric("Workflow", wf)

    st.markdown("")

    # 2-column details layout
    left, right = st.columns([1.2, 1])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Vehicle Information</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="kv">
  <div class="k">Make</div><div class="v">{vehicle.get("make","N/A")}</div>
  <div class="k">Model</div><div class="v">{vehicle.get("model","N/A")}</div>
  <div class="k">Color</div><div class="v">{vehicle.get("color","N/A")}</div>
  <div class="k">Year</div><div class="v">{vehicle.get("year","N/A")}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Incident Details</div>', unsafe_allow_html=True)

        st.markdown(
            f"""
<div class="kv">
  <div class="k">Date</div><div class="v">{incident.get("date","N/A")}</div>
  <div class="k">Location</div><div class="v">{incident.get("location","N/A")}</div>
</div>
""",
            unsafe_allow_html=True,
        )
        desc = incident.get("description", "N/A")
        st.markdown(f"<div style='margin-top:10px; color:#0F172A;'><b>Description</b></div>", unsafe_allow_html=True)
        st.write(desc)
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Damage Assessment</div>', unsafe_allow_html=True)

        sev = damage.get("severity", "N/A")
        est = damage.get("estimated_cost", None)
        areas = damage.get("affected_areas", []) or []

        sev_html = severity_pill(str(sev))
        st.markdown(
            f"""
<div class="kv">
  <div class="k">Severity</div><div class="v">{sev_html}</div>
  <div class="k">Estimated Cost</div><div class="v">{f"${est:,.2f}" if isinstance(est,(int,float)) else (est if est is not None else "N/A")}</div>
  <div class="k">Affected Areas</div><div class="v">{len(areas) if isinstance(areas,list) else "N/A"}</div>
</div>
""",
            unsafe_allow_html=True,
        )

        if isinstance(areas, list) and areas:
            st.markdown("<div style='margin-top:10px;'><b>Areas</b></div>", unsafe_allow_html=True)
            for a in areas:
                st.markdown(f"- {a}")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("")
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Trace & Metadata</div>', unsafe_allow_html=True)
        st.markdown(
            f"""
<div class="kv">
  <div class="k">Source Image</div><div class="v" style="font-weight:600; font-size:0.85rem;">{meta.get("source_image","N/A")}</div>
</div>
<p class="card-subtle" style="margin-top:10px;">
Tip: Use this metadata to correlate with logs/traces in Application Insights.
</p>
""",
            unsafe_allow_html=True,
        )
        st.markdown("</div>", unsafe_allow_html=True)


def main():
    # Header
    st.markdown(
        """
<div>
  <p class="app-title">Claims Processing System</p>
  <p class="app-subtitle">AI-powered extraction of structured claim data from uploaded images</p>
</div>
""",
        unsafe_allow_html=True,
    )
    st.divider()

    # Sidebar config
    with st.sidebar:
        st.markdown("### Configuration")
        api_url = st.text_input("API URL", value=get_api_url()).strip().rstrip("/")
        st.session_state.api_url = api_url

        st.markdown("")
        if st.button("Check API Health", use_container_width=True):
            with st.spinner("Checking health..."):
                result = check_health(api_url)

            if result.get("status") == "healthy":
                st.markdown('<span class="pill pill-ok">Healthy</span>', unsafe_allow_html=True)
                st.caption(result.get("service", ""))
                st.caption(f"Version: {result.get('version','')}")
            else:
                st.markdown('<span class="pill pill-bad">Unreachable</span>', unsafe_allow_html=True)
                st.caption(result.get("error", "Unknown error"))

        st.markdown("---")
        st.caption("Use **Local** API: `http://localhost:8080`")
        st.caption("Or **Deployed** API: `https://<your-container-app-url>`")

    # Main content layout
    left, right = st.columns([1.3, 0.7])

    with left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Upload Claim Image</div>', unsafe_allow_html=True)
        st.caption("Supported formats: JPG, JPEG, PNG")

        uploaded = st.file_uploader("Select an image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

        st.markdown("")
        process_btn = st.button(
            "Process Claim",
            type="primary",
            use_container_width=True,
            disabled=not uploaded,
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-title">Preview</div>', unsafe_allow_html=True)
        if uploaded:
            st.image(uploaded, use_container_width=True)
            st.caption(uploaded.name)
        else:
            st.caption("Upload an image to preview it here.")
        st.markdown("</div>", unsafe_allow_html=True)

    # Processing + results
    if process_btn and uploaded:
        st.markdown("")
        with st.status("Processing claim...", expanded=True) as status:
            status.update(label="Uploading image...", state="running")
            file_bytes = uploaded.getvalue()

            # better mime handling
            name_lower = uploaded.name.lower()
            if name_lower.endswith(".png"):
                mime = "image/png"
            else:
                mime = "image/jpeg"

            status.write("Calling OCR + Structuring workflow…")
            result = process_claim(st.session_state.api_url, file_bytes, uploaded.name, mime)

            if result.get("success"):
                status.update(label="Processing complete", state="complete")
            else:
                status.update(label="Processing failed", state="error")

        st.divider()
        st.markdown('<div class="section-h">Results</div>', unsafe_allow_html=True)
        st.markdown('<p class="section-p">Structured claim information extracted from the image.</p>', unsafe_allow_html=True)

        if result.get("success"):
            st.markdown('<span class="pill pill-ok">Success</span>', unsafe_allow_html=True)
            st.markdown("")
            display_results(result.get("data", {}))

            st.markdown("")
            with st.expander("View raw JSON"):
                st.json(result)
        else:
            st.markdown('<span class="pill pill-bad">Error</span>', unsafe_allow_html=True)
            st.error(result.get("error", "Unknown error"))

    st.markdown('<div class="footer">© 2026 Claims Processing Platform • Powered by Azure AI</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
