from dash import Dash, html, dcc, callback, callback_context, dash_table, MATCH, ALL, no_update
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np


import random

app = Dash(__name__)
server = app.server

# Number of battlefields and total resources
NUM_BATTLEFIELDS = 5
TOTAL_RESOURCES = 100

# dict to store victories and draw table
victories_table_df = pd.DataFrame({
    "Nombre": ["Player", "AI"],
    "Victorias": [0, 0],
    "Empates": [0, 0]
})

# 🔹 Datos ficticios de territorios ganados por dos jugadores
map_df =  pd.DataFrame({
    "lat": [19.4, 19.6, 19.8, 20.0, 19.5, 19.7],  # Latitudes de territorios
    "lon": [-99.1, -99.3, -99.2, -99.5, -99.4, -99.6],  # Longitudes
    "player": ["Tie", "Tie", "Tie", "Tie", "Tie", "Tie"],
    "color_code": [0, 0, 0, 0, 0, 0]
})

victories_df_copy = victories_table_df.copy()

game_options = ["DEFAULT", "RULES 2", "RULES 3", "RULES 4"]

fields = [3, 4, 5, 6]

number_of_fields = 5
# Layout
app.layout = html.Div([

    dcc.Store(id="store-data", storage_type="memory", data=[]),

    dcc.Store(id="hexbin-values", storage_type="memory", data=[]),

    html.H1("BLOTTO GAME"),

    dcc.RadioItems(
        options=[
                    {
                        "label": option, 
                        "value": option, 
                        "title": option,
                    } for option in game_options
                ],
        value=game_options[0],
        inline=True, 
        className="dcc_control", 
        id="game-options"),

    html.Div(id="rules-explanation",
             className="generated-text",
             style={"background-color": "#217234",
                    "color": "whitesmoke",
                    "marginTop": "15px",
                    "padding": "5px",
                    "text-align": "left",
                    "white-space": "pre-line",
                    }),

    html.Div(["NUMBER OF BATTLEFIELDS AND NUMBER OF ROUNDS",
        html.Div(["Battlefields",
            dcc.Dropdown(
                id="number-of-fields",
                options=[option for option in fields],
                value=number_of_fields,
                clearable=False,
                ),
            ], style={"marginTop": "15px", "marginBottom": "15px"}),
        html.Div(["Rounds",
            dcc.Dropdown(
                id="number-of-runds",
                options=[i for i in range(1, 11)],
                value=3,
                clearable=False
                ),
            ], style={"marginTop": "15px", "marginBottom": "15px"}),
        ], className="generated-text", style={"text-align": "left", "marginTop": "30px"}),
    
    html.Div([
        html.Div(id="slider-container", 
                 children=[html.Div([
                    html.H3(f"Battlefield {i+1}"),
                    dcc.Slider(
                        id={"type": "slider", "index": i},
                        min=0,
                        max=TOTAL_RESOURCES,
                        step=1,
                        value=0,
                        vertical=True,
                        verticalHeight=250,
                        marks={i: str(i) for i in range(0, TOTAL_RESOURCES+1, 20)},
                        tooltip={"placement": "left", "always_visible": True}
                    )
                ]) for i in range(NUM_BATTLEFIELDS)], 
                style={"display": "flex", "justifyContent": "space-around"}
            )
        ]),

    html.H3("Total Allocated:"),
    html.Div(id="total-allocated", className="generated-text"),

    html.Button("Submit Allocations", id="submit-btn", className="button"),
    html.Div(id="results", style={"marginTop": "20px"}, className="generated-text"),
    
    dcc.Tabs(id="graph-display", value="general-info-chart", children=[
        dcc.Tab(label="DISTRIBUTION PER BATTELGROUND", value="general-info-chart", className="generated-text"),
        dcc.Tab(label="MAPS", value="tab-2", className="generated-text"),
    ]),

    dcc.Graph(id="allocation-chart"),

    dash_table.DataTable(
        id="table",
        columns=[
            {"name": col, "id": col} for col in victories_table_df.columns
        ],
        data=victories_table_df.to_dict('records'),
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
        },
        style_data_conditional=[
        {
            'if': {
                'filter_query': '{{Victorias}} = {}'.format(victories_table_df['Victorias'].max()),
                'column_id': 'Victorias'
            },
            'backgroundColor': '#FF4136',
            'color': 'white'
        }]
    )
])

# Display rules according to selection
@app.callback(
    Output("rules-explanation", "children"),
    Input("game-options", "value")
)
def display_rules(rules):
    rules_for_all = ["- You cannot allocate more than 100 resourses in total"]
    if rules == "DEFAULT":
        return f"""You have chosen {rules} option which are:\n
        {rules_for_all[0]}\n
        - You can allocate the resources however you want regardless of the round\n
        - You don't have to allocate all the 100 resourses\n
        """
    elif rules == "RULES 2":
        return f"""You have chosen {rules} option which are:\n
        {rules_for_all[0]}\n
        - You cannot allocate the same ammount of resources on two different battlefields per round\n
        - You have to allocate at least half of the 100 resourses in total\n
        """
    elif rules == "RULES 3":
        return f"""You have chosen {rules} option which are:\n
        {rules_for_all[0]}\n
        - You cannot repeat a combination of allocations on different rounds\n
        - You have to allocate at least 90 resourses in total per round\n
        """
    else:
        return f"""You have chosen {rules} options which are:\n
        {rules_for_all[0]}\n
        - You cannot leave any battlefield empty\n
        - You have to allocate all 100 resources per round\n
        """



