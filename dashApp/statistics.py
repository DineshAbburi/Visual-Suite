import dash
from dash import html
import plotly.express as px
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import dcc
import seaborn as sns
from flask import url_for
# from app import server



def create_stats_dash(flask_app):
    dash_app = dash.Dash(
        server=flask_app,
        name="Dashboard",
        url_base_pathname="/statistics/",
        external_stylesheets=[dbc.themes.DARKLY]
    )

    @flask_app.context_processor
    def inject_flask_urls():
        return{
            'Feature_eng': url_for('transformations')
        }


    @dash_app.callback(
        Output('column-dropdown', 'options'),
        Input('column-dropdown', 'value'),
        State('stored-data', 'data')
    )
    def update_dropdown_options(selected_column, data):
        try:
            if data is None:
                return []
            df = pd.read_json(data, orient='split')
            numeric_columns = df.select_dtypes(include=['number'])
            column_names = numeric_columns.columns.tolist()
            dropdown_options = [{'label': col, 'value': col} for col in column_names]
            return dropdown_options
        except Exception as e:
            print(f"Error in update_dropdown_options: {e}")
            return []

    @dash_app.callback(
        [Output('column-stats', 'children'), 
         Output('column-plot', 'children')],  
        [Input('column-dropdown', 'value'),
         Input('plot-type-radio', 'value')],
        State('stored-data', 'data')
    )
    def update_content(selected_column, plot_type, data):
        try:
            if data is None:
                return dcc.Markdown("No data available."), ""
            
            df = pd.read_json(data, orient='split')
            stats_content = dcc.Markdown("No column selected.")
            plot_content = ""

            if selected_column:
                # Compute main statistics
                stats = df[selected_column].describe()

                # Format each statistic into a string with a newline between them
                stats_str = "\n".join([f"{stat_name}: {stat_value}\n" for stat_name, stat_value in stats.items()])

                # Remove the trailing newline character
                stats_str = stats_str.rstrip("\n")

                # Compute outliers
                Q1 = df[selected_column].quantile(0.25)
                Q3 = df[selected_column].quantile(0.75)
                IQR = Q3 - Q1
                outliers = df[(df[selected_column] < (Q1 - 1.5 * IQR)) | (df[selected_column] > (Q3 + 1.5 * IQR))][selected_column]
                unique_outliers = outliers.unique()

                # Unique values
                unique_values = df[selected_column].nunique()

                # Create a plot for the selected column
                if plot_type == 'histogram':
                    fig = px.histogram(df, x=selected_column, nbins=30)

                    # Calculate KDE using seaborn
                    kde_values = sns.kdeplot(df[selected_column], color='red').get_lines()[0].get_data()

                    # Add KDE curve to the plot
                    fig.add_scatter(x=kde_values[0], y=kde_values[1], mode='lines', line=dict(color='red', width=2))
                elif plot_type == 'boxplot':
                    fig = px.box(df, y=selected_column)
                else:
                    fig = {}

                fig.update_layout(
                    plot_bgcolor='#333333',
                    paper_bgcolor='#333333',
                    font=dict(color='white')
                )

                # Format the outliers and unique values
                outliers_str = "\n".join([f"{outlier}" for outlier in unique_outliers])
                unique_values_str = f"Unique Values: {unique_values}"                       

                # Concatenate all strings
                stats_content = dcc.Markdown(f"\n{stats_str}\n\n**Outliers:**\n{outliers_str}\n\n{unique_values_str}")
                plot_content = dcc.Graph(figure=fig, style={'width': '100%', 'height': '100%'})

            return stats_content, plot_content
        except Exception as e:
            print(f"Error in update_content: {e}")
            return dcc.Markdown("Error processing data."), ""



    navbar = dbc.Navbar(
    dbc.Container([
        dbc.NavbarBrand("EDA Dashboard", className="text-white fw-bold"),
        dbc.Nav([
            dbc.DropdownMenu(
                label="Pre-Processing",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("Feature Engineering", href='/transformations',external_link=True),
                    dbc.DropdownMenuItem("Duplicates", href="/duplicates/",external_link=True)
                ]
            ),
            dbc.DropdownMenu(
                label="Visualize",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("Describe", href="/describe",external_link=True),
                    dbc.DropdownMenuItem("Missing Analysis", href="/missingvalue/",external_link=True),
                    dbc.DropdownMenuItem("Co-Relations", href="/correlationmatrix/",external_link=True),
                    dbc.DropdownMenuItem("Charts", href="/charts",external_link=True)
                ]
            ),
            dbc.DropdownMenu(
                label="Regression",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("Regression Models", href="/regression",external_link=True),
                    dbc.DropdownMenuItem("Comparative Analysis", href="/comparativeanalysis",external_link=True),
                    dbc.DropdownMenuItem("Feature Importance", href="/featureimportance",external_link=True)
                ]
            ),
            dbc.DropdownMenu(
                label="Report",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("Generate Report", href="/download_report",external_link=True),
                    dbc.DropdownMenuItem("Export Data", href="/export_data",external_link=True)  # Replace with actual route if using Flask url_for
                ]
            ),
            dbc.DropdownMenu(
                label="Settings",
                nav=True,
                in_navbar=True,
                children=[
                    dbc.DropdownMenuItem("Logout", href="/logout",external_link=True)  # Replace with actual route if using Flask url_for
                ]
            ),
        ], className="ms-auto", navbar=True)
    ]),
    color="dark",
    dark=True,
    sticky='top',
    className="shadow"
)
    options = []
    dash_app.layout = html.Div(
        children=[
            # html.Link(rel="stylesheet", href="/assets/style.css"),
            html.Div(navbar),
            html.Div(
                className="container-fluid",
                children=[
                    html.Div(
                        className="row",
                        children=[
                            html.Div(
                                className="col-md-4",
                                children=[
                                    html.Div(
                                        className="data-preview p-4",
                                        children=[
                                            html.H3("Column Statistics", style={'font-size': '24px'}),
                                            
                                            dcc.Dropdown(
                                                id='column-dropdown',
                                                
                                                options=[],           
                                                value=None,                
                                                placeholder="Select a column",
                                                style={'backgroundColor': '#444444', 'color': '#ffffff', 'font-size': '16px'},
                                                # dropdownStyle = {'color':'black'}
                                                className="custom-dropdown",
                                                
                                                #dropdown_menu_style = {'backgroundColor': '#333333', 'color': '#FFFFFF'   }
                                            ),

                                            html.Div(id="column-stats", className='mt-4', style={'font-size': '16px', 'color': 'white'})
                                        ]
                                    )
                                ]
                            ),
                            html.Div(
                                className="col-md-8",
                                children=[
                                    html.Div(
                                        className="data-visualization p-4",
                                        children=[
                                            html.H4(id='selected-column-heading', style={'text-align': 'center', 'color': 'white', 'margin-bottom': '20px'}),
                                            html.Div(
                                                className="radio-buttons",
                                                children=[
                                                    dcc.RadioItems(
                                                        id='plot-type-radio',
                                                        options=[
                                                            {'label': 'Box Plot', 'value': 'boxplot'},
                                                            {'label': 'Histogram', 'value': 'histogram'}
                                                        ],
                                                        value='histogram',
                                                        labelStyle={'display': 'inline-block', 'color': 'white', 'margin-right': '20px'},
                                                        inputStyle={"margin-right": "10px"}
                                                    )
                                                ],
                                                style={'margin-bottom': '20px', 'text-align': 'center'}
                                            ),
                                            html.Div(id="column-plot", style={'width': '100%', 'height': '100%'})
                                        ]
                                    )
                                ]
                            )
                        ]
                    ),
                ],
                style={'height': 'calc(100vh - 70px)', 'overflowY': 'auto', 'backgroundColor': '#222222'}
            ),
            dcc.Store(id='stored-data')
        ],
        style={'width': '100%', 'backgroundColor': '#333333'}
    )

    @dash_app.callback(
        Output('selected-column-heading', 'children'),
        Input('column-dropdown', 'value')
    )
    def update_heading(selected_column):
        if selected_column:
            return selected_column
        return ""

    return dash_app

