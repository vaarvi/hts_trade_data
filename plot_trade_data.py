import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Output, Input
import subprocess
import time

# Load and prepare data
master_df = pd.read_csv("Plot_Trade_Data.csv")

# Convert non-string columns to numeric (ignore description, HTS, country, year)
for col in master_df.columns:
    if col not in ["HTS", "description", "country", "year"]:
        master_df[col] = pd.to_numeric(master_df[col], errors='coerce')

# Unique HTS and numeric value columns
hts_codes = master_df["HTS"].dropna().unique().tolist()

# Convert HTS codes to integers or strings to avoid ".0" in dropdown
hts_codes = [str(int(hts)) if isinstance(hts, float) else str(hts) for hts in hts_codes]

value_columns = [col for col in master_df.columns 
                 if col not in ["HTS", "description", "country", "year"]
                 and pd.api.types.is_numeric_dtype(master_df[col])]

# Dash app setup
app = Dash(__name__)
app.title = "Trade Data Explorer"

app.layout = html.Div(
    style={"backgroundColor": "#111", "padding": "20px", "color": "white"},
    children=[
        html.H1("HTS Trade Data", style={"textAlign": "center"}),

        html.Div([
            html.Label("Select HTS Codes:", style={"marginRight": "10px"}),
            dcc.Dropdown(
                id='hts-dropdown',
                options=[{"label": hts, "value": hts} for hts in hts_codes],
                multi=True,
                value=[hts_codes[0]],
                style={"width": "50%", "color": "black", "backgroundColor": "white"}
            ),
        ], style={"marginBottom": "20px"}),

        html.Div([
            html.Label("Select Metrics:", style={"marginRight": "10px"}),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[{"label": metric, "value": metric} for metric in value_columns],
                multi=True,
                value=[value_columns[0]],
                style={"width": "50%", "color": "black", "backgroundColor": "white"}
            ),
        ], style={"marginBottom": "30px"}),

        dcc.Graph(id="bar-graph", style={"backgroundColor": "#111"})
    ]
)

@app.callback(
    Output("bar-graph", "figure"),
    Input("hts-dropdown", "value"),
    Input("metric-dropdown", "value")
)

def update_graph(selected_hts, selected_metrics):
    fig = go.Figure()

    # Convert selected HTS codes to strings before using in title
    selected_hts_str = [str(hts) for hts in selected_hts]  # Ensure all are strings

    for hts in selected_hts:
        df_filtered = master_df[master_df["HTS"] == int(hts)]  # Convert HTS to integer for comparison

        for metric in selected_metrics:
            df_metric = df_filtered[df_filtered[metric] != 0]

            if df_metric.empty:
                continue

            df_metric = df_metric.sort_values(by=metric, ascending=False).head(30)

            fig.add_trace(
                go.Bar(
                    x=df_metric["country"],
                    y=df_metric[metric],
                    name=f"{metric} | HTS {hts}"
                )
            )

    fig.update_layout(
        template="plotly_dark",
        barmode="group",
        title=", ".join(selected_hts_str),  # Use the string version of selected HTS
        xaxis_title="Country",
        yaxis_title="Value",
        height=650,
        width=1100,
        legend_title="Metric | HTS Code",
        title_x=0.5,
        title_font=dict(size=24),
        xaxis=dict(tickmode='array')
    )

    return fig

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
    time.sleep(2)
    subprocess.Popen(["open", "http://127.0.0.1:8050/"])  # macOS
