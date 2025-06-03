import dash
import plotly.express as px
import pandas as pd
from dash.dependencies import Input, Output
import plotly.figure_factory as ff
import dash
from dash.dependencies import Input, Output,State
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash import dcc,html


def create_missing_dash_application(flask_app):
    dash_app = dash.Dash(
        server=flask_app, 
        name="Dashboard", 
        url_base_pathname="/missingvalue/", 
        external_stylesheets=[dbc.themes.DARKLY]
    )

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

    colors = {
        'background': '#333333',
        'text': 'white'
    }

    layout = html.Div([
        navbar,
        html.H1("Non-Missing Values Analysis", style={'color': colors['text']}),
        dcc.Graph(
            id='non-missing-values-bar',
            figure={
                'layout': {
                    'plot_bgcolor': colors['background'],
                    'paper_bgcolor': colors['background'],
                    'font': {
                        'color': colors['text']
                    }
                }
            }
        )
    ], style={'backgroundColor': colors['background']})

    dash_app.layout = layout
    return dash_app

def update_dash_app(dash_app, df):  
    print("DataFrame Present:",df.columns[2])
    if df is not None and not df.empty:
        non_missing_values = df.notnull().sum()
        non_missing_df = pd.DataFrame({'Column': non_missing_values.index, 'Non-Missing Values': non_missing_values.values})

        fig = px.bar(non_missing_df, x='Column', y='Non-Missing Values',
                     labels={'Column': 'Columns', 'Non-Missing Values': 'Number of Non-Missing Values'})
        fig.update_traces(marker_color='#FEE600')
        fig.update_layout(
            plot_bgcolor='#333333',
            paper_bgcolor='#333333',
            font=dict(color='white')
        )

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

        colors = {
            'background': '#333333',
            'text': 'white'
        }

        layout = html.Div([
            navbar,
            html.H1("Non-Missing Values Analysis", style={'color': colors['text']}),
            dcc.Graph(
                id='non-missing-values-bar',
                figure=fig  # Use the updated figure here
            )
        ], style={'backgroundColor': colors['background']})

        dash_app.layout = layout

def create_cm_dash(flask_app):
    dash_app = dash.Dash(
        server=flask_app, 
        name="Dashboard", 
        url_base_pathname="/correlationmatrix/", 
        external_stylesheets=[dbc.themes.DARKLY]
    )

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

    colors = {
        'background': '#333333',
        'text': 'white'
    }

    layout = html.Div([
        navbar,
        html.H1("Correlation Matrix", style={'color': colors['text']}),
        html.Div([
            dcc.Dropdown(
                id='dropdown1',
                value=None,
                placeholder="Select column",
                style={'margin-bottom': '10px'}
            ),
            dcc.Dropdown(
                id='dropdown2',
                value=None,
                placeholder="Select column"
            ),
        ], style={'width': '50%', 'margin': '0 auto', 'display': 'flex', 'flexDirection': 'column'}),
        dcc.Graph(id='heatmap', 
                  figure={'layout': {'plot_bgcolor': colors['background'], 'paper_bgcolor': colors['background'], 'font': {'color': colors['text']}}},
                  style={'height': '600px'}  # Set the height of the heatmap
        ),
        dcc.Store(id='stored-data')
    ], style={'backgroundColor': colors['background']})

    dash_app.layout = layout

    @dash_app.callback(
        Output('heatmap', 'figure'),
        [Input('dropdown1', 'value'), Input('dropdown2', 'value')],
        State('stored-data', 'data')
    )
    def update_heatmap(column1, column2, data):
        df = pd.read_json(data, orient='split')
        if column1 is None and column2 is None:
            numeric_columns = df.select_dtypes(include=['number'])
            correlation_matrix = numeric_columns.corr()
            x = correlation_matrix.columns.tolist()
            y = correlation_matrix.index.tolist()
            z = correlation_matrix.values
        else:
            selected_correlation_matrix = df[[column1, column2]].corr()
            x = [column1, column2]
            y = [column1, column2]
            z = selected_correlation_matrix.values

        fig = go.Figure(data=go.Heatmap(
            z=z,
            x=x,
            y=y,
            colorscale=[
                [0, 'grey'],
                [0.5, '#FFE600'],
                [1, 'grey']
            ],
            showscale=True,
            colorbar=dict(title='Correlation'),
            text=z,
            texttemplate="%{text:.2f}",
            hoverinfo='text',
            zmid=0  # Add midpoint for the color scale
        ))
        fig.update_layout(
            height=600,  # Set the height of the heatmap
            plot_bgcolor='black',
            paper_bgcolor='#333333',
            font=dict(color='white'),
            xaxis=dict(tickfont=dict(color='white')),
            yaxis=dict(tickfont=dict(color='white')),
        )
        return fig

    return dash_app

def update_cm_dash(dash_app, df):
    if df is not None and not df.empty:
        numeric_columns = df.select_dtypes(include=['number'])
        correlation_matrix = numeric_columns.corr()
        column_names = correlation_matrix.columns.tolist()

        dropdown1_options = [{'label': col, 'value': col} for col in column_names]
        dropdown2_options = dropdown1_options

        dash_app.layout = html.Div([
            dash_app.layout.children[0],  # navbar
            html.H1("Correlation Matrix", style={'color': '#FFFFFF'}),
            html.Div([
                dcc.Dropdown(
                    id='dropdown1',
                    options=dropdown1_options,
                    value=None,
                    placeholder="Select column",
                    style={'color': 'black', 'margin-bottom': '10px'}
                ),
                dcc.Dropdown(
                    id='dropdown2',
                    options=dropdown2_options,
                    value=None,
                    placeholder="Select column",
                    style={'color': 'black'}
                ),
            ], style={'width': '50%', 'margin': '0 auto', 'display': 'flex', 'flexDirection': 'column'}),
            dcc.Graph(id='heatmap',
                      figure={
                          'data': [
                              go.Heatmap(
                                  z=correlation_matrix.values,
                                  x=column_names,
                                  y=column_names,
                                  colorscale=[
                                      [0, 'grey'],
                                      [0.5, '#FFE600'],
                                      [1, 'grey']
                                  ],
                                  showscale=True,
                                  colorbar=dict(title='Correlation'),
                                  text=correlation_matrix.values,
                                  texttemplate="%{text:.2f}",
                                  hoverinfo='text',
                                  zmid=0  # Add midpoint for the color scale
                              )
                          ],
                          'layout': {
                              'height': 600,  # Set the height of the heatmap
                              'plot_bgcolor': '#333333',
                              'paper_bgcolor': '#333333',
                              'font': {'color': 'white'},
                              'xaxis': {'tickfont': {'color': 'white'}},
                              'yaxis': {'tickfont': {'color': 'white'}},
                          }
                      },
                      style={'height': '600px'}  # Set the height of the heatmap
            ),
            dcc.Store(id='stored-data', data=df.to_json(orient='split'))  # Store the DataFrame in client-side storage
        ], style={'backgroundColor': '#333333'})

    else:
        dash_app.layout = html.Div([
            dash_app.layout.children[0],  # navbar
            html.H1("No Data Available", style={'color': '#FFFFFF'})
        ], style={'backgroundColor': '#333333'})

    return dash_app