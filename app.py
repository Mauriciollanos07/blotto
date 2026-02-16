from dash import Dash, html, dcc, callback, callback_context, dash_table, MATCH, ALL, no_update
from dash.dependencies import Input, Output, State

import plotly.express as px
import plotly.figure_factory as ff
import pandas as pd
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

# 🔹 Set coordintaes for map vizualization
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
        ⚪ You cannot allocate more than 100 resourses in total\n
        ⚪ You can allocate the resources however you want regardless of the round\n
        ⚪ You don't have to allocate all the 100 resourses\n
        """, 
    "RULES 2": f"""You have chosen RULES 2 option which are:\n
        ⚪ You cannot allocate more than 100 resourses in total\n
        ⚪ You cannot allocate the same ammount of resources on two different battlefields per round\n
        """,
    "RULES 3": f"""You have chosen RULES 3 options which are:\n
        ⚪ You cannot allocate more than 100 resourses in total\n
        ⚪ You cannot leave any battlefield empty\n
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

    # Store if is rounds option is active or not
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
             className="generated-text"),

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
        ], className="generated-text", style={"textAlign": "left", "marginTop": "30px", "color": "#3D5A3C"}),
    
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
    html.Div(id="results", className="generated-text"),

    html.Div(id="rounds-container", children=[
        html.Div("Start or cancel a game with specific rounds. Doing it will reset table", id="rounds-message", className="generated-text", style={"marginBottom": "20px", "marginTop": "20px"}),
        html.Button(ROUNDS_BTN[is_rounds], id="rounds-btn", className= "button", style={"marginBottom": "20px"})
        ]
    ),

    dcc.Tabs(id="graph-display", value="general-info-chart", children=[
        dcc.Tab(label="DISTRIBUTION PER BATTELGROUND", value="general-info-chart", className="generated-text", id="tab-1"),
        dcc.Tab(label="MAPS", value="tab-2", className="generated-text", id="tab-2"),
    ]),

    dcc.Graph(id="allocation-chart"),

    dash_table.DataTable(
        id="table",
        columns=[
            {"name": col, "id": col} for col in victories_table_df.columns
        ],
        data=victories_table_df.to_dict('records'),
        style_header={
            "backgroundColor": "#1E3A5F",
            "color": "whitesmoke",
            "fontWeight": "bold",
            "padding": "10px",
            "textAlign": "left",
        }, 
        style_cell={
            "backgroundColor": "whitesmoke",
            "color": "#1E3A5F",
            "textAlign": "left",
            "padding": "10px"    
        }
    )
], id="container")

# Display rules according to selection
@app.callback(
    Output("rules-explanation", "children"),
    Input("game-options", "value")
)
def display_rules(rules):
    """
    Callback function to display the rules explanation based on the selected game option.
     Args:
        rules (str): The selected game option from the radio items.
     Returns:
        str: The explanation of the rules corresponding to the selected game option.
    """
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
    """Callback function to update the state of the rounds match, including the button text, message, and submit button status based on the current state of the rounds match.
     Args:
        is_rounds (bool): A boolean indicating whether the rounds match is active or not.
        rounds_selected (int): The number of rounds selected for the match.
        rounds_count (int): The current count of rounds played in the match.
     Returns:
        tuple: A tuple containing the button text, message, and submit button disabled status.
    """
    
    # Set variables
    disable = False
    button_message = ROUNDS_BTN[is_rounds]
    message = "Start or cancel a game with specific rounds. Doing it will reset table"
    current_round = rounds_selected - rounds_count

 # Figure out rounds played if rounds match is active
    # if is round is not activated notify player
    if not is_rounds:
        message = f"{message} You are currently in free mode"
        return button_message, message, disable
    # if rounds selected is equal to rounds count it means that the player has just started a match with rounds and is in the first round, so we set current round to 1
    elif rounds_selected == rounds_count:
        current_round = 1
    # if rounds count is greater than 0 it means that the player has more rounds to play, so we set current round to the difference between rounds selected and rounds count plus 1 (because if the player has 2 rounds to play it means that they are in round 2, if they have 1 round to play it means that they are in round 3, etc)
    elif rounds_count > 0:
        current_round = (rounds_selected - rounds_count) + 1
    message = f"{message} You are currently in a rounds match and the current round is {current_round} out of {rounds_selected}"

    # If match is finished disable submit to stop count and make user reset info
    if rounds_count < 1:
        button_message = f"END Match"
        message = f"You have played the final round, check the table to see the winner and END match to keep playing"
        disable = True

    return button_message, message, disable

