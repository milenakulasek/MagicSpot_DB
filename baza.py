import requests
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

st.set_page_config(initial_sidebar_state="expanded")

base_path = Path(__file__).resolve().parent

file_path = base_path / "ppGpp_baza.xlsx"
logo_path = base_path / "logo.jpg"

@st.cache_data
def load_data(path):
    return pd.read_excel(path)

df = load_data(file_path)

ppgpp_values = pd.to_numeric(df["ppGpp_mean"], errors="coerce").dropna()
ppgpp_default_min = float(ppgpp_values.min()) if not ppgpp_values.empty else 0.0
ppgpp_default_max = float(ppgpp_values.max()) if not ppgpp_values.empty else 0.0

FILTER_CONFIG = {
    'filter_instrumentation': 'instrumentation',
    'filter_internal_standard': 'internal_standard',
    'filter_species': 'species',
    'filter_kingdom': 'kingdom',
    'filter_genotype': 'genotype',
    'filter_organ': 'organ',
    'filter_growth': 'growth_scale',
    'filter_tr1': 'treatment_type1',
    'filter_tr2': 'treatment_type2'
}

for key, col in FILTER_CONFIG.items():
    if key not in st.session_state:
        st.session_state[key] = sorted(df[col].dropna().unique().tolist())

if "toggle_inducible" not in st.session_state:
    st.session_state["toggle_inducible"] = False
if "use_ppgpp_min" not in st.session_state:
    st.session_state["use_ppgpp_min"] = False
if "use_ppgpp_max" not in st.session_state:
    st.session_state["use_ppgpp_max"] = False
if "filter_ppgpp_min" not in st.session_state:
    st.session_state["filter_ppgpp_min"] = ppgpp_default_min
if "filter_ppgpp_max" not in st.session_state:
    st.session_state["filter_ppgpp_max"] = ppgpp_default_max


def build_doi_url(value):
    if pd.isna(value):
        return None

    doi_value = str(value).strip()
    if not doi_value:
        return None

    doi_value_lower = doi_value.lower()
    if doi_value_lower.startswith(("http://", "https://")):
        return doi_value

    # Normalize common DOI notations like "doi: 10.xxxx/..." or "doi.org/10.xxxx/..."
    doi_value = doi_value.replace(" ", "")
    doi_value_lower = doi_value.lower()
    if doi_value_lower.startswith("doi:"):
        doi_value = doi_value[4:]
    doi_value_lower = doi_value.lower()
    if doi_value_lower.startswith("doi.org/"):
        doi_value = doi_value[len("doi.org/"):]

    return f"https://doi.org/{doi_value}"


def reset_filters():
    for key, col in FILTER_CONFIG.items():
        st.session_state[key] = sorted(df[col].dropna().unique().tolist())
    st.session_state["toggle_inducible"] = False
    st.session_state["use_ppgpp_min"] = False
    st.session_state["use_ppgpp_max"] = False
    st.session_state["filter_ppgpp_min"] = ppgpp_default_min
    st.session_state["filter_ppgpp_max"] = ppgpp_default_max


with st.sidebar:
    st.markdown("""
        <style>
            /* 1. Sidebar background */
            [data-testid="stSidebar"] {
                background-color: #D3D3D3 !important;
            }

            /* 2. ROYALBLUE BUTTONS */
            div.stButton > button:first-child {
                background-color: royalblue !important;
                color: white !important;
                border: none !important;
                border-radius: 5px;
            }

            .ms-header {
                position: relative;
                padding: 25px 10px;
                margin-bottom: 8px;
                text-align: center;
                background: transparent;
                overflow: hidden;
            }

            .ms-header::before {
                content: '';
                position: absolute;
                bottom: 10%;
                left: 0;
                width: 100%;
                height: 160px;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='60' viewBox='0 0 300 60'%3E%3Cpath d='M0 58 L100 58 Q115 58 120 10 Q125 58 140 58 L180 58 Q190 58 195 35 Q200 58 210 58 L300 58' stroke='royalblue' stroke-width='1.5' fill='none'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: center;
                background-size: contain;
                z-index: 1;
            }

            .custom-title {
                font-family: "Segoe UI", sans-serif;
                margin: 0;
                font-size: 1.8em;
                font-weight: 800;
                color: royalblue;
                position: relative;
                z-index: 2;
                letter-spacing: -0.5px;
            }
            
            .profile-box {
                padding: 8px; 
                background-color: rgba(0, 0, 0, 0.8); 
                border-radius: 4px; 
                color: white;
                text-align: center;
                margin-top: 10px;
            }
        </style>

        <div class="ms-header">
            <h1 class='custom-title'>MagicSpot DB</h1>
        </div>            
    """, unsafe_allow_html=True)

