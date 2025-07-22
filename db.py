from dash import Dash, dcc, html, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import random
import datetime

def fetch_data():
    n = 20
    return pd.DataFrame({
        "Q": [f"Question {i}" for i in range(1, n+1)],
        "A": [random.choice(["Answered", "Not Answered"]) for _ in range(n)],
        "AA": [random.randint(0, 10) for _ in range(n)],
        "AB": [random.randint(0, 10) for _ in range(n)],
        "AC": [random.randint(0, 10) for _ in range(n)],
        "AD": [random.randint(0, 10) for _ in range(n)],
    })

app = Dash(__name__)
server = app.server

app.layout = html.Div([
    dcc.Interval(id="interval", interval=10*60*1000, n_intervals=0),
    html.Div([
        # Sidebar
        html.Div([
            html.H2("TABLEX", style={"textAlign": "center"}),
            html.Div(id="counts-div", style={"marginTop": "20px", "textAlign": "center"}),
            dcc.Graph(id="proportion-bar", config={"displayModeBar": False}),
            dcc.Graph(id="histogram", config={"displayModeBar": False}),
        ], style={
            "flex": "0 0 25%",
            "padding": "20px",
            "boxShadow": "2px 2px 2px #ccc",
            "height": "100vh",  # full viewport height :contentReference[oaicite:4]{index=4}
            "boxSizing": "border-box"
        }),

        # Data table
        html.Div([
            dash_table.DataTable(
                id="data-table",
                columns=[{"name": c, "id": c} for c in ["Q", "A", "AA", "AB", "AC", "AD"]],
                data=[],
                page_size=10,
                style_table={"height": "calc(100vh - 40px)", "overflowY": "auto"},  # fill remaining height
                style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold", "position": "sticky", "top": 0},
                style_cell={"textAlign": "left", "padding": "5px"},
            )
        ], style={"flex": "1", "padding": "20px"})
    ], style={"display": "flex", "alignItems": "flex-start"})
])

@app.callback(
    Output("data-table", "data"),
    Output("counts-div", "children"),
    Output("proportion-bar", "figure"),
    Output("histogram", "figure"),
    Input("interval", "n_intervals")
)
def update(n):
    df = fetch_data()
    ans = (df["A"] == "Answered").sum()
    not_ans = (df["A"] == "Not Answered").sum()

    counts = [
        html.P(f"Answered: {ans}", style={"color": "blue", "fontSize": "18px"}),
        html.P(f"Not Answered: {not_ans}", style={"color": "red", "fontSize": "18px"})
    ]

    # Horizontal stacked bar with counts labeled inside
    bar = go.Figure()
    bar.add_trace(go.Bar(
        x=[not_ans], y=[""],
        name="Not Answered", orientation='h',
        marker_color="red", text=[str(not_ans)], textposition='inside'
    ))
    bar.add_trace(go.Bar(
        x=[ans], y=[""],
        name="Answered", orientation='h',
        marker_color="blue", text=[str(ans)], textposition='inside'
    ))
    bar.update_layout(barmode="stack", height=100, margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={"visible": False}, yaxis={"visible": False})

    avg_vals = df[["AA", "AB", "AC", "AD"]].mean()
    hist = go.Figure(go.Bar(
        x=avg_vals.index, y=avg_vals.values, marker_color="lightslategray",
        hovertemplate="%{x}: %{y:.2f}"
    ))
    hist.update_layout(title="Average AA–AD", height=300, margin=dict(l=40, r=20, t=40, b=40))

    return df.to_dict("records"), counts, bar, hist

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8080, debug=True)

