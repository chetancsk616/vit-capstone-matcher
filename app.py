from __future__ import annotations

import io
import re
from datetime import datetime
from typing import Iterable

import pandas as pd
import streamlit as st

try:
    from jobspy import scrape_jobs
except Exception:
    scrape_jobs = None


st.set_page_config(
    page_title="Off-Campus Internship Scraper & VIT Capstone Matcher",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

BOARD_MAP = {
    "LinkedIn": "linkedin",
    "Indeed": "indeed",
    "ZipRecruiter": "zip_recruiter",
    "Google Jobs": "google",
}
VERIFIED_BOARDS = {"linkedin", "indeed", "zip_recruiter", "google"}
TRACK_KEYWORDS = [
    "python", "django", "flask", "fastapi", "javascript", "typescript", "react",
    "next.js", "node", "full stack", "frontend", "backend", "software engineer",
    "software developer", "ai", "ml", "machine learning", "deep learning", "llm",
    "data science", "data analyst", "data engineer", "cloud", "aws", "azure",
    "gcp", "devops", "docker", "kubernetes", "cybersecurity", "mobile", "android", "ios",
]
PAID_PATTERNS = [
    r"\bpaid\b", r"\bstipend\b", r"\bcompensation\b", r"\bsalary\b", r"\bctc\b",
    r"\bper\s+month\b", r"\bmonthly\b", r"\bhourly\b", r"\bper\s+hour\b",
    r"\b\d+\s*(?:k|lpa|lakhs?)\b", r"(?:₹|rs\.?|inr|\$|usd)\s*\d+",
]
DURATION_PATTERNS = [
    r"\b[4-6]\s*(?:months?|mos?)\b", r"\b(?:four|five|six)\s+months?\b",
    r"\b20\+?\s*(?:hours?|hrs?)\s*/?\s*(?:week|wk)\b", r"\b(?:full[-\s]?time|fulltime)\b",
    r"\b40\s*(?:hours?|hrs?)\s*/?\s*(?:week|wk)\b", r"\b8th\s*semester\b",
]


def inject_css() -> None:
    st.markdown(
        """
        <style>
            :root { --line: rgba(255,255,255,.11); --text: #eef4ff; --muted: #9aa8bd; }
            .stApp {
                background: radial-gradient(circle at top left, rgba(68,215,182,.12), transparent 32rem),
                            linear-gradient(135deg, #080b12 0%, #0c111b 45%, #101827 100%);
                color: var(--text);
            }
            [data-testid="stSidebar"] { background: rgba(12,18,28,.94); border-right: 1px solid var(--line); }
            [data-testid="stSidebar"] label, [data-testid="stSidebar"] p { color: var(--text); }
            .hero {
                border: 1px solid var(--line); border-radius: 8px; padding: 28px 30px; margin-bottom: 18px;
                background: linear-gradient(135deg, rgba(68,215,182,.20), rgba(116,167,255,.12)),
                            linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.02));
                box-shadow: 0 18px 60px rgba(0,0,0,.22);
            }
            .hero h1 { font-size: 2.2rem; line-height: 1.1; margin: 0 0 10px 0; letter-spacing: 0; }
            .hero p { color: #cbd7ea; max-width: 820px; margin: 0; font-size: 1rem; }
            .pill {
                display: inline-flex; border: 1px solid rgba(68,215,182,.35); color: #bff6e9;
                background: rgba(68,215,182,.12); border-radius: 999px; padding: 7px 12px;
                font-size: .78rem; font-weight: 700; margin-bottom: 12px; text-transform: uppercase;
            }
            .metric-card { border: 1px solid var(--line); border-radius: 8px; padding: 16px; background: rgba(16,23,34,.78); }
            .metric-label { color: var(--muted); font-size: .78rem; text-transform: uppercase; font-weight: 700; }
            .metric-value { color: var(--text); font-size: 1.7rem; font-weight: 800; margin-top: 3px; }
            .job-card {
                border: 1px solid var(--line); border-radius: 8px; padding: 18px; margin: 0 0 14px 0;
                background: linear-gradient(180deg, rgba(21,31,44,.96), rgba(13,19,29,.96));
                box-shadow: 0 14px 36px rgba(0,0,0,.18);
            }
            .job-topline { display: flex; justify-content: space-between; gap: 14px; align-items: flex-start; }
            .job-title { font-size: 1.13rem; font-weight: 800; color: var(--text); margin-bottom: 3px; }
            .job-meta { color: var(--muted); font-size: .92rem; }
            .badge-row { display: flex; gap: 8px; flex-wrap: wrap; margin-top: 12px; }
            .badge {
                border-radius: 999px; padding: 6px 10px; font-size: .78rem; font-weight: 800;
                white-space: nowrap; border: 1px solid rgba(255,255,255,.11);
            }
            .badge-platform { color: #d8e5ff; background: rgba(116,167,255,.13); }
            .badge-ready { color: #bff6e9; background: rgba(68,215,182,.16); border-color: rgba(68,215,182,.34); }
            .badge-review { color: #ffe6a6; background: rgba(246,200,95,.16); border-color: rgba(246,200,95,.34); }
            .badge-risk { color: #ffd0d5; background: rgba(255,107,122,.16); border-color: rgba(255,107,122,.34); }
            .summary { color: #c8d4e5; margin-top: 13px; line-height: 1.55; font-size: .93rem; }
            .apply-button {
                display: inline-block; color: #061018 !important; background: linear-gradient(135deg, #44d7b6, #74a7ff);
                border-radius: 7px; padding: 9px 13px; text-decoration: none !important; font-weight: 900; margin-top: 14px;
            }
            .rule-list { color: #c8d4e5; margin-top: 8px; line-height: 1.55; }
            .stTabs [data-baseweb="tab-list"] { gap: 8px; }
            .stTabs [data-baseweb="tab"] { border-radius: 8px; background: rgba(255,255,255,.05); border: 1px solid var(--line); padding: 8px 14px; }
            div[data-testid="stDataFrame"] { border: 1px solid var(--line); border-radius: 8px; overflow: hidden; }
            @media (max-width: 760px) { .hero { padding: 22px; } .hero h1 { font-size: 1.65rem; } .job-topline { flex-direction: column; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def contains_any(patterns: Iterable[str], text: str) -> bool:
    return any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in patterns)


def matched_keywords(text: str) -> list[str]:
    lowered = text.lower()
    return [keyword for keyword in TRACK_KEYWORDS if keyword in lowered]


def normalize_site(site: str | None) -> str:
    site = (site or "").strip().lower().replace(" ", "_")
    aliases = {"ziprecruiter": "zip_recruiter", "google_jobs": "google"}
    return aliases.get(site, site)


def compatibility_badge(score: int) -> tuple[str, str]:
    if score >= 70:
        return "🟢 VIT Capstone Ready", "badge-ready"
    if score >= 40:
        return "🟡 Requires Review", "badge-review"
    return "🔴 Risk: Likely Unpaid/Part-Time", "badge-risk"


def compute_vit_score(row: pd.Series) -> dict[str, object]:
    combined_text = " ".join(str(row.get(column, "") or "") for column in [
        "title", "company", "location", "description", "job_type", "interval", "min_amount", "max_amount"
    ])
    site = normalize_site(str(row.get("site", "")))
    paid = contains_any(PAID_PATTERNS, combined_text) or pd.notna(row.get("min_amount")) or pd.notna(row.get("max_amount"))
    commitment = contains_any(DURATION_PATTERNS, combined_text)
    legitimate = site in VERIFIED_BOARDS
    keywords = matched_keywords(combined_text)
    score = (30 if paid else 0) + (20 if commitment else 0) + (20 if legitimate else 0) + (30 if keywords else 0)
    badge, badge_class = compatibility_badge(score)
    return {
        "vit_score": score,
        "vit_badge": badge,
        "vit_badge_class": badge_class,
        "paid_signal": paid,
        "duration_signal": commitment,
        "verified_platform": legitimate,
        "track_keywords": ", ".join(keywords[:8]) if keywords else "No direct match",
    }


def clean_jobs(raw_jobs: pd.DataFrame) -> pd.DataFrame:
    if raw_jobs is None or raw_jobs.empty:
        return pd.DataFrame()
    jobs = raw_jobs.copy()
    expected_columns = [
        "site", "job_url", "title", "company", "location", "date_posted", "job_type",
        "interval", "min_amount", "max_amount", "description",
    ]
    for column in expected_columns:
        if column not in jobs.columns:
            jobs[column] = None
    jobs["site"] = jobs["site"].fillna("Unknown").astype(str).str.replace("_", " ").str.title()
    jobs["title"] = jobs["title"].fillna("Untitled role")
    jobs["company"] = jobs["company"].fillna("Unknown company")
    jobs["location"] = jobs["location"].fillna("Not specified")
    jobs["description"] = jobs["description"].fillna("")
    jobs["job_url"] = jobs["job_url"].fillna("")
    score_frame = jobs.apply(compute_vit_score, axis=1, result_type="expand")
    jobs = pd.concat([jobs, score_frame], axis=1)
    jobs = jobs.sort_values(["vit_score", "date_posted"], ascending=[False, False], na_position="last")
    return jobs.reset_index(drop=True)


@st.cache_data(ttl=60 * 30, show_spinner=False)
def scrape_cached_jobs(search_query: str, location: str, selected_platforms: tuple[str, ...], max_results: int) -> tuple[pd.DataFrame, str | None]:
    if scrape_jobs is None:
        return pd.DataFrame(), "python-jobspy is not installed. Run pip install -r requirements.txt and restart Streamlit."
    site_names = [BOARD_MAP[platform] for platform in selected_platforms]
    try:
        raw_jobs = scrape_jobs(
            site_name=site_names,
            search_term=search_query,
            location=location,
            results_wanted=max_results,
            hours_old=168,
            country_indeed="India",
            description_format="markdown",
            verbose=0,
        )
        return clean_jobs(raw_jobs), None
    except TimeoutError:
        return pd.DataFrame(), "The scraper timed out. Try fewer platforms or lower max results."
    except Exception as exc:
        return pd.DataFrame(), f"Scraping failed: {exc}"


def text_preview(text: str, max_chars: int = 310) -> str:
    stripped = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(stripped) <= max_chars:
        return stripped or "No description was provided by the source."
    return f"{stripped[:max_chars].rstrip()}..."


def html_escape(value: object) -> str:
    return (str(value or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;"))


def render_job_card(row: pd.Series) -> None:
    badge_class = html_escape(row.get("vit_badge_class", "badge-risk"))
    apply_url = str(row.get("job_url", "") or "")
    apply_html = ""
    if apply_url.startswith(("http://", "https://")):
        apply_html = f'<a class="apply-button" href="{html_escape(apply_url)}" target="_blank" rel="noopener noreferrer">Apply Now</a>'
    st.markdown(
        f"""
        <div class="job-card">
            <div class="job-topline">
                <div>
                    <div class="job-title">{html_escape(row.get("title"))}</div>
                    <div class="job-meta">{html_escape(row.get("company"))} · {html_escape(row.get("location"))}</div>
                </div>
                <div class="badge {badge_class}">{html_escape(row.get("vit_badge"))} · {int(row.get("vit_score", 0))}%</div>
            </div>
            <div class="badge-row">
                <span class="badge badge-platform">{html_escape(row.get("site"))}</span>
                <span class="badge badge-platform">Paid: {"Yes" if row.get("paid_signal") else "Check"}</span>
                <span class="badge badge-platform">Duration: {"Suitable" if row.get("duration_signal") else "Unclear"}</span>
                <span class="badge badge-platform">Track: {html_escape(row.get("track_keywords"))}</span>
            </div>
            <div class="summary">{html_escape(text_preview(row.get("description")))}</div>
            {apply_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def dataframe_downloads(df: pd.DataFrame) -> None:
    csv_data = df.to_csv(index=False).encode("utf-8")
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="VIT Matched Roles", index=False)
    col_a, col_b = st.columns(2)
    with col_a:
        st.download_button("Download CSV", data=csv_data, file_name=f"vit_capstone_jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.csv", mime="text/csv", use_container_width=True)
    with col_b:
        st.download_button("Download Excel", data=excel_buffer.getvalue(), file_name=f"vit_capstone_jobs_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)


def render_metrics(df: pd.DataFrame) -> None:
    ready_count = int((df["vit_score"] >= 70).sum()) if not df.empty else 0
    review_count = int(((df["vit_score"] >= 40) & (df["vit_score"] < 70)).sum()) if not df.empty else 0
    avg_score = int(round(df["vit_score"].mean())) if not df.empty else 0
    cols = st.columns(4)
    metrics = [("Roles Found", len(df)), ("Capstone Ready", ready_count), ("Requires Review", review_count), ("Avg VIT Score", f"{avg_score}%")]
    for col, (label, value) in zip(cols, metrics):
        with col:
            st.markdown(f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div></div>', unsafe_allow_html=True)


def render_checklist() -> None:
    st.subheader("VIT Capstone Conversion Checklist")
    st.caption("Use this as a verification companion before submitting any off-campus internship for 20-credit conversion.")
    with st.expander("Paid stipend requirement", expanded=True):
        st.checkbox("Offer letter mentions stipend, salary, hourly pay, or written compensation.", key="paid_check")
        st.checkbox("Compensation proof can be submitted if requested by the department.", key="paid_proof_check")
        st.markdown('<div class="rule-list">The app scores compensation signals at 30% because unpaid roles are usually the largest conversion risk.</div>', unsafe_allow_html=True)
    with st.expander("Minimum duration and full-time commitment"):
        st.checkbox("Internship duration is clearly 4 to 6 months.", key="duration_check")
        st.checkbox("Role supports at least 20 hours per week or full-time engagement.", key="hours_check")
        st.checkbox("Timeline aligns with the 8th-semester Capstone window.", key="semester_check")
    with st.expander("3-review cycle"):
        st.checkbox("Review 1: Problem statement, scope, company mentor details, and expected output.", key="review_1")
        st.checkbox("Review 2: Midpoint progress, implementation proof, and mentor feedback.", key="review_2")
        st.checkbox("Review 3: Final demo, report, presentation, and completion evidence.", key="review_3")
    with st.expander("Internal and external guide allocation"):
        st.checkbox("Internal faculty guide is allocated and aware of the company project.", key="internal_guide")
        st.checkbox("External/company guide details are captured with email and designation.", key="external_guide")
        st.checkbox("Both guides can support reviews and final evaluation artifacts.", key="guide_support")
    with st.expander("NOC generation steps"):
        st.checkbox("Shortlisted role has a verified company, location, and direct application link.", key="noc_company")
        st.checkbox("Offer letter or selection email is available.", key="noc_offer")
        st.checkbox("Department approval, NOC request, and portal submission steps are completed.", key="noc_submission")


def main() -> None:
    inject_css()
    st.markdown(
        """
        <section class="hero">
            <div class="pill">VIT Capstone Compliant Engine</div>
            <h1>Off-Campus Internship Scraper & VIT Capstone Matcher</h1>
            <p>Search verified tech job boards, score internship postings against VIT 20-credit Capstone conversion signals, and export a shortlist with direct application links.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    with st.sidebar:
        st.header("Search Controls")
        search_query = st.text_input("Search Query", value="Software Engineering Intern")
        location = st.text_input("Location", value="Remote")
        selected_platforms = st.multiselect("Job Platforms", options=list(BOARD_MAP.keys()), default=["LinkedIn", "Indeed", "Google Jobs"])
        max_results = st.slider("Max Results Per Platform", min_value=5, max_value=50, value=15, step=5)
        only_ready = st.toggle("Show Only VIT Capstone Ready Roles (>=70% Score)", value=False)
        run_search = st.button("Run Scraper", type="primary", use_container_width=True)
        st.divider()
        st.caption("Scoring weights: Paid 30%, duration 20%, verified platform 20%, engineering keyword match 30%.")
    if not selected_platforms:
        st.warning("Choose at least one platform from the sidebar.")
        return
    if "last_search" not in st.session_state:
        st.session_state.last_search = None
    if run_search or st.session_state.last_search is None:
        with st.spinner("Scraping job boards and scoring VIT compatibility..."):
            jobs, error = scrape_cached_jobs(search_query, location, tuple(selected_platforms), max_results)
        st.session_state.last_search = {"jobs": jobs, "error": error, "query": search_query, "location": location, "platforms": selected_platforms}
    state = st.session_state.last_search
    jobs = state["jobs"]
    error = state["error"]
    if error:
        st.error(error)
    if jobs.empty:
        st.info("No roles found for this search. Try a broader query, another location, or fewer platform filters.")
        render_checklist()
        return
    filtered_jobs = jobs[jobs["vit_score"] >= 70].copy() if only_ready else jobs.copy()
    render_metrics(filtered_jobs)
    st.write("")
    tab_cards, tab_table, tab_checklist = st.tabs(["🎴 Job Cards", "📊 Data Table", "📜 VIT Capstone Checklist"])
    with tab_cards:
        if filtered_jobs.empty:
            st.info("No roles matched the current VIT-ready filter. Disable the toggle to review borderline postings.")
        else:
            for _, row in filtered_jobs.iterrows():
                render_job_card(row)
    with tab_table:
        quick_search = st.text_input("Quick Search", placeholder="Filter by title, company, location, keyword, or platform")
        table_df = filtered_jobs.copy()
        if quick_search:
            haystack = table_df.astype(str).agg(" ".join, axis=1).str.lower()
            table_df = table_df[haystack.str.contains(re.escape(quick_search.lower()), na=False)]
        display_columns = ["vit_score", "vit_badge", "title", "company", "location", "site", "track_keywords", "paid_signal", "duration_signal", "job_url"]
        st.dataframe(
            table_df[display_columns],
            use_container_width=True,
            hide_index=True,
            column_config={
                "vit_score": st.column_config.ProgressColumn("VIT Score", min_value=0, max_value=100, format="%d%%"),
                "job_url": st.column_config.LinkColumn("Apply Link", display_text="Open"),
                "paid_signal": st.column_config.CheckboxColumn("Paid Signal"),
                "duration_signal": st.column_config.CheckboxColumn("Duration Signal"),
            },
        )
        dataframe_downloads(table_df[display_columns])
    with tab_checklist:
        render_checklist()


if __name__ == "__main__":
    main()
