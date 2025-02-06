from dash import Dash, html, dcc, callback, dash_table
from dash.dependencies import Input, Output, State

import plotly.express as px
import pandas as pd

import random

app = Dash(__name__)

# Number of battlefields and total resources
NUM_BATTLEFIELDS = 5
TOTAL_RESOURCES = 100

# dict to store victories and draw table
victories_table_df = pd.DataFrame({
    "Nombre": ["Player", "AI"],
    "Victorias": [0, 0],
    "Empates": [0, 0]
})

table_d = victories_table_df.to_dict('records')

# Layout
app.layout = html.Div([
    html.H1("BLOTTO GAME"),
    
    html.Div([
        html.Div([
            html.H3(f"Battlefield {i+1}"),
            dcc.Slider(
                id=f"slider-{i+1}",
                min=0,
                max=TOTAL_RESOURCES,
                step=1,
                value=0,
                vertical=True,
                verticalHeight=250,
                marks={i: str(i) for i in range(0, TOTAL_RESOURCES+1, 20)},
                tooltip={"placement": "left", "always_visible": True}
            )
        ]) for i in range(NUM_BATTLEFIELDS)
    ], style={"display": "flex", "justify-content": "space-around"}),

    html.H3("Total Allocated:"),
    html.Div(id="total-allocated", className="generated-text"),

    html.Button("Submit Allocations", id="submit-btn", className="button"),
    html.Div(id="results", style={"marginTop": "20px"}, className="generated-text"),
    
    dcc.Graph(id="allocation-chart"),

    dash_table.DataTable(
        id='table',
        columns=[
            {"name": col, "id": col} for col in victories_table_df.columns
        ],
        data=table_d,
        style_header={
            "background-color": "#217234",
            "color": "whitesmoke",
            "font-weight": "bold",
            "padding": "10px",
            "text-align": "left",
        }, 
        style_cell={
            "background-color": "whitesmoke",
            "color": "#217234",
            "text-align": "left",
            "padding": "10px"    
        }
    )
])


# Check if allocations are valid
@app.callback(
    Output("total-allocated", "children"),
    [Input(f"slider-{i+1}", "value") for i in range(NUM_BATTLEFIELDS)],
)
def update_total(*values):
    total = sum(values)
    if total > TOTAL_RESOURCES:
        return f"Total: {total} (Exceeds limit!)"
    return f"Total: {total}"



# Simulate round against random results from machine
@app.callback(
    Output("results", "children"),
    Output("allocation-chart", "figure"),
    Output("table", "data"),
    [Input("submit-btn", "n_clicks")],
    [State(f"slider-{i+1}", "value") for i in range(NUM_BATTLEFIELDS)]
)
def calculate_results(n_clicks, *player_allocations):
    if not n_clicks:
        return "", {}, [{}]

    # Player allocations
    player_allocations = list(player_allocations)


    # Message player if input exceeds and therefor is invalid
    if sum(player_allocations) > TOTAL_RESOURCES:
        return "PLAYER EXCEEDED TOTAL RESOURCES! Check distribution and try again", {}, table_d

    # AI allocations (random strategy for now)
    ai_allocations = [random.randint(0, TOTAL_RESOURCES // NUM_BATTLEFIELDS) for _ in range(NUM_BATTLEFIELDS)]
    
    # Results per battlefield
    results = []
    for i in range(NUM_BATTLEFIELDS):
        if player_allocations[i] > ai_allocations[i]:
            results.append("Player")
        elif player_allocations[i] < ai_allocations[i]:
            results.append("AI")
        else:
            results.append("Tie")

    # Summary
    player_wins = results.count("Player")
    ai_wins = results.count("AI")
    summary = f"Player Wins: {player_wins}, AI Wins: {ai_wins}, Ties: {results.count('Tie')}"

    # Update dataframe for table of victories
    for dict in table_d:
        if player_wins > ai_wins and dict["Nombre"] == "Player":
            dict["Victorias"] = dict["Victorias"] + 1
        elif player_wins < ai_wins and dict["Nombre"] == "AI":
            dict["Victorias"] = dict["Victorias"] + 1
        elif player_wins == ai_wins:
            dict["Empates"] = dict["Empates"] + 1

    # Update order of table according to who is leading
    if table_d[0]["Victorias"] < table_d[1]["Victorias"]:
        aux = table_d[0]
        table_d[0] = table_d[1]
        table_d[1] = aux

    #print(table_d)
    #print(victories_table_df)

    # Visualization
    df = pd.DataFrame({
        "Battlefield": [f"Battlefield {i+1}" for i in range(NUM_BATTLEFIELDS)],
        "Player Allocation": player_allocations,
        "AI Allocation": ai_allocations
    })
    fig = px.bar(df, x="Battlefield", y=["Player Allocation", "AI Allocation"], barmode="group")

    return summary, fig, table_d
    


if __name__ == '__main__':
    app.run(debug=True)