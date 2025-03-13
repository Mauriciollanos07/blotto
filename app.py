from dash import Dash, html, dcc, callback, callback_context, dash_table, MATCH, ALL, no_update
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
import numpy as np

import random
import reglas

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

# Text for match button (start in false which is free mode)
ROUNDS_BTN = {True: "CANCEL match", False: "START Match with Rounds"}
is_rounds = False

# 🔹 Datos ficticios de territorios ganados por dos jugadores
map_df =  pd.DataFrame({
    "lat": [4.595556, 38.897778, 51.501, -34.608056, 33.5804, 55.751667],  # Latitudes de territorios
    "lon": [-74.0775, -77.036667, -0.142, -58.370278, -7.6055, 37.617778],  # Longitudes
    "player": ["Tie", "Tie", "Tie", "Tie", "Tie", "Tie"],
    "color_code": [0, 0, 0, 0, 0, 0]
})

# Copy of created datafram (dont think is necessary)
victories_df_copy = victories_table_df.copy()

# Text to describe the different rules base on selected value
GAME_OPTIONS = {"DEFAULT": f"""You have chosen DEFAULT option which are:\n
        - You cannot allocate more than 100 resourses in total\n
        - You can allocate the resources however you want regardless of the round\n
        - You don't have to allocate all the 100 resourses\n
        """, 
    "RULES 2": f"""You have chosen RULES 2 option which are:\n
        - You cannot allocate more than 100 resourses in total\n
        - You cannot allocate the same ammount of resources on two different battlefields per round\n
        """,
    "RULES 3": f"""You have chosen RULES 4 options which are:\n
        - You cannot allocate more than 100 resourses in total\n
        - You cannot leave any battlefield empty\n
        """}

# Take just the keys for the radio items
GAME_OPTIONS_KEYS = GAME_OPTIONS.keys()

# Amount of fields options
fields = [3, 4, 5, 6]
number_of_fields = 5