total_records = len(df)
unique_articles = df['reference_DOI'].nunique()


with st.sidebar:
    st.markdown("**Compare ppGpp levels across:**")
    
    col_stat1, col_stat2, col_stat3  = st.columns(3)
    col_stat1.metric("Species", df['species'].nunique())
    col_stat2.metric("Articles", unique_articles)
    col_stat3.metric("Records", total_records)

    st.divider()

    on = st.toggle("Show data for inducible lines", key="toggle_inducible")

    st.button("Reset all filters", on_click=reset_filters)

    with st.expander("Analytical Method", expanded=True):
        options_inst = sorted(df["instrumentation"].dropna().unique().tolist())
        f_instrumentation = st.multiselect("Instrumentation:", 
            options=options_inst, 
            key="filter_instrumentation"
        )

        options_istd = sorted(df["internal_standard"].dropna().unique().tolist())
        f_internal_standard = st.multiselect("Internal standard:", 
            options=options_istd, 
            key="filter_internal_standard"
        )

    with st.expander("Biological Context", expanded=False):
            options_kingdom = sorted(df["kingdom"].dropna().unique().tolist())
            f_kingdom = st.multiselect("Kingdom:", 
                options=options_kingdom, 
                key="filter_kingdom"
            )

            options_species = sorted(df["species"].dropna().unique().tolist())
            f_species = st.multiselect("Species:", 
                options=options_species, 
                key="filter_species"
            )

            options_genotype = sorted(df["genotype"].dropna().unique().tolist())
            f_genotype = st.multiselect("Genotype:", 
                options=options_genotype, 
                key="filter_genotype"
            )

            options_organ = sorted(df["organ"].dropna().unique().tolist())
            f_organ = st.multiselect("Organ:", 
                options=options_organ, 
                key="filter_organ"
            )

            options_growth = sorted(df["growth_scale"].dropna().unique().tolist())
            f_growth = st.multiselect("Growth scale:", 
                options=options_growth, 
                key="filter_growth"
            )
            
    with st.expander("Treatment", expanded=False):
            options_tr1 = sorted(df["treatment_type1"].dropna().unique().tolist())
            f_tr1 = st.multiselect("Treatment type 1:", 
                options=options_tr1, 
                key="filter_tr1")

            options_tr2 = sorted(df["treatment_type2"].dropna().unique().tolist())
            f_tr2 = st.multiselect("Treatment type 2:", 
                options=options_tr2, 
                key="filter_tr2")  

    with st.expander("ppGpp Level", expanded=False):
            st.checkbox("Use minimum level", key="use_ppgpp_min")
            st.number_input(
                "Min ppGpp level:",
                key="filter_ppgpp_min",
                format="%.4f"
            )
            st.checkbox("Use maximum level", key="use_ppgpp_max")
            st.number_input(
                "Max ppGpp level:",
                key="filter_ppgpp_max",
                format="%.4f"
            )


filters = {
    'kingdom': f_kingdom,
    'species': f_species,
    'instrumentation': f_instrumentation,
    'internal_standard': f_internal_standard,
    'genotype': f_genotype,
    'organ': f_organ,
    'growth_scale': f_growth,
    'treatment_type1': f_tr1,
    'treatment_type2': f_tr2
}

mask = pd.Series(True, index=df.index)

# 2. Loop through your filters dictionary
# This replaces that giant block of & & & & &
for col, vals in filters.items():
    if vals:
        mask &= df[col].isin(vals)

ppgpp_mean_numeric = pd.to_numeric(df["ppGpp_mean"], errors="coerce")
active_min = st.session_state["filter_ppgpp_min"] if st.session_state.get("use_ppgpp_min", False) else None
active_max = st.session_state["filter_ppgpp_max"] if st.session_state.get("use_ppgpp_max", False) else None

if active_min is not None and active_max is not None and active_min > active_max:
    active_min, active_max = active_max, active_min

if active_min is not None:
    mask &= ppgpp_mean_numeric >= active_min

if active_max is not None:
    mask &= ppgpp_mean_numeric <= active_max

