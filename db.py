import dash
from dash import html, dcc, dash_table
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objects as go
import random
import datetime

# Simulate new data arrival every 10 minutes
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

app = dash.Dash(__name__,
    requests_pathname_prefix="/dashboard/",
    suppress_callback_exceptions=True
)

app.layout = html.Div([
    dcc.Interval(id="interval", interval=10*60*1000, n_intervals=0),
    html.Div([
        html.H2("TABLEX", style={"textAlign": "center"}),
        html.Div(id="counts"),
        dcc.Graph(id="proportion-bar", config={"displayModeBar": False}),
        dcc.Graph(id="histogram", config={"displayModeBar": False}),
    ], style={"width": "25%", "display": "inline-block", "verticalAlign": "top", "padding": "20px"}),
    html.Div([
        dash_table.DataTable(
            id="datatable",
            columns=[{"name": c, "id": c} for c in ["Q", "A", "AA", "AB", "AC", "AD"]],
            data=[],
            page_size=10,
            style_table={"overflowX": "auto"},
            style_header={"backgroundColor": "#f2f2f2", "fontWeight": "bold"},
            style_cell={"textAlign": "left", "padding": "5px"},
        )
    ], style={"width": "70%", "display": "inline-block", "padding": "20px"})
])


@app.callback(
    Output("datatable", "data"),
    Output("counts", "children"),
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

    total = ans + not_ans
    red = not_ans / total * 10 if total else 0
    blue = ans / total * 10 if total else 0

    bar = go.Figure([
        go.Bar(x=[""], y=[red], name="Not Answered", marker_color="red", hovertemplate=f"{not_ans}"),
        go.Bar(x=[""], y=[blue], name="Answered", marker_color="blue", hovertemplate=f"{ans}")
    ])
    bar.update_layout(barmode="stack", height=200, margin=dict(l=20, r=20, t=20, b=20),
                      xaxis={"visible": False}, yaxis={"visible": False})

    avg = df[["AA", "AB", "AC", "AD"]].mean()
    hist = go.Figure(go.Bar(x=avg.index, y=avg.values, marker_color="lightslategray",
                            hovertemplate="%{x}: %{y:.2f}"))
    hist.update_layout(title="Average of AA–AD", height=300, margin=dict(l=40, r=20, t=40, b=40))

    return df.to_dict("records"), counts, bar, hist


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
