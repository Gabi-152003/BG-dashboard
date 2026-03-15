"""
Bulgaria High-Growth Firms Dashboard
ESI Monitor Style – Data Driven Entrepreneurship | WHU
-----------------------------------------------------
Requirements: pip install dash plotly pandas openpyxl
Run:          python dashboard_BG.py
Then open:    http://127.0.0.1:8050
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
import os

# ── 1. LOAD DATA ──────────────────────────────────────────────────────────────
# Make sure BG_with_variables.xlsx is in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
df = pd.read_excel(os.path.join(BASE_DIR, "BG_with_variables.xlsx"))

YEARS      = [2020, 2021, 2022, 2023, 2024]
CATEGORIES = [
    "Scaler", "HighGrowthFirm", "ConsistentHighGrowthFirm",
    "VeryHighGrowthFirm", "Gazelle", "Mature", "Scaleup", "Superstar"
]
LABELS = {
    "Scaler":                    "Scalers",
    "HighGrowthFirm":            "High-Growth Firms (HGFs)",
    "ConsistentHighGrowthFirm":  "Consistent HGFs",
    "VeryHighGrowthFirm":        "Consistent Hypergrowers",
    "Gazelle":                   "Gazelles",
    "Mature":                    "Mature HGFs",
    "Scaleup":                   "Scaleups",
    "Superstar":                 "Superstars",
}

# ESI colour palette
ESI_COLORS = ["#1a5e5b", "#2a8c87", "#3dbdb6", "#7dd4d0",
              "#a8e6e3", "#c8f0ee", "#e0f8f7", "#f0fcfb"]

ALL_INDUSTRIES = sorted(df["NACE Rev. 2 main section"].dropna().unique())
ALL_REGIONS    = sorted(df["Region in country clean"].dropna().unique())

# ── 2. HELPER: compute % per category for a subset ───────────────────────────
def compute_pct(subset, category, year):
    col  = f"{category} {year}"
    if col not in subset.columns:
        return None
    vals    = subset[col]
    n_ones  = (vals == 1).sum()
    n_valid = ((vals == 1) | (vals == 0)).sum()
    return round(n_ones / n_valid * 100, 2) if n_valid > 0 else None

# ── 3. APP LAYOUT ─────────────────────────────────────────────────────────────
app = Dash(__name__)
server = app.server
app.title = "Bulgaria High-Growth Monitor"

# Shared dropdown style
DD = {"backgroundColor": "#f0fcfb", "color": "#1a5e5b", "border": "1px solid #3dbdb6"}

app.layout = html.Div(style={"fontFamily": "Segoe UI, Arial, sans-serif",
                              "backgroundColor": "#f7fffe", "minHeight": "100vh"}, children=[

    # ── Header ──
    html.Div(style={"backgroundColor": "#1a5e5b", "padding": "24px 40px",
                    "display": "flex", "alignItems": "center", "gap": "20px"}, children=[
        html.H1("🇧🇬 Bulgaria High-Growth Firms Monitor",
                style={"color": "white", "margin": 0, "fontSize": "26px"}),
        html.Span("ESI Monitor Style | WHU Data Driven Entrepreneurship",
                  style={"color": "#7dd4d0", "fontSize": "14px"}),
    ]),

    # ── Tabs ──
    dcc.Tabs(id="tabs", value="tab-overview", style={"margin": "0 20px"},
             colors={"border": "#1a5e5b", "primary": "#1a5e5b", "background": "#e0f8f7"},
             children=[

        # ══ TAB 1 – OVERVIEW ══════════════════════════════════════════════════
        dcc.Tab(label="📊 Overview", value="tab-overview", children=[
            html.Div(style={"padding": "20px 40px"}, children=[

                html.H3("Evolution of Growth Metrics (2020–2024)",
                        style={"color": "#1a5e5b"}),

                # Controls
                html.Div(style={"display": "flex", "gap": "30px",
                                "marginBottom": "20px", "flexWrap": "wrap"}, children=[
                    html.Div([
                        html.Label("Metric:", style={"fontWeight": "bold",
                                                      "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="overview-category",
                            options=[{"label": LABELS[c], "value": c} for c in CATEGORIES],
                            value="Scaler",
                            style={"width": "280px", **DD}
                        )
                    ]),
                    html.Div([
                        html.Label("Display:", style={"fontWeight": "bold",
                                                       "color": "#1a5e5b"}),
                        dcc.RadioItems(
                            id="overview-display",
                            options=[{"label": " % of firms", "value": "pct"},
                                     {"label": " Absolute count", "value": "abs"}],
                            value="pct",
                            inline=True,
                            style={"marginTop": "6px"}
                        )
                    ]),
                ]),

                dcc.Graph(id="overview-bar"),

                # KPI cards
                html.Div(id="kpi-cards",
                         style={"display": "flex", "gap": "16px",
                                "flexWrap": "wrap", "marginTop": "20px"}),
            ])
        ]),

        # ══ TAB 2 – BY INDUSTRY ═══════════════════════════════════════════════
        dcc.Tab(label="🏭 By Industry", value="tab-industry", children=[
            html.Div(style={"padding": "20px 40px"}, children=[

                html.H3("Growth Metrics by Industry", style={"color": "#1a5e5b"}),

                html.Div(style={"display": "flex", "gap": "30px",
                                "marginBottom": "20px", "flexWrap": "wrap"}, children=[
                    html.Div([
                        html.Label("Year:", style={"fontWeight": "bold",
                                                    "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="industry-year",
                            options=[{"label": str(y), "value": y} for y in YEARS],
                            value=2023, style={"width": "120px", **DD}
                        )
                    ]),
                    html.Div([
                        html.Label("Metric:", style={"fontWeight": "bold",
                                                      "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="industry-category",
                            options=[{"label": LABELS[c], "value": c} for c in CATEGORIES],
                            value="Scaler", style={"width": "280px", **DD}
                        )
                    ]),
                ]),

                dcc.Graph(id="industry-bar"),
            ])
        ]),

        # ══ TAB 3 – BY REGION ═════════════════════════════════════════════════
        dcc.Tab(label="📍 By Region", value="tab-region", children=[
            html.Div(style={"padding": "20px 40px"}, children=[

                html.H3("Growth Metrics by Region", style={"color": "#1a5e5b"}),

                html.Div(style={"display": "flex", "gap": "30px",
                                "marginBottom": "20px", "flexWrap": "wrap"}, children=[
                    html.Div([
                        html.Label("Year:", style={"fontWeight": "bold",
                                                    "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="region-year",
                            options=[{"label": str(y), "value": y} for y in YEARS],
                            value=2023, style={"width": "120px", **DD}
                        )
                    ]),
                    html.Div([
                        html.Label("Metric:", style={"fontWeight": "bold",
                                                      "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="region-category",
                            options=[{"label": LABELS[c], "value": c} for c in CATEGORIES],
                            value="Scaler", style={"width": "280px", **DD}
                        )
                    ]),
                ]),

                dcc.Graph(id="region-bar"),
            ])
        ]),

        # ══ TAB 4 – COMPARE ═══════════════════════════════════════════════════
        dcc.Tab(label="🔍 Compare", value="tab-compare", children=[
            html.Div(style={"padding": "20px 40px"}, children=[

                html.H3("Compare Metrics Across Time", style={"color": "#1a5e5b"}),
                html.P("Select up to 4 metrics to compare their evolution side by side.",
                       style={"color": "#555"}),

                html.Div(style={"marginBottom": "20px"}, children=[
                    html.Label("Metrics to compare:",
                               style={"fontWeight": "bold", "color": "#1a5e5b"}),
                    dcc.Checklist(
                        id="compare-categories",
                        options=[{"label": f"  {LABELS[c]}", "value": c}
                                 for c in CATEGORIES],
                        value=["Scaler", "HighGrowthFirm",
                               "ConsistentHighGrowthFirm", "VeryHighGrowthFirm"],
                        inline=True,
                        style={"marginTop": "8px", "color": "#1a5e5b"}
                    )
                ]),

                dcc.Graph(id="compare-lines"),
            ])
        ]),

        # ══ TAB 5 – DATA TABLE ════════════════════════════════════════════════
        dcc.Tab(label="📋 Data Table", value="tab-table", children=[
            html.Div(style={"padding": "20px 40px"}, children=[

                html.H3("Explore Company Data", style={"color": "#1a5e5b"}),

                html.Div(style={"display": "flex", "gap": "20px",
                                "marginBottom": "16px", "flexWrap": "wrap"}, children=[
                    html.Div([
                        html.Label("Filter by Region:",
                                   style={"fontWeight": "bold", "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="table-region",
                            options=[{"label": "All", "value": "All"}] +
                                    [{"label": r, "value": r} for r in ALL_REGIONS],
                            value="All", style={"width": "200px", **DD}
                        )
                    ]),
                    html.Div([
                        html.Label("Filter by Industry:",
                                   style={"fontWeight": "bold", "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="table-industry",
                            options=[{"label": "All", "value": "All"}] +
                                    [{"label": i.split(" - ")[-1][:40], "value": i}
                                     for i in ALL_INDUSTRIES],
                            value="All", style={"width": "300px", **DD}
                        )
                    ]),
                    html.Div([
                        html.Label("Filter by Year (Scaler = 1):",
                                   style={"fontWeight": "bold", "color": "#1a5e5b"}),
                        dcc.Dropdown(
                            id="table-year",
                            options=[{"label": "No filter", "value": "none"}] +
                                    [{"label": str(y), "value": y} for y in YEARS],
                            value="none", style={"width": "150px", **DD}
                        )
                    ]),
                ]),

                html.Div(id="table-count",
                         style={"marginBottom": "10px", "color": "#555",
                                "fontSize": "14px"}),

                dash_table.DataTable(
                    id="data-table",
                    page_size=15,
                    sort_action="native",
                    filter_action="native",
                    style_header={
                        "backgroundColor": "#1a5e5b", "color": "white",
                        "fontWeight": "bold", "fontSize": "12px"
                    },
                    style_cell={
                        "fontSize": "12px", "padding": "6px",
                        "maxWidth": "200px", "overflow": "hidden",
                        "textOverflow": "ellipsis"
                    },
                    style_data_conditional=[
                        {"if": {"row_index": "odd"},
                         "backgroundColor": "#f0fcfb"}
                    ],
                ),
            ])
        ]),
    ]),

    # Footer
    html.Div(style={"textAlign": "center", "padding": "16px",
                    "color": "#888", "fontSize": "12px",
                    "borderTop": "1px solid #ccc", "marginTop": "20px"}, children=[
        "Bulgaria High-Growth Firms Monitor | WHU Data Driven Entrepreneurship | "
        "Data source: Orbis / Bureau van Dijk"
    ])
])


# ── 4. CALLBACKS ──────────────────────────────────────────────────────────────

# ── Tab 1: Overview bar + KPI cards ──
@app.callback(
    Output("overview-bar", "figure"),
    Output("kpi-cards", "children"),
    Input("overview-category", "value"),
    Input("overview-display", "value"),
)
def update_overview(category, display):
    pcts, counts = [], []
    for yr in YEARS:
        col   = f"{category} {yr}"
        vals  = df[col]
        n1    = (vals == 1).sum()
        nv    = ((vals == 1) | (vals == 0)).sum()
        pcts.append(round(n1 / nv * 100, 2) if nv > 0 else 0)
        counts.append(int(n1))

    y_vals = pcts if display == "pct" else counts
    y_label = "% of firms" if display == "pct" else "Number of firms"

    fig = go.Figure(go.Bar(
        x=[str(y) for y in YEARS],
        y=y_vals,
        marker_color=["#2a8c87" if v < max(y_vals) else "#1a5e5b"
                      for v in y_vals],
        text=[f"{v:.2f}%" if display == "pct" else str(v) for v in y_vals],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"{LABELS[category]} in Bulgaria (2020–2024)",
        yaxis_title=y_label,
        xaxis_title="Year",
        plot_bgcolor="white",
        paper_bgcolor="white",
        yaxis=dict(gridcolor="#e0f8f7"),
        font=dict(family="Segoe UI", color="#1a5e5b"),
        margin=dict(t=60, b=40),
    )

    # KPI cards: peak year and 2024 vs 2020 change
    peak_yr  = YEARS[y_vals.index(max(y_vals))]
    delta    = round(pcts[-1] - pcts[0], 2)
    delta_str = f"+{delta}%" if delta >= 0 else f"{delta}%"
    delta_col = "#1a5e5b" if delta >= 0 else "#c0392b"

    cards = [
        _kpi_card("2024 value", f"{pcts[-1]:.2f}%", f"{counts[-1]:,} firms"),
        _kpi_card("Peak year", str(peak_yr), f"{max(pcts):.2f}%"),
        _kpi_card("Change 2020→2024", delta_str, "percentage points",
                  color=delta_col),
        _kpi_card("Valid observations", f"{((df[f'{category} 2024']==1)|(df[f'{category} 2024']==0)).sum():,}",
                  "firms with complete data"),
    ]
    return fig, cards


def _kpi_card(title, value, subtitle, color="#1a5e5b"):
    return html.Div(style={
        "backgroundColor": "white", "border": f"2px solid {color}",
        "borderRadius": "10px", "padding": "16px 24px",
        "minWidth": "160px", "textAlign": "center",
        "boxShadow": "2px 2px 8px rgba(0,0,0,0.07)"
    }, children=[
        html.P(title, style={"margin": 0, "fontSize": "12px", "color": "#888"}),
        html.H2(value, style={"margin": "4px 0", "color": color, "fontSize": "28px"}),
        html.P(subtitle, style={"margin": 0, "fontSize": "11px", "color": "#aaa"}),
    ])


# ── Tab 2: By Industry ──
@app.callback(
    Output("industry-bar", "figure"),
    Input("industry-year", "value"),
    Input("industry-category", "value"),
)
def update_industry(year, category):
    rows = []
    for ind in ALL_INDUSTRIES:
        subset = df[df["NACE Rev. 2 main section"] == ind]
        pct = compute_pct(subset, category, year)
        if pct is not None:
            label = ind.split(" - ")[-1][:45]
            rows.append({"Industry": label, "pct": pct})

    if not rows:
        return go.Figure()

    dfi = pd.DataFrame(rows).sort_values("pct", ascending=True)

    fig = go.Figure(go.Bar(
        x=dfi["pct"], y=dfi["Industry"],
        orientation="h",
        marker_color="#2a8c87",
        text=[f"{v:.2f}%" for v in dfi["pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"{LABELS[category]} by Industry — Bulgaria {year}",
        xaxis_title="% of firms",
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#e0f8f7"),
        font=dict(family="Segoe UI", color="#1a5e5b"),
        height=600,
        margin=dict(l=320, t=60, b=40),
    )
    return fig


# ── Tab 3: By Region ──
@app.callback(
    Output("region-bar", "figure"),
    Input("region-year", "value"),
    Input("region-category", "value"),
)
def update_region(year, category):
    rows = []
    for reg in ALL_REGIONS:
        subset = df[df["Region in country clean"] == reg]
        pct = compute_pct(subset, category, year)
        if pct is not None:
            rows.append({"Region": reg, "pct": pct})

    if not rows:
        return go.Figure()

    dfr = pd.DataFrame(rows).sort_values("pct", ascending=True)

    fig = go.Figure(go.Bar(
        x=dfr["pct"], y=dfr["Region"],
        orientation="h",
        marker_color=["#1a5e5b" if r == "Sofia City" else "#2a8c87"
                      for r in dfr["Region"]],
        text=[f"{v:.2f}%" for v in dfr["pct"]],
        textposition="outside",
    ))
    fig.update_layout(
        title=f"{LABELS[category]} by Region — Bulgaria {year}",
        xaxis_title="% of firms",
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(gridcolor="#e0f8f7"),
        font=dict(family="Segoe UI", color="#1a5e5b"),
        height=650,
        margin=dict(l=160, t=60, b=40),
    )
    return fig


# ── Tab 4: Compare lines ──
@app.callback(
    Output("compare-lines", "figure"),
    Input("compare-categories", "value"),
)
def update_compare(selected_cats):
    if not selected_cats:
        return go.Figure()

    fig = go.Figure()
    for i, cat in enumerate(selected_cats):
        pcts = []
        for yr in YEARS:
            col  = f"{cat} {yr}"
            vals = df[col]
            nv   = ((vals == 1) | (vals == 0)).sum()
            n1   = (vals == 1).sum()
            pcts.append(round(n1 / nv * 100, 2) if nv > 0 else 0)

        fig.add_trace(go.Scatter(
            x=[str(y) for y in YEARS],
            y=pcts,
            name=LABELS[cat],
            mode="lines+markers",
            line=dict(color=ESI_COLORS[i % len(ESI_COLORS)], width=3),
            marker=dict(size=8),
        ))

    fig.update_layout(
        title="Evolution of Growth Metrics — Bulgaria 2020–2024",
        yaxis_title="% of firms",
        xaxis_title="Year",
        plot_bgcolor="white", paper_bgcolor="white",
        yaxis=dict(gridcolor="#e0f8f7"),
        legend=dict(bgcolor="white", bordercolor="#ccc", borderwidth=1),
        font=dict(family="Segoe UI", color="#1a5e5b"),
        margin=dict(t=60, b=40),
    )
    return fig


# ── Tab 5: Data Table ──
@app.callback(
    Output("data-table", "data"),
    Output("data-table", "columns"),
    Output("table-count", "children"),
    Input("table-region", "value"),
    Input("table-industry", "value"),
    Input("table-year", "value"),
)
def update_table(region, industry, year):
    subset = df.copy()

    if region != "All":
        subset = subset[subset["Region in country clean"] == region]
    if industry != "All":
        subset = subset[subset["NACE Rev. 2 main section"] == industry]
    if year != "none":
        col = f"Scaler {year}"
        if col in subset.columns:
            subset = subset[subset[col] == 1]

    # Columns to show
    base_cols = [
        "Company name Latin alphabet",
        "Region in country clean",
        "NACE Rev. 2 main section",
        "Founded Year",
    ]
    var_cols = [f"{cat} 2023" for cat in CATEGORIES]
    show_cols = base_cols + var_cols
    show_cols = [c for c in show_cols if c in subset.columns]

    subset_show = subset[show_cols].head(500)

    columns = [{"name": c.replace("NACE Rev. 2 main section", "Industry")
                          .replace("Region in country clean", "Region")
                          .replace("Company name Latin alphabet", "Company"),
                "id": c} for c in show_cols]

    count_msg = f"Showing {len(subset_show):,} companies (max 500 displayed)"
    return subset_show.to_dict("records"), columns, count_msg


# ── 5. RUN ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n✅ Dashboard running at: http://127.0.0.1:8050\n")
    app.run(debug=True)