def update_stats_dash(dash_app, df):
    if df is not None and not df.empty:
        df_json = df.to_json(orient='split')
        numeric_columns = df.select_dtypes(include=['number'])
        column_names = numeric_columns.columns.tolist()

        dropdown_options = [{'label': col, 'value': col} for col in column_names]

        
        navbar = dbc.Navbar(
            dbc.Container([
                dbc.NavbarBrand("EDA Dashboard", className="text-white fw-bold"),
                dbc.Nav([
                    dbc.DropdownMenu(
                        label="Pre-Processing",
                        nav=True,
                        in_navbar=True,
                        children=[
                            dbc.DropdownMenuItem("Feature Engineering", href="/transformations",external_link=True),
                            dbc.DropdownMenuItem("Duplicates", href="/duplicates/",external_link=True)
                        ]
                    ),
                    dbc.DropdownMenu(
                        label="Visualize",
                        nav=True,
                        in_navbar=True,
                        children=[
                            dbc.DropdownMenuItem("Describe", href="/describe",external_link=True),
                            dbc.DropdownMenuItem("Missing Analysis", href="/missingvalue/",external_link=True),
                            dbc.DropdownMenuItem("Co-Relations", href="/correlationmatrix/",external_link=True),
                            dbc.DropdownMenuItem("Charts", href="/charts",external_link=True)
                        ]
                    ),
                    dbc.DropdownMenu(
                        label="Regression",
                        nav=True,
                        in_navbar=True,
                        children=[
                            dbc.DropdownMenuItem("Regression Models", href="/regression",external_link=True),
                            dbc.DropdownMenuItem("Comparative Analysis", href="/comparativeanalysis",external_link=True),
                            dbc.DropdownMenuItem("Feature Importance", href="/featureimportance",external_link=True)
                        ]
                    ),
                    dbc.DropdownMenu(
                        label="Report",
                        nav=True,
                        in_navbar=True,
                        children=[
                            dbc.DropdownMenuItem("Generate Report", href="/download_report",external_link=True),
                            dbc.DropdownMenuItem("Export Data", href="/export_data",external_link=True)
                        ]
                    ),
                    dbc.DropdownMenu(
                        label="Settings",
                        nav=True,
                        in_navbar=True,
                        children=[
                            dbc.DropdownMenuItem("Logout", href="/logout")
                        ]
                    ),
                ], className="ms-auto", navbar=True)
            ]),
            color="dark",
            dark=True,
            sticky='top',
            className="shadow"
        )

        dash_app.layout = html.Div(
            children=[
                html.Link(rel="stylesheet", href="/assets/style.css"),
                navbar,
                html.Div(
                    className="container-fluid",
                    children=[
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="col-md-4",
                                    children=[
                                        html.Div(
                                            className="data-preview p-4",
                                            children=[
                                                html.H3("Column Statistics", style={'font-size': '24px'}),

                                                dbc.DropdownMenu(
                                                    label ="Select Column",
                                                    children = [
                                                        dbc.DropdownMenuItem(option['label'], id = f"dropdown-{option['value']}")
                                                        for option in dropdown_options
                                                    ]
                                                ),
                                                dcc.Dropdown(
                                                    id='column-dropdown',
                                                    options=dropdown_options,
                                                    value=None,
                                                    placeholder="Select a column",
                                                    style={'backgroundColor': '#444444', 'color': '#ffffff', 'font-size': '16px'},
                                                    className="custom-dropdown",
                                                    
                                                    #dropdown_style={'backgroundColor': '#333333', 'color': '#ffffff'}
                                                ),
                                               
                                                html.Div(id="column-stats", className='mt-4', style={'font-size': '16px', 'color': 'white'})
                                            ]
                                        )
                                    ]
                                ),
                                html.Div(
                                    className="col-md-8",
                                    children=[
                                        html.Div(
                                            className="data-visualization p-4",
                                            children=[
                                                html.H4(id='selected-column-heading', style={'text-align': 'center', 'color': 'white', 'margin-bottom': '20px'}),
                                                html.Div(
                                                    className="radio-buttons",
                                                    children=[
                                                        dcc.RadioItems(
                                                            id='plot-type-radio',
                                                            options=[
                                                                {'label': 'Histogram', 'value': 'histogram'},
                                                                {'label': 'Box Plot', 'value': 'boxplot'}
                                                            ],
                                                            value='histogram',
                                                            labelStyle={'display': 'inline-block', 'color': 'white', 'margin-right': '20px'},
                                                            inputStyle={"margin-right": "10px"}
                                                        )
                                                    ],
                                                    style={'margin-bottom': '20px', 'text-align': 'center'}
                                                ),
                                                html.Div(id="column-plot", style={'width': '100%', 'height': '100%'})
                                            ]
                                        )
                                    ]
                                )
                            ]
                        ),
                    ],
                    style={'height': 'calc(100vh - 70px)', 'overflowY': 'auto', 'backgroundColor': '#222222'}
                ),
                dcc.Store(id='stored-data', data=df_json)
            ],
            style={'width': '100%', 'backgroundColor': '#333333'}
        )
    else:
        dash_app.layout = html.Div([
            dbc.Navbar(
                [
                    dbc.NavbarBrand(
                        html.Img(src="", height="70px"),
                        className="me-auto",
                        style={'margin-right': '20px'}
                    )
                ],
                color="dark",
                dark=True,
                className='bg-dark'
            ),
            html.Div(
                children=[
                    html.H1("No Data Available", style={'color': '#FFFFFF', 'text-align': 'center', 'margin-top': '20%'})
                ],
                style={'height': '100vh', 'backgroundColor': '#333333'}
            )
        ])

    return dash_app


# /static/images/heading.png