# 3. Apply the Toggle filter LAST
# This is the "Gatekeeper"
if not st.session_state.get("toggle_inducible", False):
    mask &= (df['is_inducible'] == "no")

# 4. Create your filtered dataframe
df_filtered = df[mask]

st.markdown("""
    <style>
    .nav-collapse-toggle {
        position: absolute;
        opacity: 0;
        pointer-events: none;
    }

    .nav-shell {
        position: fixed;
        top: clamp(3.25rem, 7vh, 4.25rem);
        left: 50%;
        right: auto;
        transform: translateX(-50%);
        width: min(920px, calc(100vw - 2rem));
        z-index: 999;
        display: flex;
        align-items: center;
        overflow: visible;
    }

    /* Keep nav in the main-content area when sidebar is open */
    @media (min-width: 1100px) {
        .nav-shell {
            left: calc(22.5rem + (100vw - 22.5rem) / 2);
            right: auto;
            transform: translateX(-50%);
            width: min(920px, calc(100vw - 23.5rem));
        }
    }

    .nav-collapse-toggle:checked + .nav-shell {
        width: 2.35rem;
        right: 1rem;
        left: auto;
        transform: none;
    }

    .nav-handle {
        width: 2.35rem;
        height: 2.1rem;
        align-self: center;
        border: 1px solid #0a66c2;
        border-left: none;
        border-radius: 0 10px 10px 0;
        background: linear-gradient(135deg, #0a66c2 0%, #0858a8 100%);
        box-shadow: 0 6px 14px rgba(10, 102, 194, 0.35);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        color: #ffffff;
        font-size: 1rem;
        font-weight: 700;
        user-select: none;
    }

    .nav-handle::before {
        content: "\\00BB";
    }

    .nav-collapse-toggle:checked + .nav-shell .nav-handle::before {
        content: "\\00AB";
    }

    .nav-handle::after {
        content: "Hide menu";
        position: absolute;
        left: calc(100% + 8px);
        right: auto;
        top: 50%;
        transform: translateY(-50%);
        background: #0f2a56;
        color: #ffffff;
        padding: 5px 8px;
        border-radius: 6px;
        font-size: 0.75rem;
        font-weight: 600;
        white-space: nowrap;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.15s ease;
        z-index: 1000;
    }

    .nav-handle:hover::after {
        opacity: 1;
    }

    .nav-collapse-toggle:checked + .nav-shell .nav-handle::after {
        content: "Show menu";
        left: auto;
        right: calc(100% + 8px);
    }

    .nav-collapse-toggle:checked + .nav-shell .nav-container {
        display: none;
        width: 0;
        padding: 0;
        border: 0;
        opacity: 0;
        pointer-events: none;
    }

    .nav-container {
        flex: 1;
        display: flex;
        gap: 12px;
        justify-content: center;
        margin: 0;
        padding: 0 12px;
        position: relative;
        flex-wrap: wrap;
    }

    .nav-container::before {
        content: "";
        position: absolute;
        left: 0;
        right: 0;
        top: 50%;
        height: 54%;
        transform: translateY(-50%);
        border: 1px solid rgba(10, 102, 194, 0.55);
        border-right: none;
        border-radius: 12px 0 0 12px;
        background: linear-gradient(135deg, rgba(10, 102, 194, 0.42) 0%, rgba(8, 88, 168, 0.42) 100%);
        backdrop-filter: blur(6px);
        -webkit-backdrop-filter: blur(6px);
        box-shadow: 0 6px 18px rgba(10, 102, 194, 0.28);
        z-index: 0;
        pointer-events: none;
    }

    .nav-container > * {
        position: relative;
        z-index: 1;
    }

    /* Prevent fixed nav from overlapping section headers */
    .main .block-container {
        padding-top: clamp(8.5rem, 16vh, 10.5rem);
    }

    /* Keep section jumps and first heading visible below fixed nav */
    #top,
    #About,
    #Visualisation,
    #Tabular,
    #Cite,
    #Contact {
        scroll-margin-top: clamp(8.5rem, 16vh, 10.5rem);
    }

    h2 {
        scroll-margin-top: clamp(8.5rem, 16vh, 10.5rem);
    }
    
    .nav-card {
        text-decoration: none !important;
        color: #0f2a56 !important;
        background: linear-gradient(135deg, #ffffff 0%, #f0f7ff 100%);
        border: 2px solid #c7dbff;
        padding: 14px 20px;
        border-radius: 12px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.2s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .nav-card:hover {
        background: linear-gradient(135deg, #0a66c2 0%, #0858a8 100%);
        color: white !important;
        border-color: #0a66c2;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(10, 102, 194, 0.25);
    }
    
    .nav-icon {
        font-size: 1.1rem;
        line-height: 1;
    }
    
    .back-to-top {
        text-align: center;
        margin: 20px 0;
    }
    
    .back-to-top a {
        text-decoration: none !important;
        color: #0a66c2 !important;
        font-size: 0.9rem;
        font-weight: 600;
        padding: 8px 16px;
        border: 1px solid #c7dbff;
        border-radius: 8px;
        display: inline-block;
        transition: all 0.2s ease;
    }
    
    .back-to-top a:hover {
        background: #0a66c2;
        color: white !important;
        border-color: #0a66c2;
    }
    </style>
    
    <div id="top"></div>
    <input type="checkbox" id="nav-collapse" class="nav-collapse-toggle">
    <div class="nav-shell">
        <div class="nav-container">
        <a class="nav-card" href="#About">
            <span>About</span>
        </a>
        <a class="nav-card" href="#Visualisation">
            <span>Visualisations</span>
        </a>
        <a class="nav-card" href="#Tabular">
            <span>Data Details</span>
        </a>
        <a class="nav-card" href="#Cite">
            <span>How to Cite</span>
        </a>
        <a class="nav-card" href="#Contact">
            <span>Contact</span>
        </a>
        </div>
        <label for="nav-collapse" class="nav-handle" title="Hide menu"></label>
    </div>
""", unsafe_allow_html=True)

