from dash import dcc, html, dash_table
import dash
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash.dependencies import Input, Output, State
import pandas as pd
import numpy as np
import json
import os
import dash_draggable
import sqlalchemy as sa
from sqlalchemy import create_engine
import requests
from flask import Flask
import pyodbc






def init_dashboard():
    app = dash.Dash(
        __name__, 
        external_stylesheets=[dbc.themes.BOOTSTRAP, "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css"]

    )
    
    
    
    def convert_units(df):
    # Ensure 'Result' is numeric and handle conversion errors
        df['Result'] = pd.to_numeric(df['Result'], errors='coerce')
    
    # Ensure 'Units' column is of type string to avoid issues
        df['Units'] = df['Units'].astype(str)
    
    # Check for and handle missing values in 'Units' column
        if df['Units'].isnull().any():
            print("Warning: There are missing values in the 'Units' column. These rows will be skipped.")
    
    # Convert Fahrenheit to Celsius where applicable and update units
        mask = df['Units'] == '°F'
        df.loc[mask, 'Result'] = (df.loc[mask, 'Result'] - 32) * 5.0 / 9.0
        df.loc[mask, 'Units'] = '°C'
    
        return df

    

            
    # Fonction pour récupérer les données depuis l'API
   # def fetch_data():
  ##      response = requests.get('http://10.5.50.18:5000/data')
  #      data = response.json()
  #      return pd.DataFrame(data)

