from pathlib import Path
from urllib.parse import unquote

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Education across Lebanon", page_icon="📊", layout="wide")

TEAL = "#087E8B"
AMBER = "#D97732"
DROP = "School dropout (%)"
ILL = "Illiteracy (%)"


def area_label(value):
    label = unquote(str(value).rsplit("/", 1)[-1]).replace("_", " ")
    try:
        label = label.encode("latin1").decode("utf8")
    except (UnicodeEncodeError, UnicodeDecodeError):
        pass
    return label


@st.cache_data
def load_data():
    data = pd.read_csv(Path(__file__).parent / "education.csv")
    data = data.rename(columns={
        "PercentageofSchooldropout": DROP,
        "PercentageofEducationlevelofresidents-illeterate": ILL,
    })
    data["Town"] = data["Town"].str.strip()
    data["Area"] = data["refArea"].map(area_label)
    for column in (DROP, ILL):
        data[column] = pd.to_numeric(data[column], errors="coerce")
        data[column + " invalid"] = data[column].notna() & ~data[column].between(0, 100)
        data.loc[data[column + " invalid"], column] = float("nan")
    return data


def style_chart(fig):
    fig.update_layout(
        template="plotly_white", height=400,
        margin=dict(l=15, r=20, t=25, b=35),
        font=dict(family="Arial", size=13, color="#253449"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(gridcolor="#E7EDF1", zeroline=False)
    return fig


data = load_data()
st.caption("MSBA 325 · DATA EXPLORER · 2023 SOURCE DATA")
st.title("Education across Lebanon")
st.markdown("Explore how reported **school dropout** varies across towns and how it relates to "
            "**illiteracy**. Start with the full dataset, then choose an area and its towns to inspect local patterns.")
st.caption("Based on the histogram and scatter plot in the supplied Plotly assignment. "
           "Source: Impact Open Data, via AUB CODEC’s Educational Level–Lebanon–2023 dataset.")

with st.container(border=True):
    st.subheader("Explore an area, then its towns", divider=False)
    c1, c2 = st.columns([1, 2])
    with c1:
        area = st.selectbox("1. Area", ["All areas"] + sorted(data["Area"].unique()), key="area")
    area_data = data if area == "All areas" else data[data["Area"] == area]
    towns = sorted(area_data["Town"].unique())
    # Changing the parent resets the child, preventing stale towns from another area.
    if st.session_state.get("previous_area") != area:
        st.session_state["towns"] = []
        st.session_state["previous_area"] = area
    with c2:
        selected = st.multiselect("2. Towns in this area", towns, key="towns",
                                  placeholder="All towns in the selected area",
                                  help="Leave empty to show every town in the area. Type to search, or select several towns.")
    st.caption(f"{len(towns):,} town choices available. Changing the area updates this list and resets the town selection. "
               "Area labels preserve the source’s mix of districts and governorates.")

view = area_data[area_data["Town"].isin(selected)] if selected else area_data
dropout = view.dropna(subset=[DROP])
pairs = view.dropna(subset=[DROP, ILL])
full_drop = data.dropna(subset=[DROP])
full_pairs = data.dropna(subset=[DROP, ILL])
scope = area if not selected else f"{area} · {len(selected)} selected town(s)"
st.caption(f"CURRENT VIEW: {scope}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Towns in view", f"{len(view):,}")
m2.metric("Reported dropout", f"{len(dropout):,} towns")
m3.metric("Median dropout", f"{dropout[DROP].median():.1f}%" if len(dropout) else "No data")
m4.metric("Complete pairs", f"{len(pairs):,} towns")

st.subheader("Two patterns in the full dataset")
a, b = st.columns(2)
under10 = int((full_drop[DROP] < 10).sum())
corr = full_pairs[ILL].corr(full_pairs[DROP])
with a:
    st.info(f"**Dropout is concentrated at lower values.** {under10:,} of {len(full_drop):,} reporting towns "
            f"({under10 / len(full_drop):.1%}) have dropout below 10%. "
            f"The median is {full_drop[DROP].median():.1f}%, while the mean is {full_drop[DROP].mean():.1f}%, "
            "consistent with a right tail of higher reported rates.")
with b:
    st.info(f"**Illiteracy and dropout have a weak positive association.** Pearson’s r is {corr:.2f} "
            f"across {len(full_pairs):,} towns with valid values for both measures. "
            "The spread of points means one measure does not reliably predict the other. Association does not establish causation.")
st.caption("These two insights describe all supplied towns with valid data and stay fixed as a reference. "
           "The charts and summaries below respond to both filters.")

left, right = st.columns(2)
with left:
    st.subheader("Where do dropout rates cluster?")
    st.caption("One observation per town · fixed 5-percentage-point bins")
    if dropout.empty:
        st.warning("No valid dropout values for this selection. Choose another town or clear the town filter.")
    else:
        fig = go.Figure(go.Histogram(x=dropout[DROP], xbins=dict(start=0, end=105, size=5),
                                    marker_color=TEAL,
                                    hovertemplate="Dropout bin: %{x}<br>Towns: %{y}<extra></extra>"))
        fig.update_layout(xaxis_title=DROP, yaxis_title="Number of towns", bargap=0.06)
        fig.update_xaxes(range=[-0.5, 105], ticksuffix="%", dtick=20)
        fig.update_yaxes(rangemode="tozero")
        st.plotly_chart(style_chart(fig), use_container_width=True, key="histogram")
        st.write(f"**In this view:** {(dropout[DROP] < 10).mean():.1%} of {len(dropout):,} reporting towns "
                 f"are below 10% dropout. Median: {dropout[DROP].median():.1f}%.")
with right:
    st.subheader("Does illiteracy track dropout?")
    st.caption("One point per town · hover for the town and exact values")
    if pairs.empty:
        st.warning("No towns have valid values for both measures in this selection.")
    else:
        fig = go.Figure(go.Scatter(x=pairs[ILL], y=pairs[DROP], mode="markers",
                                  customdata=pairs[["Town", "Area"]].to_numpy(),
                                  marker=dict(color=AMBER, size=9, opacity=0.65,
                                              line=dict(color="white", width=0.5)),
                                  hovertemplate="<b>%{customdata[0]}</b><br>%{customdata[1]}"
                                  "<br>Illiteracy: %{x:.1f}%<br>Dropout: %{y:.1f}%<extra></extra>"))
        fig.update_layout(xaxis_title=ILL, yaxis_title=DROP)
        fig.update_xaxes(range=[-2, 102], ticksuffix="%", dtick=20)
        fig.update_yaxes(range=[-2, 102], ticksuffix="%", dtick=20)
        st.plotly_chart(style_chart(fig), use_container_width=True, key="scatter")
        if len(pairs) >= 3 and pairs[ILL].nunique() > 1 and pairs[DROP].nunique() > 1:
            r = pairs[ILL].corr(pairs[DROP])
            st.write(f"**In this view:** Pearson’s r = {r:.2f} across {len(pairs):,} complete pairs. "
                     "Small selections can produce unstable correlations.")
        else:
            st.write("**In this view:** Correlation is not shown. It requires at least three complete towns "
                     "and variation in both measures.")

with st.expander("Why these interactions and charts?", expanded=False):
    st.markdown("""
**Interaction 1 — Area dropdown.** This answers: “What do education patterns look like in my area?”
A single-select dropdown keeps a long list of geographic labels compact, whereas radio buttons would
consume too much space. It provides context and reduces clutter through an overview-to-detail flow.
Selecting an area filters both charts and rebuilds the town options, so the second control is dependent on the first.

**Interaction 2 — Searchable town multiselect.** This answers: “Within that area, how do particular towns compare?”
A multiselect supports comparing several towns, while a single-town dropdown would remove that comparison.
A checkbox for every town would overwhelm the page. Only towns from the selected area appear, focusing
attention and enabling progressive drill-down. Empty selection means all towns in the area. Changing
area clears earlier town choices so unavailable towns cannot silently affect the view.

**Chart choices.** The histogram reveals concentration and the right tail without one bar per town.
The scatter plot uses position on two axes to reveal association, clusters and outliers. Fixed axes and
bin widths preserve context when filtering. Transparent points reduce overplotting, and hover details
provide exact values without covering the plot in labels. Plotly zoom can help inspect dense clusters.
""")

with st.expander("Data source, cleaning and limitations"):
    st.markdown("""
The app uses the supplied **Educational Level–Lebanon–2023** CSV, also used for slides 3 and 4
of the Plotly assignment. The separate water-resources file is not needed for this pair of education charts.
The dataset names 2023, while the export filename is dated September 5, 2024. It is not a live feed.

Publisher: **Impact Open Data**. [Source portal](https://impact.cib.gov.lb/home#open_data_section).
[Dataset identifier](http://linked.aub.edu.lb/CODEC/Lebanon/Dataset/Educational_Level-Lebanon-2023).

Town names are trimmed, geographic URI labels are made readable, and percentages outside 0–100 are
treated as invalid. Missing values stay missing, rather than becoming zero. Each histogram uses towns
with valid dropout values; the scatter plot and correlation use complete pairs. Invalid values in
unused education fields do not affect these charts. Raw data is preserved in the repository.

Areas mix district and governorate labels in the source. The app preserves these groups and does not
assume they are comparable administrative levels or reconstruct a geographic hierarchy. Every town
has equal weight: these summaries are **not population-weighted national rates**. Reporting coverage
varies, definitions and sampling details are not provided in the CSV, and town-level associations do
not establish relationships between individual residents or causation.
""")
    st.write(f"Source rows: {len(data):,}. Invalid dropout values: {int(data[DROP + ' invalid'].sum())}. "
             f"Invalid illiteracy values: {int(data[ILL + ' invalid'].sum())}.")
    st.write(f"Current selection: {len(view) - len(dropout):,} towns omitted from the histogram; "
             f"{len(view) - len(pairs):,} omitted from the scatter plot because required values are missing or invalid.")

with st.expander("Explore or download the selected data"):
    display = view[["Town", "Area", DROP, ILL]].sort_values(["Area", "Town"])
    st.dataframe(display, hide_index=True, use_container_width=True)
    st.download_button("Download selected towns (CSV)", display.to_csv(index=False).encode("utf-8"),
                       "selected_education.csv", "text/csv")

st.caption("MSBA 325 · Education across Lebanon · Built with Streamlit and Plotly")