# Update sliders with correct number of battlefields
@app.callback(
    Output("slider-container", "children"),
    Input("number-of-fields", "value")
)
def get_num_battlefields(num_battlefields):
    return [html.Div([
            html.H3(f"Battlefield {i+1}"),
            dcc.Slider(
                id={"type": "slider", "index": i},
                min=0,
                max=TOTAL_RESOURCES,
                step=1,
                value=0,
                vertical=True,
                verticalHeight=250,
                marks={i: str(i) for i in range(0, TOTAL_RESOURCES+1, 20)},
                tooltip={"placement": "left", "always_visible": True}
            )
        ]) for i in range(num_battlefields)] 


# Check if allocations are valid
@app.callback(
    Output("total-allocated", "children"),
    Input({"type": "slider", "index": ALL}, "value")
)
def update_total(values):
    total = sum(values)
    if total > TOTAL_RESOURCES:
        return f"Total: {total} (Exceeds limit!)"
    return f"Total: {total}"

# Update stored data
@app.callback(
    Output("store-data", "data"),
    #Output("hexbin-values", "data"),
    Input("submit-btn", "n_clicks"),
    Input("store-data", "data"),
    [State({"type": "slider", "index": ALL}, "value")],
    prevent_initial_call=True
)
def save_data(n_clicks, data, player_allocations):
    if data is None:
        print(f"data is doesn't exist and is: {data}")
        return no_update  # No actualizar si no hay valor
    print(f"data exists and is: {data}")
    
    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "submit-btn":

        ai_allocations = [random.randint(0, TOTAL_RESOURCES // len(player_allocations)) for _ in range(len(player_allocations))]
        print(ai_allocations)
        data = ai_allocations
        print(f"data has been updated and is {data}")

        """# creat copy of hb dataframe
        hb_copy = hb_copy.copy()

        # Create variable for hexbin
        if len(player_allocations) < 6:
            hb_copy = hb_copy.drop(5).reset_index(drop=True)
        
        if len(player_allocations) < 5:
            hb_copy = hb_copy.drop(4).reset_index(drop=True)

        if len(player_allocations) < 4:
            hb_copy = hb_copy.drop(4).reset_index(drop=True)

        print(f"hex bin data frame is: {hb_copy}")

        hb_newdata = hb_copy.to_dict"""
        

    return [data]  # Guardamos el valor como lista (para probar)


# Simulate round against random results from machine
@app.callback(
    Output("results", "children"),
    Output("allocation-chart", "figure"),
    Output("table", "data"),
    [Input("submit-btn", "n_clicks")],
    [Input("graph-display", "value")],
    [Input("store-data", "data")],
    [State("table", "data")],
    [State({"type": "slider", "index": ALL}, "value")]
)
def calculate_results(n_clicks, graph_selected, s_data, t_d, player_allocations):

    # Make dataframe
    victories_df_copy = pd.DataFrame(t_d)
    hexbin_df = pd.DataFrame(map_df)


    # Get info about click trigger
    if not n_clicks:
        return "", {}, victories_df_copy.to_dict('records')

    
    # Player allocations
    player_allocations = list(player_allocations)

    # Message player if input exceeds and therefor is invalid
    if sum(player_allocations) > TOTAL_RESOURCES:
        return "PLAYER EXCEEDED TOTAL RESOURCES! Check distribution and try again", {}, victories_df_copy.to_dict('records')

    # AI allocations (random strategy for now)
    #ai_allocations = [random.randint(0, TOTAL_RESOURCES // len(player_allocations)) for _ in range(len(player_allocations))]
    #print(ai_allocations)

    # Results per battlefield
    results = []
    print(f"Data imported from dcc.Store is {s_data}")
    if len(player_allocations) == len(s_data[0]):
        for i in range(len(player_allocations)):
            if player_allocations[i] > s_data[0][i]:
                results.append("Player")
            elif player_allocations[i] < s_data[0][i]:
                results.append("AI")
            else:
                results.append("Tie")

    battle_winner = np.array(results)
    print(f"battle_winner: {battle_winner}")

    # Summary
    player_wins = results.count("Player")
    ai_wins = results.count("AI")
    summary = f"Player Wins: {player_wins}, AI Wins: {ai_wins}, Ties: {results.count('Tie')}"

    #print(victories_df_copy)

    # Update dataframe for table of victories
    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if trigger_id == "submit-btn":
        if player_wins > ai_wins and victories_df_copy.at[0, "Nombre"] == "Player":
            victories_df_copy.at[0, "Victorias"] = victories_df_copy.at[0, "Victorias"] + 1
        elif player_wins > ai_wins and victories_df_copy.at[1, "Nombre"] == "Player":
            victories_df_copy.at[1, "Victorias"] = victories_df_copy.at[1, "Victorias"] + 1
        elif player_wins < ai_wins and victories_df_copy.at[0, "Nombre"] == "AI":
            victories_df_copy.at[0, "Victorias"] = victories_df_copy.at[0, "Victorias"] + 1
        elif player_wins < ai_wins and victories_df_copy.at[1, "Nombre"] == "AI":
            victories_df_copy.at[1, "Victorias"] = victories_df_copy.at[1, "Victorias"] + 1
        elif player_wins == ai_wins:
            victories_df_copy.at[0, "Empates"] = victories_df_copy.at[0, "Empates"] + 1
            victories_df_copy.at[1, "Empates"] = victories_df_copy.at[1, "Empates"] + 1
        
        """# update map dataframe
        if len(player_allocations) < 6:
            hexbin_df = hexbin_df.drop(5).reset_index(drop=True)
    
        if len(player_allocations) < 5:
            hexbin_df = hexbin_df.drop(4).reset_index(drop=True)

        if len(player_allocations) < 4:
            hexbin_df = hexbin_df.drop(3).reset_index(drop=True)"""

    # Update order of table according to who is leading
    victories_df_copy = victories_df_copy.sort_values("Victorias", ascending=False)
    victories_df_copy = victories_df_copy.reset_index(drop=True)

    print(victories_df_copy)

    #print(table_d)
    #print(victories_table_df)

    # Update graph based on tab selected
    #if graph_selected == "general-info-chart":
    # Visualization
    if len(player_allocations) == len(s_data[0]):
        if graph_selected == "general-info-chart":
            df = pd.DataFrame({
                "Battlefield": [f"Battlefield {i+1}" for i in range(len(player_allocations))],
                "Player Allocation": player_allocations,
                "AI Allocation": s_data[0]
            })
            fig = px.bar(df, x="Battlefield", y=["Player Allocation", "AI Allocation"], barmode="group")


        elif graph_selected == "tab-2":
            new_color_codes = []

            print(f"len hexbin is: {len(hexbin_df.to_dict('records'))}")

            # update map dataframe
            if len(player_allocations) < 6:
                hexbin_df = hexbin_df.drop(5).reset_index(drop=True)
        
            if len(player_allocations) < 5:
                hexbin_df = hexbin_df.drop(4).reset_index(drop=True)

            if len(player_allocations) < 4:
                hexbin_df = hexbin_df.drop(3).reset_index(drop=True)

            for result in results:
                
                print(f"result is: {result}")
                if result == "AI":
                    new_color_codes.append(2)
                elif result == "Player":
                    new_color_codes.append(1)
                else:
                    new_color_codes.append(0)
                print(f"new_color_codes is: {new_color_codes}")

            print(f"hex bin data frame is: {hexbin_df}")
            hexbin_df["player"] = results
            hexbin_df["color_code"] = new_color_codes

            hexbin_df = hexbin_df.iloc[:len(player_allocations)]
            print(f"hexbind_df[color_code] is: \n {hexbin_df['color_code']}")

            fig = ff.create_hexbin_mapbox(
            data_frame = hexbin_df,
            lat=hexbin_df["lat"],
            lon=hexbin_df["lon"],
            color=hexbin_df["color_code"],
            nx_hexagon=10,  # 🔹 Cantidad de hexágonos en eje X
            opacity=1,
            range_color=[0, 2],
            color_continuous_scale=[[0, "grey"],
                                    [0.5, "blue"],
                                    [1, "red"],]
        )

            fig.update_layout(
                mapbox_style="carto-positron",
                height=600,
                coloraxis_colorbar=dict(
                title=dict(text="Battlegorunds"),
                tickvals=[0,1,2],
                ticktext=["Tie", "Player", "Ai"]
)
                )
    else:
        fig = {}


    return summary, fig, victories_df_copy.to_dict('records')


# Update styles dinamicly
@app.callback(
    Output("game-options", "options"),
    Output("table", "style_data_conditional"),
    [Input("game-options", "value")],
    [Input("table", "data")],
    #[State({"label": "", "index": ALL}, "value")]
)
def update_styles(selected_value, t_d):

    # Make dataframe
    victories_df_copy = pd.DataFrame(t_d)

    return [
        {
            "label": html.Span(opt, 
                               style={
                                   "font-weight": "bold",
                                   "color": "#217234"} if opt == selected_value else {}),
            "value": opt
        }
        for opt in game_options
    ],    [
        {
            'if': {
                'filter_query': '{{Victorias}} = {}'.format(victories_df_copy['Victorias'].max()),
            },
            'backgroundColor': '#808D3E',
            'color': 'white',
            'font-weight': 'bold'
        }]


if __name__ == '__main__':
    app.run(debug=True)