# Update sliders with correct number of battlefields
@app.callback(
    Output("slider-container", "children"),
    Input("number-of-fields", "value")
)
def get_num_battlefields(num_battlefields):
    """Callback function to update the number of sliders displayed based on the selected number of battlefields.
     Args:
        num_battlefields (int): The number of battlefields selected from the dropdown.
     Returns:
        list: A list of html.Div elements containing the sliders for each battlefield.
    """
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
    """Callback function to early validate and warn player of possible excess of total resources allocated based on the current values of the sliders.
     Args:
        values (list): A list of values from all the sliders representing the current allocations for each battlefield.
     Returns:
        str: A message indicating the total allocated resources and whether it exceeds the limit or not.
    """
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
    """Callback function to update the state of the rounds match based on the clicks on the rounds button and the current state of the rounds match.
     Args:
        n_clicks (int): The number of times the rounds button has been clicked.
        is_rounds (bool): The current state of the rounds match (active or not).
     Returns:
        tuple: A tuple containing the updated state of the rounds match and the disabled status of the number of rounds input.
    """
    if is_rounds is None:
        return no_update

    disabled = False

    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    # Whenever rounds button is clicked change status
    if trigger_id != "rounds-btn":
        return no_update
    elif is_rounds == True:
        is_rounds = False
    else:
        disabled = True
        is_rounds = True
    return is_rounds, disabled


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
    """Callback function to update the stored data for AI allocations and player allocations when the submit button is clicked.
     Args:
        n_clicks (int): The number of times the submit button has been clicked.
        rule (str): The selected game option from the radio items, used to determine the rules for generating AI allocations.
        ai_data (list): The current stored data for AI allocations, used to update the AI allocations based on the selected rules.
        player_data (list): The current stored data for player allocations, used to update the player allocations based on the current slider values.
        player_allocations (list): A list of values from all the sliders representing the current allocations for each battlefield, used to update the player allocations in the stored data.
     Returns:
        tuple: A tuple containing the updated data for AI allocations and player allocations to be stored in the respective dcc.Store components.
    """
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
        player_data = player_allocations

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
    """Callback function to calculate the results of a round against random AI allocations, update the allocation chart, update the victories table, and manage the rounds count based on 
        the current state of the game and the inputs received.
     Args:
        rule (str): The selected game option from the radio items, used to determine the rules for generating AI allocations and validating player allocations.
        n_clicks (int): The number of times the submit button has been clicked.
        round_clicks (int): The number of times the rounds button has been clicked.
        graph_selected (str): The selected graph display option.
        ai_data (list): The current stored data for AI allocations.
        player_data (list): The current stored data for player allocations.
        is_round (bool): The current state of the rounds match (active or not).
        round_selected (int): The currently selected round option.
        round_count (int): The current round count.
        t_d (list): The current table data.
    Returns:
        tuple: A tuple containing the updated results message, the updated allocation chart figure, the updated table data, and the updated rounds count.
    """

    ctx = callback_context

    if not ctx.triggered:
        trigger_id = "None"
    else:
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if is_round == True:
        r_count = round_count
    else:
        r_count = round_selected

    # Make dataframes for graphics
    victories_df_copy = pd.DataFrame(t_d)
    hexbin_df = pd.DataFrame(map_df)

    # reset table if rounds button is clicked to start new match
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
    get_validation = reglas.validate_player_allocs(player_data, rule, TOTAL_RESOURCES)
    if not get_validation["Valid"]:
        return get_validation["Message"], {}, victories_df_copy.to_dict('records'), r_count

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
            if r_count > 0:
                r_count = r_count - 1
            else:
                victories_df_copy = pd.DataFrame({
                    "Nombre": ["Player", "AI"],
                    "Victorias": [0, 0],
                    "Empates": [0, 0]
                })
                r_count = round_selected
        
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
    """Callback function to update the styles of the game options and the victories table based on the current state of the game.
     Args:
        selected_value (str): The currently selected game option from the radio items.
        t_d (list): The current data of the victories table, used to determine which player is leading and update the styles accordingly.
     Returns:
        tuple: A tuple containing the updated options for the game options radio items with the selected option styled differently, and the updated style conditions for the victories table to highlight the leading player.
    """

    # Make dataframe
    victories_df_copy = pd.DataFrame(t_d)

    return [
        {
            "label": html.Span(opt, 
                style={
                    "fontWeight": "bold",
                    "color": "#2C3E2A"} if opt == selected_value else {}),
            "value": opt
        }
        for opt in GAME_OPTIONS_KEYS
    ],    [
        {
            'if': {
                'filter_query': '{{Victorias}} = {}'.format(victories_df_copy['Victorias'].max()),
            },
            'backgroundColor': '#0A7E8C',
            'color': 'white',
            'fontWeight': 'bold'
        }]


if __name__ == '__main__':
    app.run(debug=True)