st.markdown("<div id='About'></div>", unsafe_allow_html=True)
st.markdown("## About")
st.markdown("""
This database was developed to keep pace with the rapidly expanding body of data regarding ppGpp levels in _Eukaryotes_. Born out of a practical need for a centralized "fast-check" resource, it serves as a hub for researchers to quickly access and contextualize their data.
It provides a curated collection of measurements extracted from peer-reviewed literature.

**Features:**
- Filter by species, genotype, organ, growth conditions, and treatments
- Add your own data points temporarily to compare with literature values
- Download filtered data in CSV format
- Export forest plot visualization using the camera icon

**Please, note:**
- The data is collected from various sources and the conditions may differ significantly. Always refer to the original papers for detailed experimental context and methodologies.
- In some cases, where raw data was not available, values were estimated from figures using WebPlotDigitizer. These are marked in the dataset (details section) and should be interpreted with caution.
- The data for **inducible lines** is hidden by default, as they usually show very high ppGpp levels upon induction, which can skew the overall view. You can enable them using the toggle in the sidebar.
""")

st.markdown('<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>', unsafe_allow_html=True)

st.markdown("<div id='Visualisation'></div>", unsafe_allow_html=True)
st.markdown("## Data visualisation")

if 'manual_points' not in st.session_state:
    st.session_state.manual_points = []

with st.container(border=True):
    st.caption("➕ Add your own data points (temporary, not saved)")
    col1, col2, col3, col4, col5 = st.columns([1.5, 1.5, 2, 1.2, 1.2])
    
    with col1:
        manual_mean = st.number_input("Mean:", value=0.0, format="%.2f", key="manual_mean")
    with col2:
        manual_sd = st.number_input("SD:", value=0.0, format="%.2f", key="manual_sd")
    with col3:
        manual_label = st.text_input("Label:", value="My Data", key="manual_label")
    with col4:
        st.write(" ")
        add_manual = st.button("Add point", use_container_width=True)
    with col5:
        st.write(" ")
        clear_manual = st.button("Clear all", use_container_width=True)

if add_manual:
    st.session_state.manual_points.append({
        'ppGpp_mean': manual_mean,
        'ppGpp_sd': manual_sd,
        'label': manual_label
    })
    st.rerun()

if clear_manual:
    st.session_state.manual_points = []
    st.rerun()

if st.session_state.manual_points:
    st.write("---")
    st.subheader("Manual Data Points")
    
    hcol1, hcol2, hcol3, hcol4 = st.columns([1.5, 1.5, 2, 0.5])
    hcol1.write("**Mean**")
    hcol2.write("**SD**")
    hcol3.write("**Label**")
    hcol4.write("")

    for i, point in enumerate(st.session_state.manual_points):
        rcol1, rcol2, rcol3, rcol4 = st.columns([1.5, 1.5, 2, 0.5])
        
        rcol1.write(f"{point['ppGpp_mean']:.2f}")
        rcol2.write(f"{point['ppGpp_sd']:.2f}")
        rcol3.write(point['label'])
        
        if rcol4.button("🗑️", key=f"delete_{i}"):
            st.session_state.manual_points.pop(i)
            st.rerun()
