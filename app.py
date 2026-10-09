
import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import base64
import html

# ==========================================
# RIZQ — CLIMATE RETROFIT INTELLIGENCE
# Academic Research Prototype
# ==========================================

st.set_page_config(
    page_title="RIZQ | Climate Retrofit Intelligence",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

ASSETS = Path(__file__).resolve().parent / "assets"

# ==========================================
# DESIGN SYSTEM
# ==========================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #f4f8f6;
}

[data-testid="stSidebar"] {
    background: #102b34;
}

[data-testid="stSidebar"] * {
    color: #f1fff9 !important;
}

h1, h2, h3 {
    color: #153c34;
}

.hero {
    padding: 44px 38px;
    border-radius: 24px;
    background: linear-gradient(115deg, #102b34, #185a48, #378c68);
    color: white;
    margin-bottom: 24px;
}

.hero h1 {
    color: white;
    font-size: 52px;
    margin: 8px 0;
    font-weight: 800;
}

.hero p {
    color: #e2fff0;
    font-size: 17px;
}

.eyebrow {
    color: #b9f7d4;
    letter-spacing: 2px;
    font-size: 12px;
    font-weight: 800;
}

.chip {
    display: inline-block;
    border: 1px solid #a2d8bf;
    padding: 8px 12px;
    margin: 8px 6px 0 0;
    border-radius: 24px;
    font-size: 12px;
    color: white;
}

.notice {
    background: #e3f3eb;
    border: 1px solid #b9dfcc;
    color: #17533e;
    padding: 16px;
    border-radius: 14px;
    margin: 12px 0 24px 0;
}

.section-note {
    color: #637e73;
    margin-bottom: 18px;
}

[data-testid="stMetric"] {
    background: white;
    border: 1px solid #e0ebe5;
    border-radius: 16px;
    padding: 18px;
}

[data-testid="stMetricValue"] {
    color: #176a4d;
}

.stButton > button[kind="primary"] {
    background: #176a4d;
    border-color: #176a4d;
}

div[data-testid="stDataFrame"] {
    border-radius: 14px;
}

/* Uniform image tiles, independent of SVG dimensions */
.rizq-image-card {
    background: #ffffff;
    border: 1px solid #dce9e2;
    border-radius: 18px;
    overflow: hidden;
    box-shadow: 0 6px 18px rgba(16,43,52,.05);
    margin-bottom: 12px;
}
.rizq-image-stage {
    height: 154px;
    background: #edf6f1;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 14px;
}
.rizq-image-stage img {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: contain;
}
.rizq-image-title {
    padding: 13px 14px 15px;
    font-size: 14px;
    font-weight: 700;
    color: #153c34;
}
.rizq-feature-image {
    background: #edf6f1;
    border: 1px solid #dce9e2;
    border-radius: 18px;
    height: 220px;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    overflow: hidden;
    margin: 8px 0 22px;
}
.rizq-feature-image img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
@media (max-width: 768px) {
    .hero { padding: 30px 24px; }
    .hero h1 { font-size: 42px; }
    .rizq-image-stage { height: 132px; }
}
</style>
""", unsafe_allow_html=True)


# ==========================================
# SAMPLE DATA
# ==========================================

DEFAULT_BUILDINGS = [
    {
        "Building": "Al Noor Residential Tower",
        "Type": "Residential",
        "Area": 18000,
        "Energy": 3600000,
        "Age": 22,
        "Budget": 1800000,
        "Solar": True,
        "Status": "Assessment ready"
    },
    {
        "Building": "Green Horizon School",
        "Type": "Education",
        "Area": 9200,
        "Energy": 1550000,
        "Age": 18,
        "Budget": 950000,
        "Solar": True,
        "Status": "Assessment ready"
    },
    {
        "Building": "Central Business Plaza",
        "Type": "Commercial",
        "Area": 24000,
        "Energy": 5500000,
        "Age": 28,
        "Budget": 2900000,
        "Solar": False,
        "Status": "Assessment ready"
    },
    {
        "Building": "Community Health Center",
        "Type": "Healthcare",
        "Area": 6500,
        "Energy": 1150000,
        "Age": 14,
        "Budget": 750000,
        "Solar": True,
        "Status": "Assessment ready"
    }
]

if "buildings" not in st.session_state:
    st.session_state.buildings = DEFAULT_BUILDINGS.copy()

if "projects" not in st.session_state:
    st.session_state.projects = []

if "workers" not in st.session_state:
    st.session_state.workers = [
        {"Name": "Worker A", "Skill": "Solar PV", "Available": True},
        {"Name": "Worker B", "Skill": "HVAC", "Available": True},
        {"Name": "Worker C", "Skill": "Energy Auditing", "Available": True}
    ]


# ==========================================
# HELPERS
# ==========================================

def _svg_data_url(filename):
    """Read only named local SVG files, for consistent HTML image sizing."""
    allowed = {"city.svg", "retrofit.svg", "solar.svg", "workers.svg"}
    if filename not in allowed:
        return None
    path = ASSETS / filename
    if not path.is_file() or path.stat().st_size <= 20:
        return None
    try:
        raw = path.read_bytes()
        return "data:image/svg+xml;base64," + base64.b64encode(raw).decode("ascii")
    except OSError:
        return None


def show_image(filename, caption=None):
    """Display large feature artwork at a fixed, non-cropped height."""
    src = _svg_data_url(filename)
    if src:
        st.markdown(
            f'<div class="rizq-feature-image"><img src="{src}" '
            f'alt="{html.escape(filename)}"></div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Image missing or empty: assets/{filename}")
    if caption:
        st.caption(caption)


def show_solution_card(title, filename):
    """Uniform visual card: same dimensions, no image cropping."""
    src = _svg_data_url(filename)
    safe_title = html.escape(title)
    if src:
        st.markdown(
            '<div class="rizq-image-card">'
            f'<div class="rizq-image-stage"><img src="{src}" alt="{safe_title}"></div>'
            f'<div class="rizq-image-title">{safe_title}</div>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.info(f"Missing: assets/{filename}")


def calculate_assessment(building):
    area = max(float(building["Area"]), 1)
    energy = max(float(building["Energy"]), 0)
    age = max(int(building["Age"]), 0)

    intensity = energy / area

    # Illustrative rules, not a trained AI model
    intensity_score = min(intensity / 350, 1) * 45
    age_score = min(age / 35, 1) * 25
    solar_score = 15 if building["Solar"] else 5
    budget_score = min(building["Budget"] / 2500000, 1) * 15

    priority = round(
        intensity_score + age_score +
        solar_score + budget_score, 1
    )

    if intensity >= 230:
        saving_rate = 0.30
    elif intensity >= 160:
        saving_rate = 0.23
    else:
        saving_rate = 0.15

    annual_saving = energy * saving_rate

    # Illustrative emission factor only
    emission_factor = 0.40
    avoided_tonnes = annual_saving * emission_factor / 1000

    return {
        "Priority": priority,
        "Intensity": round(intensity, 1),
        "SavingRate": saving_rate,
        "EnergySaved": round(annual_saving),
        "CO2Avoided": round(avoided_tonnes, 1)
    }


def assessment_table():
    records = []

    for building in st.session_state.buildings:
        result = calculate_assessment(building)

        records.append({
            "Building": building["Building"],
            "Type": building["Type"],
            "Priority score": result["Priority"],
            "Energy intensity": result["Intensity"],
            "Potential savings (kWh/year)": result["EnergySaved"],
            "Estimated CO2 avoided (t/year)": result["CO2Avoided"]
        })

    return pd.DataFrame(records).sort_values(
        "Priority score",
        ascending=False
    )


def money(value):
    return f"AED {value:,.0f}"


# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:
    st.markdown("## 🌿 RIZQ")
    st.caption("CLIMATE RETROFIT INTELLIGENCE")
    st.write("Prioritize buildings. Fund upgrades. Verify impact.")

    page = st.radio(
        "Explore the platform",
        [
            "Command Center",
            "Add Building",
            "AI-Assisted Assessment",
            "Funding Studio",
            "Green Jobs & Workers",
            "Impact Verification",
            "Projects & Reports",
            "Methodology & Testing"
        ]
    )

    st.divider()
    st.caption("INT305 • Software Engineering")
    st.caption("Academic prototype • Synthetic data")
    st.caption("Session-only demonstration")


# ==========================================
# HERO
# ==========================================

st.markdown("""
<div class="hero">
    <div class="eyebrow">
        SUSTAINABLE CITIES • SMART FUNDING • GREEN JOBS
    </div>
    <h1>RIZQ</h1>
    <p>
        AI-Assisted Climate Retrofit Funding & Green Jobs Platform
    </p>
    <span class="chip">Explainable prioritization</span>
    <span class="chip">Blended finance</span>
    <span class="chip">Verified impact workflow</span>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="notice">
    <b>ACADEMIC RESEARCH PROTOTYPE</b> —
    All building records, funding amounts, workers and
    impact estimates are synthetic. The assessment engine
    uses illustrative rules, not a trained AI model.
    No real financing, certification or verified
    environmental impact is provided.
</div>
""", unsafe_allow_html=True)


# ==========================================
# COMMAND CENTER
# ==========================================

if page == "Command Center":

    st.title("Climate Retrofit Command Center")
    st.markdown(
        '<div class="section-note">'
        'A unified view of sustainable buildings, '
        'retrofit investments and green employment.'
        '</div>',
        unsafe_allow_html=True
    )

    df = assessment_table()

    total_budget = sum(
        b["Budget"] for b in st.session_state.buildings
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Buildings assessed", len(df))
    c2.metric("Projects funded", len(st.session_state.projects))
    c3.metric("Potential project budgets", money(total_budget))
    c4.metric("Green workers", len(st.session_state.workers))

    st.divider()

    st.subheader("Explore RIZQ Solutions")

    image_columns = st.columns(4)

    image_items = [
        ("Smart Cities", "city.svg"),
        ("Building Retrofit", "retrofit.svg"),
        ("Solar Energy", "solar.svg"),
        ("Green Jobs", "workers.svg")
    ]

    for col, (title, filename) in zip(
        image_columns, image_items
    ):
        with col:
            show_solution_card(title, filename)

    st.divider()

    left, right = st.columns([1.5, 1])

    with left:
        st.subheader("Building Priority Ranking")

        chart = px.bar(
            df,
            x="Building",
            y="Priority score",
            color="Priority score",
            color_continuous_scale="Greens",
            title="Illustrative retrofit priority"
        )

        chart.update_layout(
            plot_bgcolor="white",
            paper_bgcolor="white",
            xaxis_tickangle=-20
        )

        st.plotly_chart(chart, use_container_width=True)

    with right:
        st.subheader("Building Portfolio")

        types = pd.DataFrame(
            st.session_state.buildings
        )["Type"].value_counts().reset_index()

        types.columns = ["Type", "Count"]

        pie = px.pie(
            types,
            names="Type",
            values="Count",
            hole=0.58,
            color_discrete_sequence=px.colors.sequential.Greens
        )

        st.plotly_chart(pie, use_container_width=True)

    st.subheader("Retrofit Opportunity Overview")
    st.dataframe(df, use_container_width=True, hide_index=True)


# ==========================================
# ADD BUILDING
# ==========================================

elif page == "Add Building":

    st.title("Register a Building")
    st.write(
        "Create a synthetic building profile for "
        "retrofit assessment."
    )

    show_image("city.svg")

    with st.form("add_building_form"):

        name = st.text_input(
            "Building name",
            placeholder="Example: Sustainable Innovation Center"
        )

        kind = st.selectbox(
            "Building type",
            [
                "Residential",
                "Commercial",
                "Education",
                "Healthcare",
                "Government",
                "Industrial"
            ]
        )

        c1, c2 = st.columns(2)

        with c1:
            area = st.number_input(
                "Floor area (m²)",
                min_value=100,
                value=5000
            )

            energy = st.number_input(
                "Annual electricity consumption (kWh)",
                min_value=0,
                value=900000
            )

        with c2:
            age = st.number_input(
                "Building age (years)",
                min_value=0,
                value=15
            )

            budget = st.number_input(
                "Available retrofit budget (AED)",
                min_value=0,
                value=500000,
                step=50000
            )

        solar = st.checkbox(
            "Building is suitable for solar assessment",
            value=True
        )

        submitted = st.form_submit_button(
            "Add building",
            type="primary"
        )

    if submitted:
        if not name.strip():
            st.error("Please enter a building name.")
        elif any(
            b["Building"].lower() == name.strip().lower()
            for b in st.session_state.buildings
        ):
            st.error("A building with this name already exists.")
        else:
            st.session_state.buildings.append({
                "Building": name.strip(),
                "Type": kind,
                "Area": area,
                "Energy": energy,
                "Age": age,
                "Budget": budget,
                "Solar": solar,
                "Status": "Assessment ready"
            })

            st.success("Building successfully added!")


# ==========================================
# ASSESSMENT
# ==========================================

elif page == "AI-Assisted Assessment":

    st.title("AI-Assisted Retrofit Assessment")
    st.write(
        "Transparent rule-based screening for "
        "building retrofit opportunities."
    )

    show_image("retrofit.svg")

    names = [
        b["Building"] for b in st.session_state.buildings
    ]

    selected = st.selectbox("Select building", names)

    building = next(
        b for b in st.session_state.buildings
        if b["Building"] == selected
    )

    result = calculate_assessment(building)

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Priority score",
        f'{result["Priority"]}/100'
    )

    c2.metric(
        "Energy intensity",
        f'{result["Intensity"]} kWh/m²'
    )

    c3.metric(
        "Illustrative energy reduction",
        f'{result["SavingRate"]:.0%}'
    )

    st.progress(result["Priority"] / 100)

    st.subheader("Suggested Retrofit Measures")

    measures = [
        "High-efficiency HVAC upgrades",
        "LED lighting and occupancy sensors",
        "Building energy monitoring",
        "Improved insulation and glazing"
    ]

    if building["Solar"]:
        measures.append("Rooftop solar feasibility study")

    for item in measures:
        st.write("✓", item)

    st.subheader("Explainable Decision")

    st.info(
        f"{selected} received a priority score of "
        f'{result["Priority"]}/100 based on its energy '
        "intensity, building age, solar suitability "
        "and indicative budget. This is an illustrative "
        "screening score, not an AI prediction."
    )

    st.metric(
        "Potential annual electricity savings",
        f'{result["EnergySaved"]:,.0f} kWh'
    )

    st.caption(
        "Actual savings require an energy audit, "
        "engineering design and measured baseline."
    )


# ==========================================
# FUNDING STUDIO
# ==========================================

elif page == "Funding Studio":

    st.title("Smart Funding Studio")
    st.write(
        "Explore illustrative blended-finance scenarios "
        "for building retrofit projects."
    )

    show_image("solar.svg")

    selected = st.selectbox(
        "Select building",
        [b["Building"] for b in st.session_state.buildings]
    )

    building = next(
        b for b in st.session_state.buildings
        if b["Building"] == selected
    )

    cost = st.number_input(
        "Estimated retrofit cost (AED)",
        min_value=10000,
        value=int(max(building["Budget"], 10000)),
        step=10000
    )

    grant_pct = st.slider(
        "Grant contribution (%)",
        0, 80, 30
    )

    loan_pct = st.slider(
        "Green loan contribution (%)",
        0, 90, 45
    )

    if grant_pct + loan_pct > 100:
        st.error(
            "Grant and loan contributions cannot exceed 100%."
        )
    else:
        grant = cost * grant_pct / 100
        loan = cost * loan_pct / 100
        owner = cost - grant - loan

        c1, c2, c3 = st.columns(3)

        c1.metric("Grant", money(grant))
        c2.metric("Green loan", money(loan))
        c3.metric("Owner contribution", money(owner))

        finance_df = pd.DataFrame({
            "Source": [
                "Grant",
                "Green loan",
                "Building owner"
            ],
            "Amount": [grant, loan, owner]
        })

        fig = px.pie(
            finance_df,
            names="Source",
            values="Amount",
            hole=0.55,
            color_discrete_sequence=[
                "#176a4d", "#66a98b", "#c6e7d6"
            ]
        )

        st.plotly_chart(fig, use_container_width=True)

        if st.button(
            "Save simulated funding scenario",
            type="primary"
        ):
            st.session_state.projects.append({
                "Building": selected,
                "Cost": cost,
                "Grant": grant,
                "Loan": loan,
                "Owner": owner,
                "Date": str(date.today()),
                "Status": "Simulated — not funded"
            })

            st.success(
                "Funding scenario saved in this session."
            )

    st.caption(
        "No grant, loan or financial eligibility "
        "is approved or offered by this prototype."
    )


# ==========================================
# GREEN JOBS
# ==========================================

elif page == "Green Jobs & Workers":

    st.title("Green Jobs & Workforce")
    st.write(
        "Connect retrofit activities with "
        "the skills needed for implementation."
    )

    show_image("workers.svg")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Registered workers",
        len(st.session_state.workers)
    )

    c2.metric(
        "Available workers",
        sum(
            1 for w in st.session_state.workers
            if w["Available"]
        )
    )

    c3.metric(
        "Skill categories",
        len(set(
            w["Skill"] for w in st.session_state.workers
        ))
    )

    st.subheader("Workforce Directory")

    st.dataframe(
        pd.DataFrame(st.session_state.workers),
        use_container_width=True,
        hide_index=True
    )

    st.subheader("Register a Green Worker")

    with st.form("worker_form"):

        worker_name = st.text_input("Worker name")

        skill = st.selectbox(
            "Specialization",
            [
                "Solar PV",
                "HVAC",
                "Energy Auditing",
                "Building Automation",
                "Electrical Retrofit",
                "Insulation"
            ]
        )

        available = st.checkbox(
            "Available for assignments",
            value=True
        )

        if st.form_submit_button(
            "Add worker",
            type="primary"
        ):
            if worker_name.strip():
                st.session_state.workers.append({
                    "Name": worker_name.strip(),
                    "Skill": skill,
                    "Available": available
                })

                st.success("Worker registered.")
            else:
                st.error("Enter a worker name.")

    st.caption(
        "All worker profiles are fictional "
        "demonstration records."
    )


# ==========================================
# IMPACT VERIFICATION
# ==========================================

elif page == "Impact Verification":

    st.title("Impact Measurement & Verification")
    st.write(
        "Compare an illustrative baseline with "
        "a post-retrofit consumption scenario."
    )

    show_image("solar.svg")

    selected = st.selectbox(
        "Select building",
        [b["Building"] for b in st.session_state.buildings]
    )

    building = next(
        b for b in st.session_state.buildings
        if b["Building"] == selected
    )

    baseline = float(building["Energy"])

    measured = st.number_input(
        "Post-retrofit annual electricity (kWh)",
        min_value=0.0,
        value=float(round(baseline * 0.77)),
        step=1000.0
    )

    saved = baseline - measured

    reduction = (
        saved / baseline * 100 if baseline > 0 else 0
    )

    avoided = saved * 0.40 / 1000

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Electricity difference",
        f"{saved:,.0f} kWh"
    )

    c2.metric(
        "Change from baseline",
        f"{reduction:.1f}%"
    )

    c3.metric(
        "Illustrative CO₂ difference",
        f"{avoided:,.1f} t"
    )

    comparison = pd.DataFrame({
        "Scenario": ["Baseline", "Post-retrofit"],
        "Electricity (kWh)": [baseline, measured]
    })

    fig = px.bar(
        comparison,
        x="Scenario",
        y="Electricity (kWh)",
        color="Scenario",
        color_discrete_sequence=[
            "#a9c8bb", "#176a4d"
        ]
    )

    st.plotly_chart(fig, use_container_width=True)

    st.warning(
        "This is a demonstration calculation, not "
        "independently verified impact. Real verification "
        "requires metered data, normalization for weather "
        "and occupancy, and an approved M&V methodology."
    )


# ==========================================
# REPORTS
# ==========================================

elif page == "Projects & Reports":

    st.title("Projects & Reports")
    st.write(
        "Review building assessments and "
        "saved funding scenarios."
    )

    df = assessment_table()

    st.subheader("Building Assessment Report")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    st.download_button(
        "Download assessment CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="RIZQ_Building_Assessment.csv",
        mime="text/csv"
    )

    st.subheader("Funding Scenarios")

    if st.session_state.projects:
        projects_df = pd.DataFrame(
            st.session_state.projects
        )

        st.dataframe(
            projects_df,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Download funding scenarios CSV",
            data=projects_df.to_csv(
                index=False
            ).encode("utf-8"),
            file_name="RIZQ_Funding_Scenarios.csv",
            mime="text/csv"
        )
    else:
        st.info(
            "No funding scenarios saved yet. "
            "Create one in Funding Studio."
        )


# ==========================================
# METHODOLOGY
# ==========================================

elif page == "Methodology & Testing":

    st.title("Methodology & Testing")

    st.subheader("Prototype Architecture")

    st.markdown("""
    **Presentation layer:** Streamlit dashboard

    **Application layer:** Python business rules

    **Assessment layer:** Transparent weighted scoring

    **Finance layer:** User-controlled scenario calculations

    **Data layer:** Synthetic session-state records

    **Visualization:** Plotly charts and local SVG assets
    """)

    st.subheader("Current Prototype Capabilities")

    st.write("✓ Register synthetic building profiles")
    st.write("✓ Rank retrofit opportunities")
    st.write("✓ Explain assessment scores")
    st.write("✓ Simulate blended financing")
    st.write("✓ Register fictional green workers")
    st.write("✓ Compare energy scenarios")
    st.write("✓ Export assessment and funding reports")

    st.subheader("Important Limitations")

    st.warning(
        "The current prototype does not use a trained "
        "machine-learning model, live building sensors, "
        "real funding APIs, verified worker identities "
        "or accredited impact certification."
    )

    st.subheader("Future Development")

    st.markdown("""
    - Train and validate retrofit prediction models
      using authorized building datasets.
    - Add persistent database storage and authentication.
    - Integrate actual energy meter readings.
    - Connect to approved funding programs.
    - Introduce verified worker credentials.
    - Add formal measurement and verification workflows.
    """)

    st.subheader("Asset Diagnostics")

    for filename in [
        "city.svg",
        "retrofit.svg",
        "solar.svg",
        "workers.svg"
    ]:
        path = ASSETS / filename
        if path.exists():
            st.success(f"Found: assets/{filename}")
        else:
            st.error(f"Missing: assets/{filename}")


# ==========================================
# FOOTER
# ==========================================

st.divider()

st.caption(
    "RIZQ | Climate Retrofit Intelligence — "
    "INT305 Software Engineering Academic Prototype. "
    "All outputs are illustrative and require "
    "real-world validation before operational use."
)