# Récupérer les données
  #  data = fetch_data()

    response = requests.get('http://10.5.50.18:5000/api/data?sheet_name=All')
    data2 = response.json()
    df = pd.DataFrame(data2)
    

    
    
    # Définir le chemin du fichier JSON pour le stockage des noms des méthodes
    METHOD_NAMES_FILE = 'method_names.json'
    COMMENTS_FILE = 'comments.json'
    TABLE_DATA_FILE = 'H:\\python LV8 v.2\\table_data.json'
    DATA_TABLE = "G:\\laboratoire\\02 Suivi statistique\\2-Programmes d'échange\\Compilation PTP 2024+.xlsx"
    df = pd.read_excel(DATA_TABLE, sheet_name='All')
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
    convert_df = convert_units(df)

    def read_json(file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                return json.load(file)
        return {}

    def write_json(file_path, data):
        with open(file_path, 'w') as file:
            json.dump(data, file)
            



    def get_equivalences(method, methods_table_data):
        
        equivalence = next((item for item in methods_table_data if item["Method"] == method), None)
        
        if equivalence:
            return equivalence['LV8 Param'], equivalence['LV8 Test']
        return None, None
    
   # def create_tables_and_calculate_std(property_id, test_id):
  #      filtered_df = data[(data['PROPERTYID'] == property_id) & (data['TESTID'] == test_id[:-1])]
  #      return filtered_df['NUMBER_VALUE'].std()
 

    # Liste initiale des colonnes disponibles
    initial_columns = [
    {'label': 'Date', 'value': 'Date'},
    {'label': 'NOM', 'value': 'NOM'},
    {'label': 'Result', 'value': 'Result'},
    {'label': 'Z-Score', 'value': 'Z-Score'},
    {'label': 'E-Score', 'value': 'e_scores'},
    {'label': 'Average', 'value': 'Average'},
    {'label': 'Std Dev', 'value': 'Std Dev'},
    {'label': 'Count', 'value': 'Count'},
    {'label': 'Rdat', 'value': 'Rdat'},
    {'label': 'Rpub', 'value': 'Rpub'},
    {'label': 'Units', 'value': 'Units'},
    {'label': 'Comment', 'value': 'Comment'},
    {'label': 'RunSum', 'value': 'RunSum'},
    {'label': 'Som', 'value': 'Som'}
]

    app.layout = dbc.Container(
    [
        dcc.Store(id='stored-method-names', storage_type='local'),
        dcc.Store(id='methods-table-data', storage_type='local'),
        dcc.Store(id='comments-store', storage_type='local'),  # Ajout pour stocker les commentaires
        dbc.Navbar(
            dbc.Container(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                html.Img(src='/logo.png', height="40px"),  # Chemin relatif vers l'image dans le dossier assets
                                width="auto"
                            ),
                            dbc.Col(
                                html.H4("Dashboard - PTP Data Analysis", className="text-center my-2"),
                                style={'display': 'flex', 'alignItems': 'center'},
                                width=3
                            ),
                                        dbc.Col(
                [
                    dcc.Textarea(
                        id='comment-textarea',
                        placeholder='Enter your comment...',
                        style={'width': '100%', 'height': 30},
                    ),
                ],
                width=3
            ),
                dbc.Col(
                    dcc.Dropdown(
                        id='method-dropdown',
                        options=[],  # Les options seront définies dynamiquement
                        className="mb-2",
                        style={'width': '100%', 'marginTop': '5px'},
                        placeholder='Select Method',
                    ),
                    width=3  # Ajustez cette valeur si nécessaire
                ),
                dbc.Col(
                    dcc.Dropdown(
                        id='first-letter-dropdown',
                        options=[],  # Les options seront définies dynamiquement
                        className="mb-2",
                        style={'width': '100%', 'marginTop': '5px'},
                        placeholder='Select First Letter',
                        disabled=True  # Désactiver par défaut
                    ),
                    width=2  # Ajustez cette valeur si nécessaire
                ),
            
        
                            dbc.Col(
                                dbc.Button(
                                    [
                                        html.I(className="fas fa-cog", style={'marginRight': '0'}),  # Icône avec espace à droite
                                    ],
                                    id="open-modal",
                                    color="primary",
                                    className="mb-2",
                                    style={'marginTop': '5px'}
                                ),
                                width="auto",
                                className="ml-auto"
                            )
                        ],
                        align="center",
                        style={'width': '100%'}  # Centrer verticalement la rangée
                    ),
                    dbc.Modal(
                        [
                            dbc.ModalHeader("Edit Methods Table"),
                            dbc.ModalBody(
                                dash_table.DataTable(
                                    id='methods-table',
                                    columns=[
                                        {'name': 'Method', 'id': 'Method', 'editable': False},
                                        {'name': 'LV8 Param', 'id': 'LV8 Param', 'editable': True},
                                        {'name': 'LV8 Test', 'id': 'LV8 Test', 'editable': True}
                                    ],
                                    data=[],
                                    editable=True,
                                    row_deletable=True,
                                    style_table={'height': '400px', 'overflowY': 'auto'},
                                    style_cell={'textAlign': 'left'},
                                )
                            ),
                            dbc.ModalFooter(
                                dbc.Button("Save", id="save-table-button", color="primary", className="ml-auto")
                            )
                        ],
                        id="table-modal",
                        is_open=False,
                        size="xl",
                        style={"max-width": "90%"}
                    ),
                ],
                fluid=True,
                style={'backgroundColor': '#f8f9fa'}
            ),
            color="primary",
            dark=True,
            sticky="top",
            className="py-1"
        ),
        html.Div(id='graphs-title', style={'textAlign': 'center', 'marginTop': '20px', 'marginBottom': '20px'}),

                            dbc.Modal(
                                [
                                    dbc.ModalHeader("Summary"),
                                    dbc.ModalBody(
                                        dash_table.DataTable(
                                            id='summary-table',
                                            columns=[
                                                {'name': 'Method', 'id': 'Method'},
                                                {'name': 'Average Delta Moving Average', 'id': 'AvgDeltaMovingAvg'},
                                                {'name': 'Average Z-Score', 'id': 'AvgZScore'}
                                            ],
                                            data=[],
                                            style_table={'height': '400px', 'overflowY': 'auto'},
                                            style_cell={'textAlign': 'left'},
                                        )
                                    ),
                                    dbc.ModalFooter(
                                        dbc.Button("Ok", id="close-summary-modal", className="ml-auto")
                                    )
                                ],
                                id="summary-modal",
                                is_open=False,
                                size="xl",
                                className="modal-xl",
                            ),
        
        dbc.Modal(
            [
                dbc.ModalHeader("Configure Columns"),
                dbc.ModalBody(
                    dbc.Container(
                        [
                            dbc.Row(
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="fas fa-chart-bar"), " Graph Settings"],
                                        id="graph-settings-toggle",
                                        color="secondary",
                                        className="mb-2",
                                        style={'width': '100%'}
                                    )
                                )
                            ),
dbc.Collapse(
    dbc.Card(
        dbc.CardBody(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            dcc.Checklist(
                                id='column-checklist',
                                options=initial_columns[0:6],
                                value=[col['value'] for col in initial_columns[0:6]],
                                inline=False,  # Désactiver l'affichage en ligne
                                labelStyle={'display': 'block'}
                            ),
                            width=4  # Définir la largeur pour occuper un tiers de l'espace
                        ),
                        dbc.Col(
                            dcc.Checklist(
                                id='column-checklist2',
                                options=initial_columns[6:],
                                value=[col['value'] for col in initial_columns[6:]],
                                inline=False,  # Désactiver l'affichage en ligne
                                labelStyle={'display': 'block'}
                            ),
                            width=4  # Définir la largeur pour occuper un tiers de l'espace
                        ),
                    ],
                    justify="center"
                    
                ),
                dbc.Row(
                    dbc.Col(
                        dcc.Input(
                            id='num-values-input',
                            type='number',
                            value=10,
                            min=1,
                            step=1,
                            className="mb-2",
                            style={'marginTop': '5px', 'width': '100%'}
                        ),
                        width=12,
                        className="ml-auto mr-auto"
                    )
                ),
                
            ]
        )
    ),
    id="graph-settings-collapse",
),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Button(
                                        [html.I(className="fas fa-edit"), " Modify Method Names"],
                                        id="method-names-toggle",
                                        color="secondary",
                                        className="mb-2",
                                        style={'width': '100%'}
                                    ),
                                )
                            ),
                            dbc.Collapse(
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            dbc.Row(
                                                dbc.Col(
                                                    dcc.Input(
                                                        id='rename-input',
                                                        type='text',
                                                        placeholder='Rename selected method',
                                                        className="mb-2",
                                                        style={'marginTop': '5px', 'width': '100%'}
                                                    ),
                                                    width=12,
                                                    className="ml-auto mr-auto"
                                                )
                                            ),
                                            dbc.Row(
                                                dbc.Col(
                                                    dbc.Button("Rename", id="rename-button", color="secondary", className="mb-2 w-100", style={'marginTop': '5px'}),
                                                    width=12,
                                                    
                                                )
                                            ),
                                            dbc.Row(
                                                dbc.Col(
                                                    dbc.Button("Reset Names", id="reset-button", color="warning", className="mb-2 w-100", style={'marginTop': '5px'}),
                                                    width=12
                                                    
                                                )
                                            ),
                                        ]
                                    )
                                ),
                                id="method-names-collapse",
                            ),
                            dbc.Row(
                                [
                                    dbc.Col(
                                        dbc.Button([html.I(className="fas fa-file-alt"), "Sommaire"], id="open-summary-modal", color="info", className="mb-2 w-100", style={'marginTop': '5px', 'marginRight' : '10px'}),
                                        width= '6',
                                        className="ml-auto mr-auto"
                                    ),
                                    dbc.Col(
                                        dbc.Button([html.I(className="fas fa-edit"), " Edit Methods"], id="open-table-modal", color="info", className="mb-2 w-100", style={'marginTop': '5px', 'marginLeft' : '10px'}),  # Bouton avec icône
                                        width='6',
                                        className="ml-auto mr-auto"
                                    )
                                ]
                            ),
                            dbc.Row(
                                dbc.Col(
                                    dbc.Button("Ok", id="close-modal", className="ml-auto mt-3"),
                                    width={"size": "auto", "offset": 10} 
                                )
                            )
                        ]
                    )
                ),
            ],
            id="modal",
            is_open=False,
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='z-score-graph')
                        ]),
                        className="mb-4",
                        style={'backgroundColor': '#e9ecef'}
                    ), width=6
                ),
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='z-prime-graph')
                        ]),
                        className="mb-4",
                        style={'backgroundColor': '#e9ecef'}
                    ), width=6
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='delta-moving-average-graph')
                        ]),
                        className="mb-4",
                        style={'backgroundColor': '#e9ecef'}
                    ), width=6
                ),

                                dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            dcc.Graph(id='z-score-moving-average-graph')
                        ]),
                        className="mb-4",
                        style={'backgroundColor': '#e9ecef'}
                    ), width=6
                )
            ]
        ),

        dbc.Row(
            dbc.Col(
dag.AgGrid(
    id="data-grid",
    rowData=[],
        columnDefs=[
            {'field': col['value'], 'cellStyle': {'color': 'red'} if col['value'] == 'RunSum' else {'color': 'black'}} for col in initial_columns
        ],
    columnSize="sizeToFit",
    suppressDragLeaveHidesColumns=False,
    dashGridOptions={"animateRows": False},
    style={'height': '400px', 'width': '100%'},

),
                width=12
            )
        ),


        dcc.Interval(
            id='interval-component',
            interval=360*1000,
            n_intervals=0
        )
    ],
    fluid=True
)
    @app.callback(
        Output('modal', 'is_open'),
        [Input('open-modal', 'n_clicks'), Input('close-modal', 'n_clicks')],
        [State('modal', 'is_open')]
    )
    def toggle_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open
    
    @app.callback(
        Output('method-names-collapse', 'is_open'),
        [Input('method-names-toggle', 'n_clicks')],
        [State('method-names-collapse', 'is_open')]
    )
    def toggle_method_names_collapse(n, is_open):
        if n:
            return not is_open
        return is_open

    @app.callback(
        Output('table-modal', 'is_open'),
        [Input('open-table-modal', 'n_clicks'), Input('save-table-button', 'n_clicks')],
        [State('table-modal', 'is_open')]
    )
    def toggle_table_modal(n1, n2, is_open):
        
        if n1 or n2:
            return not is_open
        return is_open
    
    @app.callback(
        Output('edit-methods-collapse', 'is_open'),
        [Input('edit-methods-toggle', 'n_clicks')],
        [State('edit-methods-collapse', 'is_open')]
    )
    def toggle_edit_methods_collapse(n, is_open):
        
        if n:
            return not is_open
        return is_open
    
    @app.callback(
        Output('graph-settings-collapse', 'is_open'),
        [Input('graph-settings-toggle', 'n_clicks')],
        [State('graph-settings-collapse', 'is_open')]
    )
    def toggle_graph_settings_collapse(n, is_open):
        if n:
            return not is_open
        return is_open
    

    @app.callback(
    Output('summary-modal', 'is_open'),
    [Input('open-summary-modal', 'n_clicks'), Input('close-summary-modal', 'n_clicks')],
    [State('summary-modal', 'is_open')]
    )
    def toggle_summary_modal(n1, n2, is_open):
        if n1 or n2:
            return not is_open
        return is_open

    @app.callback(
        Output('method-dropdown', 'options'),
        [Input('interval-component', 'n_intervals'),
         Input('stored-method-names', 'data')]
    )
    def update_dropdown(n, stored_names):
        
        methods = df['Method'].unique()
        options = [{'label': stored_names.get(method, method), 'value': method} for method in methods] if stored_names else [{'label': method, 'value': method} for method in methods]
        return options
    
    @app.callback(
    [Output('first-letter-dropdown', 'options'),
     Output('first-letter-dropdown', 'disabled')],
    [Input('method-dropdown', 'value')]
    )
    def update_first_letter_options(selected_method):
        if selected_method:
            filtered_df = df[df['Method'] == selected_method]
            first_letters = sorted(filtered_df['NOM'].str[0].unique())
            options = [{'label': letter, 'value': letter} for letter in first_letters]
            return options, False
        return [], True
    
    @app.callback(
    Output('methods-table', 'data'),
    [Input('interval-component', 'n_intervals'), Input('save-table-button', 'n_clicks')],
    [State('methods-table', 'data')]
    )
    def update_table_data(n, save_clicks, current_table_data):
        ctx = dash.callback_context
        stored_table_data = read_json(TABLE_DATA_FILE)
        if not ctx.triggered:
            if stored_table_data:
                return stored_table_data
            else:
                df = convert_df
                methods = df['Method'].unique()
                initial_data = [{'Method': method, 'LV8 Param': '', 'LV8 Test': ''} for method in methods]
                return initial_data

        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if trigger_id == 'save-table-button':
            
            write_json(TABLE_DATA_FILE, current_table_data)
            
            return current_table_data

        if stored_table_data:
            return stored_table_data

        df = convert_df
        methods = df['Method'].unique()
        initial_data = [{'Method': method, 'LV8 Param': '', 'LV8 Test': ''} for method in methods]
        return initial_data
    

    @app.callback(
        Output('stored-method-names', 'data'),
        [Input('rename-button', 'n_clicks'), Input('reset-button', 'n_clicks')],
        [State('method-dropdown', 'value'), State('rename-input', 'value'), State('stored-method-names', 'data')]
    )
    def manage_method_names(rename_clicks, reset_clicks, selected_method, new_name, stored_names):
        ctx = dash.callback_context
        if not ctx.triggered:
            return stored_names
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

        if trigger_id == 'rename-button':
            if rename_clicks is None or not selected_method or not new_name:
                return stored_names
            if stored_names is None:
                stored_names = {}
            stored_names[selected_method] = new_name
        elif trigger_id == 'reset-button':
            if stored_names is not None and selected_method in stored_names:
                stored_names.pop(selected_method)

        return stored_names
        

    

    def calculate_runsum(z_scores):
        result = []
        current_sum = 0
        was_negative = False
        for score in z_scores:
            try:
                num_value = float(score)
            except ValueError:
                result.append('n.a.n')
                continue
            if np.isnan(num_value):
                result.append('n.a.n')
            elif num_value < 0:
                if was_negative:
                    current_sum += 1
                else:
                    current_sum = 1
                    was_negative = True
            else:
                if was_negative:
                    current_sum = 1
                    was_negative = False
                else:
                    current_sum += 1
            result.append(current_sum)
        return result
    
    def calculate_som(z_scores):
        som = []
        current_somme = 0
        was_negative = False
        for score in z_scores:
            if np.isnan(score):
                som.append(np.nan)
                continue
            if score > 0 and not was_negative:
                current_somme += abs(score)
            elif score > 0 and was_negative:
                current_somme = 0
                was_negative = False
            elif score < 0 and not was_negative:
                current_somme = 0
                was_negative = True
            elif score < 0 and was_negative:
                current_somme += abs(score)
            som.append(round(current_somme, 2))
        return som

    def calculate_moving_average(data, window_size):
        if window_size < 1:
            window_size = 1
        data = np.array(data, dtype=np.float64)
        return pd.Series(data).rolling(window=window_size, min_periods=1).mean().tolist()
    

    @app.callback(
    Output('comments-store', 'data'),
    [Input('comment-textarea', 'value')],
    [State('method-dropdown', 'value'), State('comments-store', 'data')]
    )
    def save_comment(comment, selected_method, comments_data):
        if selected_method:
            if comments_data is None:
                comments_data = {}
            comments_data[selected_method] = comment
            write_json(COMMENTS_FILE, comments_data)
        return comments_data
    

    @app.callback(
    Output('summary-table', 'data'),
    [Input('open-summary-modal', 'n_clicks'),
     Input('num-values-input', 'value'),],
    [State('methods-table-data', 'data')]
    )
    def update_summary_table(n_clicks, num_values, methods_table_data):
        if n_clicks is None:
            return []
    
        df = convert_df
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Z-Score'] = pd.to_numeric(df['Z-Score'], errors='coerce')
        df['Result'] = pd.to_numeric(df['Result'], errors='coerce')
        df['Average'] = pd.to_numeric(df['Average'], errors='coerce')
    
        summary_data = []
        methods = df['Method'].unique()
    
        for method in methods:
            method_data = df[df['Method'] == method]
            if not method_data.empty:
                
                
                method_data = method_data.dropna(subset=['Z-Score'])
                method_data['Date'] = pd.to_datetime(method_data['Date'])
                method_data = method_data.sort_values(by='Date').tail(num_values)

                
                if len(method_data) == 0:
                    delta_moving_avg_avg = 'nan'
                    avg_z_score ='nan'
                else:
                    window_size = len(method_data)
                    print(method_data)
                    print(window_size)
                    e_scores = np.round(method_data['Result'] - method_data['Average'], 2)
                    avg_delta_moving_avg = calculate_moving_average(e_scores, window_size)
                    delta_moving_avg_avg = np.nanmean(avg_delta_moving_avg)
                    avg_z_score = method_data['Z-Score'].tail(num_values).mean()
                
                  
                summary_data.append({
                    'Method': method,
                    'AvgDeltaMovingAvg': delta_moving_avg_avg,
                    'AvgZScore': avg_z_score
                })
    
        return summary_data
    


    @app.callback(
    Output('graphs-title', 'children'),
    [Input('method-dropdown', 'value'),
     Input('first-letter-dropdown', 'value'),
     Input('stored-method-names', 'data')]
    )    
    def update_graphs_title(selected_method, first_letter, stored_names):
        if not selected_method:
            return html.H2('Dashboard', style={'font-family': 'Calibri'})

        method_name = stored_names.get(selected_method, selected_method)
        if first_letter:
            return html.H2(f'{method_name} - {first_letter}', style={'font-family': 'Calibri'})
        return html.H2(f'{method_name}', style={'font-family': 'Calibri'})
    
    @app.callback(
        Output('comment-textarea', 'value'),
        [Input('method-dropdown', 'value')],
        [State('comments-store', 'data')]
    )
    def load_comment(selected_method, comments_data):
        if selected_method and comments_data:
            return comments_data.get(selected_method, '')
        return ''
    

    
    @app.callback(
    [Output('z-score-graph', 'figure'),
     Output('z-score-moving-average-graph', 'figure'),
     Output('delta-moving-average-graph', 'figure'),
     Output('z-prime-graph', 'figure'),
     Output('data-grid', 'columnDefs'),
     Output('data-grid', 'rowData')],
    [Input('method-dropdown', 'value'),
     Input('first-letter-dropdown', 'value'),
     Input('interval-component', 'n_intervals'),
     Input('column-checklist', 'value'),
     Input('column-checklist2', 'value'),
     Input('num-values-input', 'value'),
     Input('methods-table', 'data')]
)
    def update_graphs_and_table(selected_method, first_letter, n, checklist1, checklist2, num_values, methods_table_data):
        selected_columns = checklist1 + checklist2  # Combiner les valeurs des trois Checklists
        df = convert_df
        

    # Convertir la colonne 'Date' en format datetime
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')

    # Convertir la colonne 'Z-Score' en numérique
        df['Z-Score'] = pd.to_numeric(df['Z-Score'], errors='coerce')

    # Filtrer les données pour le selected_method
        filtered_df = df[df['Method'] == selected_method]

    # Filtrer les données par la première lettre du nom si sélectionnée
        if first_letter:
            filtered_df = filtered_df[filtered_df['NOM'].str.startswith(first_letter)]

        filtered_df = filtered_df.sort_values(by='Date')
        filtered_df = filtered_df.dropna(subset=['Z-Score']).sort_values(by='Date').tail(num_values)

        property_id, test_id = get_equivalences(selected_method, methods_table_data)
   #     std_number_value = create_tables_and_calculate_std(property_id, test_id) if property_id and test_id else None

  #     if std_number_value is not None:
   #         delta = filtered_df['Result'] - filtered_df['Average']
  #          z_prime = delta / (std_number_value + (filtered_df['Std Dev'] / filtered_df['Count'])) ** (1 / 2)
  #          z_prime = z_prime.apply(lambda x: round(x, 2))
   #     else:
   #         z_prime = pd.Series([np.nan] * len(filtered_df))

        z_scores = filtered_df['Z-Score'].tolist()
        e_scores = np.round(filtered_df['Result'] - filtered_df['Average'], 2)
        dates = filtered_df['Date'].tolist()
        nom = filtered_df['NOM'].tolist()
        window_size = len(filtered_df)

        print(window_size)

    # Calculer RunSum et Som
        runsum = calculate_runsum(z_scores)
        som = calculate_som(z_scores)

    # Calculer les moyennes mobiles
        z_score_moving_avg = calculate_moving_average(z_scores, window_size)
        delta_moving_avg = calculate_moving_average(e_scores, window_size)
    
        filtered_df['RunSum'] = runsum
        filtered_df['Som'] = som
        filtered_df['e_scores'] = e_scores
        z_prime = z_scores

        
        

        
        z_score_avg = np.nanmean(z_scores)
        z_prime_avg = np.nanmean(z_prime)
        z_score_moving_avg_avg = np.nanmean(z_score_moving_avg)
        delta_moving_avg_avg = np.nanmean(delta_moving_avg)

        z_score_fig = {
        'data': [{'x': nom, 'y': z_scores, 'type': 'line', 'name': 'Z-Score', 'line': {'color': '#1f77b4', 'width': 3}}],
        'layout': {
            'title': {'text': f'Score Z', 'x': 0.5},

            'plot_bgcolor': '#f9f9f9',
            'paper_bgcolor': '#f9f9f9',
            'font': {'family': 'Arial, sans-serif', 'size': 14, 'color': '#333'},
            'hovermode': 'closest',
            'shapes': [
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': 2, 'y1': 2, 'line': {'color': 'red', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': -2, 'y1': -2, 'line': {'color': 'red', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': 0, 'y1': 0, 'line': {'color': 'green', 'width': 2}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': z_score_avg, 'y1': z_score_avg, 'line': {'color': 'blue', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {
                    'x': 1, 'y': 1.1, 'xref': 'paper', 'yref': 'paper',
                    'text': f'Valeur moyenne: {z_score_avg:.2f}', 'showarrow': False,
                    'xanchor': 'right', 'yanchor': 'top'
                }
            ]
        }
    }

        z_prime_fig = {
        'data': [{'x': nom, 'y': z_prime, 'type': 'line', 'name': "Z'", 'line': {'color': '#d62728', 'width': 3}}],
        'layout': {
            'title': {'text': f"Score Z'", 'x': 0.5},
 
            'plot_bgcolor': '#f9f9f9',
            'paper_bgcolor': '#f9f9f9',
            'font': {'family': 'Arial, sans-serif', 'size': 14, 'color': '#333'},
            'hovermode': 'closest',
            'shapes': [
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': 2, 'y1': 2, 'line': {'color': 'red', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': -2, 'y1': -2, 'line': {'color': 'red', 'width': 2, 'dash': 'dash'}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': 0, 'y1': 0, 'line': {'color': 'green', 'width': 2}},
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': z_prime_avg, 'y1': z_prime_avg, 'line': {'color': 'blue', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {
                    'x': 1, 'y': 1.1, 'xref': 'paper', 'yref': 'paper',
                    'text': f"Valeur moyenne: {z_prime_avg:.2f}", 'showarrow': False,
                    'xanchor': 'right', 'yanchor': 'top'
                }
            ]
        }
    }

        z_score_moving_avg_fig = {
        'data': [{'x': nom, 'y': z_score_moving_avg, 'type': 'bar', 'name': 'Z-Score Moving Average', 'line': {'color': '#ff7f0e', 'width': 3}}],
        'layout': {
            'title': {'text': f'Z-Score Moving Average', 'x': 0.5},

            'plot_bgcolor': '#f9f9f9',
            'paper_bgcolor': '#f9f9f9',
            'font': {'family': 'Arial, sans-serif', 'size': 14, 'color': '#333'},
            'hovermode': 'closest',
            'shapes': [
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': z_score_moving_avg_avg, 'y1': z_score_moving_avg_avg, 'line': {'color': 'blue', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {
                    'x': 1, 'y': 1.1, 'xref': 'paper', 'yref': 'paper',
                    'text': f'Valeur moyenne: {z_score_moving_avg_avg:.2f}', 'showarrow': False,
                    'xanchor': 'right', 'yanchor': 'top'
                }
            ]
        }
    }

        delta_moving_avg_fig = {
        'data': [{'x': nom, 'y': delta_moving_avg, 'type': 'bar', 'name': 'Delta Moving Average', 'line': {'color': '#2ca02c', 'width': 3}}],
        'layout': {
            'title': {'text': f'Delta Moving Average', 'x': 0.5},
            'plot_bgcolor': '#f9f9f9',
            'paper_bgcolor': '#f9f9f9',
            'font': {'family': 'Arial, sans-serif', 'size': 14, 'color': '#333'},
            'hovermode': 'closest',
            'shapes': [
                {'type': 'line', 'x0': 0, 'x1': 1, 'xref': 'paper', 'y0': delta_moving_avg_avg, 'y1': delta_moving_avg_avg, 'line': {'color': 'blue', 'width': 2, 'dash': 'dash'}}
            ],
            'annotations': [
                {
                    'x': 1, 'y': 1.1, 'xref': 'paper', 'yref': 'paper',
                    'text': f'Valeur moyenne: {delta_moving_avg_avg:.2f}', 'showarrow': False,
                    'xanchor': 'right', 'yanchor': 'top'
                }
            ]
        }
    }

    # Arrondir les valeurs à deux décimales dans filtered_df
        filtered_df = filtered_df.round(2)

    # Mettre à jour les colonnes du tableau selon la sélection de l'utilisateur
        full_column_defs = [
        {'field': 'Date', 'headerName':'Date', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'NOM', 'headerName':'Nom', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Units', 'headerName':'Unité', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Z-Score', 'headerName':'Score Z', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Result', 'headerName':'Résultat', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Average', 'headerName':'Moyenne', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Std Dev', 'headerName':'Écart type', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Count', 'headerName':'Nombre', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'e_scores', 'headerName':'Score E', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Rdat', 'headerName':'R_dat', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Rpub', 'headerName':'R_pub', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {'field': 'Comment', 'headerName':'Commentaire', 'cellStyle': {'color': 'black', 'flex': '1 1 auto'}},
        {
            'field': 'RunSum',
            'headerName':'RunSum',
            'cellStyle': {
                'flex': '1 1 auto',
                'styleConditions': [
                    {
                        'condition': 'params.value > 5',
                        'style': {'color': 'red'}
                    }
                ]
            }
        },
        {
            'field': 'Som',
            'headerName':'Somme',
            'cellStyle': {
                'flex': '1 1 auto',
                'styleConditions': [
                    {
                        'condition': 'params.value > 6',
                        'style': {'color': 'red'}
                    }
                ]
            }
        }
    ]

    # Filtrer les colonnes sélectionnées
        column_defs = [col for col in full_column_defs if col['field'] in selected_columns]

        row_data = filtered_df[selected_columns].to_dict('records')

        return z_score_fig, z_score_moving_avg_fig, delta_moving_avg_fig, z_prime_fig, column_defs, row_data

    return app.server


app = Flask(__name__)

app = init_dashboard()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8050)
    