else:
    st.info("No manual points added yet.")

if st.session_state.manual_points:
    st.caption(f"✓ Added {len(st.session_state.manual_points)} point(s)")

sort_choice = st.radio(
    "Sort Forest Plot by:",
    options=["Study", "Value", "Species"],
    horizontal=True,
    key="chart_sort_tick"
)

df_filtered['y_label'] = (
    df_filtered['species_short'] + " [" + 
    df_filtered['genotype'] + "] " + 
    df_filtered['organ'] + " - " + 
    df_filtered['treatment_type1'] + " - " +
    df_filtered['treatment_type2'] + " - " +
    df_filtered['treatment_value']
)



dynamic_height = 300 + ((len(df_filtered) + len(st.session_state.manual_points)) * 25)

if dynamic_height < 400:
    dynamic_height = 400

if not df_filtered.empty:
    if 'reference_DOI' in df_filtered.columns:
        df_filtered['reference_DOI_filled'] = df_filtered['reference_DOI'].fillna('No DOI')
    else:
        df_filtered['reference_DOI_filled'] = 'No DOI'

    if 'citation_short' in df_filtered.columns:
        def get_doi_label(row):
            citation = row['citation_short']
            if pd.notna(citation) and str(citation).strip() != '':
                return str(citation)
            return row['reference_DOI_filled']
        df_filtered['doi_label'] = df_filtered.apply(get_doi_label, axis=1)
    else:
        df_filtered['doi_label'] = df_filtered['reference_DOI_filled']

    unit_values = df_filtered['unit'].fillna('-').astype(str)

    plot_df = df_filtered[['ppGpp_mean', 'ppGpp_sd', 'y_label', 'species', 'doi_label', 'N', 'treatment_value', 'citation_short', 'reference_DOI']].copy()
    plot_df['unit_display'] = unit_values
    plot_df['data_type'] = 'literature'

    if st.session_state.manual_points:
        for i, point in enumerate(st.session_state.manual_points):
            manual_row = {
                'ppGpp_mean': point['ppGpp_mean'],
                'ppGpp_sd': point['ppGpp_sd'],
                'y_label': point['label'],
                'species': 'Your Data',
                'doi_label': point['label'],
                'N': 1,
                'treatment_value': '-',
                'unit_display': '-',
                'citation_short': point['label'],
                'reference_DOI': '',
                'data_type': 'manual'
            }
            plot_df = pd.concat([plot_df, pd.DataFrame([manual_row])], ignore_index=True)

    fig = px.scatter(
        plot_df,
        x="ppGpp_mean",
        y="y_label",
        error_x="ppGpp_sd",
        color='doi_label',
        symbol='species',
        custom_data=["ppGpp_sd", "unit_display", "N", "treatment_value", "citation_short", "data_type"],
        title="Forest Plot of ppGpp Levels"
    )

    fig.update_traces(
        hovertemplate=(
            "<b>%{y}</b><br>"
            "Value +- SD: %{x:.2f} +- %{customdata[0]:.2f}<br>"
            "Unit: %{customdata[1]}<br>"
            "N: %{customdata[2]}<br>"
            "Treatment value: %{customdata[3]}<br>"
            "Study: %{customdata[4]}<br>"
            "Data type: %{customdata[5]}"
            "<extra></extra>"
        )
    )

if sort_choice == "Species":
    sorted_df = plot_df.sort_values(['species', 'citation_short', 'y_label'], ascending=True)
elif sort_choice == "Value":
    sorted_df = plot_df.sort_values(['ppGpp_mean', 'species', 'citation_short', 'y_label'], ascending=[True, True, True, True])
elif sort_choice == "Study":
    sorted_df = plot_df.sort_values(['citation_short', 'species', 'y_label'], ascending=True)
else:
    sorted_df = plot_df.copy()


log_choice = st.radio(
    "Set x-axis scale:",
    options=["Log", "Linear"],
    horizontal=True,
    key="chart_log_tick"
)


if log_choice == "Linear":
    fig.update_xaxes(type="linear")
else:
    fig.update_xaxes(type="log")