# Layout
app.layout = html.Div([

    # All the dcc.Stores to store variables while app is running
    # Store data is the latest ai generated allocations in a list, and the same in next but with player allocations
    dcc.Store(id="store-data", storage_type="memory", data=[]),
    dcc.Store(id="store-player-data", storage_type="memory", data=[]),

    # Values necessary to build the hexbin grid (think is no longer necessary with the map)
    dcc.Store(id="hexbin-values", storage_type="memory", data=[]),

    # Store if is rounds is active or not
    dcc.Store(id="rounds-store", storage_type="memory", data=is_rounds),

    # Store how many rounds have been played (regressive count)
    dcc.Store(id="rounds-count", storage_type="memory", data=3),

    html.H1("BLOTTO GAME"),

    dcc.RadioItems(
        options=[
                    {
                        "label": option, 
                        "value": option, 
                        "title": option,
                    } for option in GAME_OPTIONS_KEYS
                ],
        value="DEFAULT",
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
                id="number-of-rounds",
                options=[i for i in range(1, 11)],
                value=3,
                clearable=False,
                disabled=False
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

    html.Button("Submit Allocations", id="submit-btn", className="button", disabled=False),
    html.Div(id="results", style={"marginTop": "20px"}, className="generated-text"),
    
    html.Div(id="rounds-container", children=[
        html.Div("Start or cancel a game with specific rounds. Doing it will reset table", id="rounds-message", className="generated-text", style={"marginBottom": "20px", "marginTop": "20px"}),
        html.Button(ROUNDS_BTN[is_rounds], id="rounds-btn", className= "button", style={"marginBottom": "20px"})
        ]
    ),

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
    for option in GAME_OPTIONS_KEYS:
        if rules == option:
            return GAME_OPTIONS[option]
    return f"Rules not found"

# Update if match with rounds is active or not (free mode) and the count of rounds already played
# Disable submit button if match has ended to make user reset rounds button
@app.callback(
    Output("rounds-btn", "children"),
    Output("rounds-message", "children"),
    Output("submit-btn", "disabled"),
    Input("rounds-store", "data"),
    Input("number-of-rounds", "value"),
    Input("rounds-count", "data")

)
def change_is_rounds(is_rounds, rounds_selected, rounds_count):
    
    # Set variables
    disable = False
    button_message = ROUNDS_BTN[is_rounds]
    message = "Start or cancel a game with specific rounds. Doing it will reset table"
    current_round = rounds_selected - rounds_count

 # Figure out rounds played if rounds match is active
    if is_rounds == True:
        if rounds_selected == rounds_count:
            current_round = 1
        elif rounds_count > 0:
            current_round = (rounds_selected - rounds_count) + 1
        message = f"{message} You are currently in a rounds match and the current round is {current_round} out of {rounds_selected}"
    else:
        message = f"{message} You are currently in free mode"

    # If match is finished disable submit to stop count and make user reset info
    if rounds_count < 1:
        button_message = f"END Match"
        message = f"You have played the final round, check the table to see the winner and END match to keep playinf"
        disable = True

    return button_message, message, disable

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

# Update is_rounds to know if rounds are active or not
@app.callback(
    Output("rounds-store", "data"),
    Output("number-of-rounds", "disabled"),
    Input("rounds-btn", "n_clicks"),
    Input("rounds-store", "data")
)

def update_is_rounds(n_clicks, is_rounds):
    if is_rounds is None:
        return no_update

    disabled = False

    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Whenever rounds button is clicked change status
    if trigger_id == "rounds-btn":
        if is_rounds == True:
            is_rounds = False
        else:
            disabled = True
            is_rounds = True
        return is_rounds, disabled
    else:
        return no_update

# Update stored data for ia allocations and player
@app.callback(
    Output("store-data", "data"),
    Output("store-player-data", "data"),
    Input("submit-btn", "n_clicks"),
    Input("game-options", "value"),
    State("store-data", "data"),
    State("store-player-data", "data"),
    [State({"type": "slider", "index": ALL}, "value")],
    prevent_initial_call=True
)
def save_data(n_clicks, rule, ai_data, player_data, player_allocations):
    if ai_data is None:
        return no_update  # No update it there is no value (it should never be None because of layout setting)

    if player_data is None:
        return no_update  # No update it there is no value (it should never be None because of layout setting)

    
    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Update data only if submit button is triggered
    if trigger_id == "submit-btn":

        ai_data = reglas.get_ai_allocations(len(player_allocations), rule) # Call function to get ai allocations
        print(f"ai data has been updated and is {ai_data}")
        player_data = player_allocations
        print(f"player data has been updated and is {player_data}")

    else:

        return no_update 
    
    return [ai_data], [player_data]

# Simulate round against random results from machine
@app.callback(
    Output("results", "children"),
    Output("allocation-chart", "figure"),
    Output("table", "data"),
    Output("rounds-count", "data"),
    [Input("game-options", "value")],
    [Input("submit-btn", "n_clicks")],
    [Input("rounds-btn", "n_clicks")],
    [Input("graph-display", "value")],
    [Input("store-data", "data")],
    [Input("store-player-data", "data")],
    [Input("rounds-store", "data")],
    [Input("number-of-rounds", "value")],
    [Input("rounds-count", "data")],
    [State("table", "data")],
)
def calculate_results(rule, n_clicks, round_clicks, graph_selected, ai_data, player_data, is_round, round_selected, round_count, t_d):

    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if is_round == True:
        r_count = round_count
    else:
        r_count = round_selected

    print("**********************************")
    print(f"rounds count after first import is {r_count}")
    print("**********************************")

    # Make dataframes for graphics
    victories_df_copy = pd.DataFrame(t_d)
    hexbin_df = pd.DataFrame(map_df)

    if trigger_id == "rounds-btn":
        victories_df_copy = pd.DataFrame({
            "Nombre": ["Player", "AI"],
            "Victorias": [0, 0],
            "Empates": [0, 0]
        })

    # Player allocations
    if player_data:
        player_data = player_data[0]

    # Ai allocations
    if ai_data:
        ai_data = ai_data[0]

    # Return nothing if no clicks have happened
    if not n_clicks:
        return "", {}, victories_df_copy.to_dict('records'), r_count

    # Message player if allocations dont follow rules selected
    if False in reglas.validate_player_allocs(player_data, rule, TOTAL_RESOURCES).keys():
        return reglas.validate_player_allocs(player_data, rule, TOTAL_RESOURCES)[False], {}, victories_df_copy.to_dict('records'), r_count

    # Results per battlefield
    results = []
    for i in range(len(player_data)):
        if player_data[i] > ai_data[i]:
            results.append("Player")
        elif player_data[i] < ai_data[i]:
            results.append("AI")
        else:
            results.append("Tie")

    # Summary
    player_wins = results.count("Player")
    ai_wins = results.count("AI")
    summary = f"Player Wins: {player_wins}, AI Wins: {ai_wins}, Ties: {results.count('Tie')}"

    # Update Victories Data Frame if submit button is triggered
    if trigger_id == "submit-btn":

        # update rounds count if necessary
        if is_round == True:
            print("**********************************")
            if r_count > 0:
                r_count = r_count - 1
                print(f"is round is true and r count is more than 0 so count has to be one less that previous round which should be {r_count} ")
            else:
                victories_df_copy = pd.DataFrame({
                    "Nombre": ["Player", "AI"],
                    "Victorias": [0, 0],
                    "Empates": [0, 0]
                })
                r_count = round_selected
                print(f"is round is true and r count is less than or equal to 0 so count has to reset, which should be {r_count} ")
        print("**********************************")
        
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

    # Update order of table according to who is leading
    victories_df_copy = victories_df_copy.sort_values("Victorias", ascending=False)
    victories_df_copy = victories_df_copy.reset_index(drop=True)

    print(victories_df_copy)

    # Update graph based on tab selected
    # Visualization
    if graph_selected == "general-info-chart":
        df = pd.DataFrame({
            "Battlefield": [f"Battlefield {i+1}" for i in range(len(player_data))],
            "Player Allocation": player_data,
            "AI Allocation": ai_data
        })
        fig = px.bar(df, x="Battlefield", y=["Player Allocation", "AI Allocation"], barmode="group")

    elif graph_selected == "tab-2":
        new_color_codes = []

        print(f"len hexbin is: {len(hexbin_df.to_dict('records'))}")

        # update map dataframe
        if len(player_data) < 6:
            hexbin_df = hexbin_df.drop(5).reset_index(drop=True)
    
        if len(player_data) < 5:
            hexbin_df = hexbin_df.drop(4).reset_index(drop=True)

        if len(player_data) < 4:
            hexbin_df = hexbin_df.drop(3).reset_index(drop=True)

        for result in results:
            
            if result == "AI":
                new_color_codes.append(2)
            elif result == "Player":
                new_color_codes.append(1)
            else:
                new_color_codes.append(0)

        hexbin_df["player"] = results
        hexbin_df["color_code"] = new_color_codes

        hexbin_df = hexbin_df.iloc[:len(player_data)]

        fig = ff.create_hexbin_mapbox(
        data_frame = hexbin_df,
        lat=hexbin_df["lat"],
        lon=hexbin_df["lon"],
        color=hexbin_df["color_code"],
        nx_hexagon=10,  
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

    return summary, fig, victories_df_copy.to_dict('records'), r_count

# Update styles dinamicly
@app.callback(
    Output("game-options", "options"),
    Output("table", "style_data_conditional"),
    [Input("game-options", "value")],
    [Input("table", "data")],
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
        for opt in GAME_OPTIONS_KEYS
    ],    [
        {
            'if': {
                'filter_query': '{{Victorias}} = {}'.format(victories_df_copy['Victorias'].max()),
            },
            'backgroundColor': '#808D3E',
            'color': 'white',
            'font-weight': 'bold'
        }]

print(f"--------------------------------------new--------------------------------------")


if __name__ == '__main__':
    app.run(debug=True)