ordered_labels = sorted_df['y_label'].unique().tolist()

fig.update_layout(
    template="plotly_white",
    yaxis={
        'categoryorder': 'array',
        'categoryarray': ordered_labels,
        'automargin': True,
        'range': [-0.5, len(ordered_labels) - 0.5]
    },
    xaxis={
        'side': 'bottom',
        'zeroline': True,
        'zerolinecolor': '#eee',
        'rangemode': 'tozero',
        'showline': True,
        'ticks': 'outside',
        'showticklabels': True
    },
    height=max(dynamic_height, 400),
    yaxis_title='',
    xaxis_title='ppGpp Level (pmol/g tissue)',
    margin=dict(l=10, r=10, t=30, b=40),
    legend=dict(
        title_text='Reference | Species',
        orientation='h',
        y=1.02,
        x=0.5,
        xanchor='center',
        yanchor='bottom'
    )
)

with st.container(border=True):
    st.plotly_chart(fig, use_container_width=True)

st.markdown(f"""
**Records in current view:** {len(df_filtered)}
""")

st.markdown('<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>', unsafe_allow_html=True)

st.markdown("<div id='Tabular'></div>", unsafe_allow_html=True)
st.markdown("## Data details")
st.dataframe(df_filtered)

st.markdown('<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>', unsafe_allow_html=True)

current_host = st.context.headers.get("host", "URL pending")
full_url = f"https://{current_host}"
access_date = datetime.now().strftime("%d %b %y")

st.markdown("<div id='Cite'></div>", unsafe_allow_html=True)
st.markdown("## How to Cite")

st.markdown("""
If you use this data, please cite the **original experimental papers** (the following list is automatically adjusted to the current filters and shows only the relevant references):
""")
if 'reference_DOI' in df_filtered.columns and not df_filtered.empty:
    unique_refs = (
        df_filtered[['reference_DOI', 'citation_short']]
        .dropna(subset=['reference_DOI'])
        .drop_duplicates(subset=['reference_DOI'])
    )

    if not unique_refs.empty:
        seen_titles = {}
        link_items = []
        for _, row in unique_refs.iterrows():
            doi_url = build_doi_url(row['reference_DOI'])
            title = row['citation_short'] if pd.notna(row.get('citation_short')) else str(row['reference_DOI']).strip()
            if doi_url:
                title_count = seen_titles.get(title, 0)
                seen_titles[title] = title_count + 1
                button_title = title if title_count == 0 else f"{title} ({title_count + 1})"
                link_items.append((button_title, doi_url))

        if link_items:
            inline_links = " | ".join([f"[{title}]({url})" for title, url in link_items])
            st.markdown(inline_links)

st.markdown("and the **database**:")
    
citation_text = f"Milena Kulasek (2026). MagicSpot DB. Department of Genetics, Nicolaus Copernicus University in Toruń. Available at: {full_url} (Accessed: {access_date})."
    
st.code(citation_text, language="text")
    
st.caption("Manuscript in preparation.")

st.markdown('<div class="back-to-top"><a href="#top">↑ Back to Top</a></div>', unsafe_allow_html=True)

st.markdown("<div id='Contact'></div>", unsafe_allow_html=True)
st.markdown("## Contact & Collaboration")

st.markdown("""
<style>
    .contact-card {
        border: 1px solid #d8e2f2;
        border-left: 6px solid #4169e1;
        border-radius: 12px;
        padding: 16px 18px;
        background: linear-gradient(135deg, #f7faff 0%, #edf3ff 100%);
        margin: 8px 0 14px 0;
    }

    .contact-title {
        font-weight: 700;
        color: #19335e;
        margin-bottom: 6px;
    }

    .contact-body {
        color: #1f2937;
        line-height: 1.55;
        margin-bottom: 0;
    }

    .contact-mail-btn {
        display: block;
        text-decoration: none !important;
        background-color: #0a66c2;
        color: white !important;
        font-weight: 600;
        border-radius: 10px;
        padding: 10px 14px;
        margin-top: 0;
        width: 100%;
        text-align: center;
        box-sizing: border-box;
    }

    .contact-mail-btn:hover {
        background-color: #004a99;
    }

    .data-callout {
        border-radius: 12px;
        border: 1px solid #c7dbff;
        background: linear-gradient(135deg, #eaf2ff 0%, #dce9ff 100%);
        padding: 12px 14px;
        margin: 8px 0 14px 0;
        color: #0f2a56;
        font-size: 1rem;
        line-height: 1.45;
    }

    .action-card {
        border: 1px solid #d8e2f2;
        border-radius: 12px;
        background: #ffffff;
        padding: 12px;
        min-height: 138px;
    }

    .action-step {
        font-size: 0.84rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #49638a;
        margin-bottom: 4px;
        font-weight: 700;
    }

    .action-title {
        font-size: 1rem;
        font-weight: 700;
        color: #163866;
        margin-bottom: 8px;
    }

    .action-desc {
        margin-top: 10px;
        margin-bottom: 0;
        color: #475569;
        font-size: 0.92rem;
        line-height: 1.45;
        min-height: 44px;
    }

    .contact-actions div[data-testid="stVerticalBlockBorderWrapper"] {
        min-height: 190px;
    }

    .contact-actions .contact-mail-btn,
    .contact-actions div.stDownloadButton > button {
        min-height: 42px;
    }

    div.stDownloadButton {
        margin-top: 0 !important;
        margin-bottom: 0 !important;
    }

    div.stDownloadButton > button {
        background-color: #0a66c2 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px;
        width: 100%;
        margin-top: 0 !important;
    }

    div.stDownloadButton > button:hover {
        background-color: #004a99 !important;
        color: white !important;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])

with col1:
    st.image("LC_MS_MS.jpg", caption="UHPLC-ESI-MS/MS platform", use_container_width=True)

with col2:
    st.markdown("""
    <div class="contact-card">
        <div class="contact-title">Work with our team</div>
        <p class="contact-body">
            We are not only creators and maintainers of this database; we are active researchers
            dedicated to advancing the field of ppGpp signaling.       
            Our team specializes in the precise measurement and analysis of alarmones using
            UHPLC-MS/MS protocols integrated with internal standards (ISTD), ensuring high data quality,
            precision, and reproducibility.
        </p><p class="contact-body">        
            We are open to collaborations, data contributions, and discussions on ppGpp research. Please don't hesitate to reach out if you are interested!
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="data-callout">
<strong>Found new data?</strong> Help expand MagicSpot DB by submitting your measurements.
Use the template below and email it to us with experimental context. After a quality check,
your contribution can be integrated into the public dataset.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="contact-actions">', unsafe_allow_html=True)

contact_col1, contact_col2 = st.columns(2)

file_form_path = "ppGpp_form.xlsx"

with contact_col1:
    with st.container(border=True):
        st.markdown('<div class="action-step">Step 1</div>', unsafe_allow_html=True)
        st.markdown('<div class="action-title">Download Template</div>', unsafe_allow_html=True)

        with open(file_form_path, "rb") as file:
            btn = st.download_button(
                label="Download ppGpp Template",
                data=file,
                file_name="ppGpp_form.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        st.markdown(
            '<p class="action-desc">Fill in your measurements using the template fields before submitting. Please, note, only the data from published articles will be considered.</p>',
            unsafe_allow_html=True,
        )

    if btn:
        st.success("Download started!")

with contact_col2:
    with st.container(border=True):
        st.markdown('<div class="action-step">Step 2</div>', unsafe_allow_html=True)
        st.markdown('<div class="action-title">Send By Email</div>', unsafe_allow_html=True)
        st.markdown(
            '<a class="contact-mail-btn" href="mailto:milena.kulasek@umk.pl?subject=MagicSpot%20DB%20Contribution">Email Milena Kulasek</a>',
            unsafe_allow_html=True,
        )
        st.markdown(
            '<p class="action-desc">Attach your completed template and any experimental notes.</p>',
            unsafe_allow_html=True,
        )

st.markdown('</div>', unsafe_allow_html=True)

st.write("---")

footer_col1, footer_col2, footer_col3 = st.columns([1, 4, 1])

with footer_col2:
    st.markdown(
        """
        <div style="text-align: center; color: #475569; border: 1px solid #e2e8f0; border-radius: 12px; background: #f8fbff; padding: 12px 14px;">
            <p style="margin-bottom: 6px; color: #334155;">
                Created and maintained by <strong>Milena Kulasek</strong> |
                <a href="mailto:milena.kulasek@umk.pl" style="color: #0a66c2; text-decoration: none;">milena.kulasek@umk.pl</a>
            </p>
            <p style="font-size: 0.85em; margin-bottom: 0;">
                © 2026 Department of Genetics, Nicolaus Copernicus University in Toruń, Poland
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )

