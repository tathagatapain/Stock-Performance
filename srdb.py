#!/usr/bin/env python
# coding: utf-8

# In[20]:


from dash import Dash, html, dcc, callback, Output, Input, dash_table, State
from dash.exceptions import PreventUpdate
import plotly.express as px
import pandas as pd
import base64
import io
from datetime import datetime, date
import dash_ag_grid

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

# Create Dash app
app = Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)

# Initialize global variable to store uploaded data
uploaded_data = None

# Layout for data upload tab
data_upload_layout = html.Div([
    html.H2("Upload Data", style={'textAlign': 'center', 'color': 'white'}),
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '98%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px',
            'color': 'white',
            'background-color': '#333'
        },
        # Allow multiple files to be uploaded
        multiple=False
    ),
    html.Div(id='output-data-upload', style={'margin': '20px'})
])

# Layout for page 1
page_1_layout = html.Div(id='page-1-content')

# Callback to update page 1 components based on uploaded data
@app.callback(
    Output('page-1-content', 'children'),
    [Input('upload-data', 'contents')]
)
def update_page1(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Update global variable
        global uploaded_data
        uploaded_data = df

        return html.Div([
            html.H2("Stock Performance Summary", style={'textAlign': 'center', 'color': 'white'}),
            html.Hr(style={'border-color': 'white'}),
            html.Div([
                html.Div([
                    html.Label("Select Index:", style={'color': 'white'}),
                    dcc.Dropdown(
                        id='index-dropdown',
                        options=[
                            {'label': 'Nifty 50', 'value': 'Nifty 50 Returns'},
                            {'label': 'Dow Jones Index', 'value': 'Dow Jones Index Returns'},
                            {'label': 'Nasdaq', 'value': 'Nasdaq Returns'},
                            {'label': 'Hang Seng', 'value': 'Hang Seng Returns'},
                            {'label': 'Nikkei 225', 'value': 'Nikkei 225 Returns'},
                            {'label': 'DAX', 'value': 'DAX Returns'}
                        ],
                        value='Nifty 50 Returns',  # Select Nifty 50 as default
                        style={'width': '200px', 'color': 'black'}
                    ),
                ], style={'display': 'inline-block', 'margin-right': '10px'}),
                html.Div([
                    html.Label("Select Year:", style={'color': 'white'}),
                    dcc.Slider(
                        id='year-slider',
                        min=df['Year'].min(),
                        max=df['Year'].max(),
                        value=df['Year'].min(),
                        marks={year: str(year) for year in range(df['Year'].min(), df['Year'].max() + 1)},
                        step=None
                    ),
                ], style={'display': 'inline-block', 'width': '70%'})
            ]),
            html.Div([
            html.Div([
                dash_table.DataTable(
                    id='summary-table',
                    columns=[],
                    data=[],
                    style_cell={'textAlign': 'center', 'color': 'white', 'backgroundColor': '#444'},  # Adjust text alignment and background color of table cells
                    style_header={'backgroundColor': '#333'},  # Adjust background color of header cells
                    style_table={'width': '100%', 'float': 'left', 'margin-bottom': '20px', 'background-color': '#444'}
                ),
            ], style={'width': '50%', 'display': 'inline-block', 'margin-right': '10px'}),
                
            html.Div([
                dcc.Graph(id='returns-piechart'),
            ], style={'width': '45%', 'float': 'right', 'display': 'inline-block', 'border': '2px solid white', 'border-radius': '5px', 'padding': '10px'}),
        ]),

            html.Div([
                dcc.Graph(id='returns-boxplot', style={'width': '47%', 'display': 'inline-block','border': '2px solid white', 'border-radius': '5px', 'padding': '10px'})
            ])
        ], style={'background-color': '#222', 'padding': '20px'})
    else:
        return html.Div()

# Callback to update page 1 components based on user input
@app.callback(
    [Output('summary-table', 'columns'),
     Output('summary-table', 'data'),
     Output('returns-boxplot', 'figure'),
     Output('returns-piechart', 'figure')],
    [Input('index-dropdown', 'value'),
     Input('year-slider', 'value')]
)
def update_page1_components(index_name, selected_year):
    if uploaded_data is not None:
        # Filter data based on selected index and year
        data = uploaded_data[(uploaded_data['Year'] == selected_year)]

        # Summary statistics table for the selected index column
        summary_table_data = data.describe().reset_index().rename(columns={'index': 'Statistic'})
        summary_table_data = summary_table_data[['Statistic', index_name]].round(2)

        # Format summary table data
        formatted_data = [{'Statistic': row['Statistic'], index_name: row[index_name]} for _, row in
                          summary_table_data.iterrows()]

        # Boxplot of returns
        boxplot = px.box(data, x=index_name)
        boxplot.update_layout(title_text=f'{index_name} ({selected_year})', title_x=0.5, font_size=9, plot_bgcolor='#222', paper_bgcolor='#222')

        # Pie chart of positive and negative returns
        positive_returns = (data[index_name] > 0).sum()
        negative_returns = (data[index_name] < 0).sum()
        labels = ['Positive Returns', 'Negative Returns']
        values = [positive_returns, negative_returns]

        piechart = px.pie(names=labels, values=values)
        piechart.update_layout(title_text=f'Percentage Positive and Negative {index_name} ({selected_year})',
                               title_x=0.5, font_size=9, plot_bgcolor='#222', paper_bgcolor='#222')

        return [{'name': i, 'id': i} for i in summary_table_data.columns], formatted_data, boxplot, piechart
    else:
        return [], [], {}, {}

# Layout for page 2
page_2_layout = html.Div(id='page-2-content')

# Callback to update page 2 components based on uploaded data
@app.callback(
    Output('page-2-content', 'children'),
    [Input('upload-data', 'contents')]
)
def update_page2(contents):
    if contents is not None:
        return html.Div([
            html.H2("Correlation Matrix", style={'textAlign': 'center', 'color': 'white'}),
            html.Label("Select Indices (select at least 2):", style={'color': 'white'}),
            dcc.Dropdown(
                id='index-dropdown-page2',
                options=[
                    {'label': 'Nifty 50', 'value': 'Nifty 50 Returns'},
                    {'label': 'Dow Jones Index', 'value': 'Dow Jones Index Returns'},
                    {'label': 'Nasdaq', 'value': 'Nasdaq Returns'},
                    {'label': 'Hang Seng', 'value': 'Hang Seng Returns'},
                    {'label': 'Nikkei 225', 'value': 'Nikkei 225 Returns'},
                    {'label': 'DAX', 'value': 'DAX Returns'}
                ],
                value=['Nifty 50 Returns', 'DAX Returns'],  # Select Nifty 50 and Dow Jones Index as default
                multi=True,
                style={'color': 'black'}
            ),
            dcc.Graph(id='correlation-matrix', style={'border': '2px solid white', 'border-radius': '5px', 'padding': '10px'}),
        ], style={'background-color': '#222', 'padding': '20px', 'color': 'white'})
    else:
        return html.Div()

# Callback to update page 2 components based on user input
@app.callback(
    Output('correlation-matrix', 'figure'),
    [Input('index-dropdown-page2', 'value')]
)
def update_page2_components(selected_indices):
    if uploaded_data is not None:
        # Filter data for selected indices
        selected_data = uploaded_data[selected_indices]

        # Compute correlation matrix
        correlation_matrix = selected_data.corr()

        # Plot correlation matrix
        fig = px.imshow(correlation_matrix,
                        labels=dict(color="Correlation"),
                        x=correlation_matrix.index,
                        y=correlation_matrix.columns, text_auto = True)

        fig.update_layout(plot_bgcolor='#222', paper_bgcolor='#222')

        return fig
    else:
        return {}

# Callback to display a snippet of the uploaded data
@app.callback(
    Output('output-data-upload', 'children'),
    [Input('upload-data', 'contents')]
)
def display_uploaded_data(contents):
    if contents is not None:
        content_type, content_string = contents.split(',')

        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        # Display a snippet of the data
        snippet_table = dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[
                    {'name': df.columns[i], 'id': df.columns[i]} for i in range(1, 13)
                    ],
            style_table={'overflowX': 'auto','color': 'white'},  # Adjust text color
            style_cell={'textAlign': 'center', 'width': '50%', 'background-color': '#444'},  # Adjust background color
            style_header={'backgroundColor': '#333'},  # Adjust header background color
        )

        return html.Div([
            snippet_table
        ])
    else:
        return html.Div()

# Layout for page 3
page_3_layout = html.Div([
    html.H2("Data Display", style={'textAlign': 'center', 'color': 'white'}),
#date picker range
    html.Div([
    dcc.DatePickerRange(
    id='my-date-picker-range',
    start_date_placeholder_text="Start Date",
    end_date_placeholder_text="End Date",
    style={'margin': '20px'},
),
    html.Div(id='output-container-date-picker-range'),
    html.Div(id='returns-output')
    
    
])
    ])


@app.callback(
    [Output('output-container-date-picker-range', 'children'),
    Output('returns-output', 'children',allow_duplicate=True)],
    [Input('my-date-picker-range', 'start_date'),
    Input('my-date-picker-range', 'end_date'),
    Input('upload-data', 'contents')],
    prevent_initial_call=True
)
def update_output1(start_date, end_date, contents):
    if contents is None or start_date is None or end_date is None:
        # Return empty Divs if any of the inputs are None
        return html.Div(), html.Div()
    
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    
    df = df[['Date','Nifty 50 Adj Close','Dow Jones Index Adj Close','Nasdaq Adj Close','Hang Seng Adj Close']]
    # Convert date columns to datetime objects if they're not already in that format
    df['Date'] = pd.to_datetime(df['Date'])
    
    # Parse start_date and end_date directly as they're already in the correct format
    start_date = datetime.strptime(start_date, '%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d')
    
    # Filter the DataFrame based on the parsed start_date and end_date
    newdf = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
    
    newdf = newdf.set_index('Date')
    newdf = newdf.apply(pd.to_numeric, errors='coerce')

    # Calculate percentage change
    returns_df = newdf.pct_change() * 100
    
    # Change column names
    returns_df = returns_df.rename(columns={
                'Nifty 50 Adj Close': 'Nifty 50 Returns',
                'Dow Jones Index Adj Close': 'Dow Jones Index Returns',
                'Nasdaq Adj Close': 'Nasdaq Returns',
                'Hang Seng Adj Close': 'Hand Seng Returns',
                'Nikkei 225 Adj Close': 'Nikkei 225 Returns',
                'DAX Adj Close': 'DAX Returns'
            })
    
    return (
        html.Div([
            html.H4('Closing Prices', style = {'textAlign':'center'}),
            dash_table.DataTable(
                id='table',
                data=newdf.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in newdf.columns],
                page_size=10,
                style_table={'overflowX': 'auto', 'color': 'white'},  # Adjust text color
                style_cell={'textAlign': 'center', 'width': '50%', 'background-color': '#444'},  # Adjust background color
                style_header={'backgroundColor': '#333'},  # Adjust header background color
                editable = True
            )
        ]),
        html.Div([
            html.Br(),
            html.H4('Returns Table', style = {'textAlign':'center'}),
            dash_table.DataTable(
                id='returns-table',
                data=returns_df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in returns_df.columns],
                page_size=10,
                style_table={'overflowX': 'auto', 'color': 'white'},  # Adjust text color
                style_cell={'textAlign': 'center', 'width': '50%', 'background-color': '#444'},  # Adjust background color
                style_header={'backgroundColor': '#333'},  # Adjust header background color
            )
        ])
    )

# Callback to update returns_df when newdf changes
@app.callback(
    Output('returns-output', 'children'),
    [Input('table', 'data')]
)
def update_returns_table(data):
    
    if data is None:
        raise PreventUpdate
        
        
    newdf = pd.DataFrame(data)
    newdf = newdf.apply(pd.to_numeric, errors='coerce')

    returns_df = newdf.pct_change() * 100
    
    # Change column names
    returns_df = returns_df.rename(columns={
                'Nifty 50 Adj Close': 'Nifty 50 Returns',
                'Dow Jones Index Adj Close': 'Dow Jones Index Returns',
                'Nasdaq Adj Close': 'Nasdaq Returns',
                'Hang Seng Adj Close': 'Hand Seng Returns',
                'Nikkei 225 Adj Close': 'Nikkei 225 Returns',
                'DAX Adj Close': 'DAX Returns'
            })
    
    return html.Div([
        html.Br(),
        html.H4('Returns Table', style = {'textAlign':'center'}),
        dash_table.DataTable(
            id='returns-table',
            data=returns_df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in returns_df.columns],
            page_size=10,
            editable=False,
            style_table={'overflowX': 'auto', 'color': 'white'},  # Adjust text color
            style_cell={'textAlign': 'center', 'width': '50%', 'background-color': '#444'},  # Adjust background color
            style_header={'backgroundColor': '#333'},  # Adjust header background color
        )
    ])

# Layout for page 4
page_4_layout = html.Div([
    html.H2("Page 4: Display Data and Add Rows/Columns", style={'textAlign': 'center', 'color': 'white'}),
    
    # Button to add a new column
    html.Div([
        dcc.Input(
            id='new-column-name',
            placeholder='Enter a column name...',
            value='',
            style={'padding': 10}
        ),
        html.Button('Add Column', id='add-column-button', n_clicks=0, style={'margin-left': '10px'}),
    ], style={'display': 'flex', 'alignItems': 'center', 'justifyContent': 'center', 'margin-top': '20px'}),
    
    # Display DataTable
    dash_table.DataTable(
        id='data-table',
        editable=True,
        row_deletable=True,
        column_selectable='single',  # Allow only single column selection for renaming
        selected_columns=[],  # Will be updated dynamically
        selected_rows=[],  # Will be updated dynamically
        style_table={'overflowX': 'auto', 'color': 'white', 'margin-top': '20px'},  # Adjust text color and top margin
        style_cell={'textAlign': 'center', 'width': '50%', 'background-color': '#444'},  # Adjust background color
        style_header={'backgroundColor': '#333'},  # Adjust header background color
    ),
    
    # Button to add a new row
    html.Div(html.Button('Add Row', id='add-row-button', n_clicks=0), style={'textAlign': 'center', 'margin-top': '20px'}),
    
    # Hidden divs to store intermediate values
    html.Div(id='intermediate-value', style={'display': 'none'})
])

# Define callback to update DataTable with data and columns
@app.callback(
    Output('data-table', 'columns', allow_duplicate = True),
    Output('data-table', 'data'),
    Input('upload-data', 'contents'),
    prevent_initial_call=True
)
def update_table(contents):
    if contents is not None:
        # Parse uploaded file and extract data
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
        df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        
        # Remove unnecessary columns
        df=df.drop(['Unnamed: 0', 'Year'], axis = 1)
        
        # Convert DataFrame columns to dict for DataTable columns
        columns = [{'name': col, 'id': col} for col in df.columns]
        
        # Convert DataFrame rows to list of dicts for DataTable data
        data = df.to_dict('records')
        
        return columns, data
    else:
        # If no data uploaded yet, return empty columns and data
        return [], []

# Callback to add new column
@app.callback(
    Output('data-table', 'columns', allow_duplicate = True),
    Input('add-column-button', 'n_clicks'),
    State('new-column-name', 'value'),
    State('data-table', 'columns'),
    prevent_initial_call=True
)
def add_column(n_clicks, column_name, existing_columns):
    if n_clicks > 0 and column_name:
        existing_columns.append({'name': column_name, 'id': column_name})
    return existing_columns

# Callback to add new row
@app.callback(
    Output('data-table', 'data', allow_duplicate = True),
    Input('add-row-button', 'n_clicks'),
    State('data-table', 'data'),
    State('data-table', 'columns'),
    prevent_initial_call=True
)
def add_row(n_clicks, rows, columns):
    if n_clicks > 0:
        rows.append({c['id']: '' for c in columns})
    return rows

# Add to layout to the app
app.layout = html.Div([
    dcc.Tabs([
        dcc.Tab(label='Upload Data', children=[data_upload_layout], style={'backgroundColor': '#222', 'color': 'white'}),
        dcc.Tab(label='Page 1', children=[page_1_layout], style={'backgroundColor': '#222', 'color': 'white'}),
        dcc.Tab(label='Page 2', children=[page_2_layout], style={'backgroundColor': '#222', 'color': 'white'}),
        dcc.Tab(label='Page 3', children=[page_3_layout], style={'backgroundColor': '#222', 'color': 'white'}),
        dcc.Tab(label='Page 4', children=[page_4_layout], style={'backgroundColor': '#222', 'color': 'white'})
    ])
], style={'background-color': '#222', 'color': 'white'})

if __name__ == '__main__':
    app.run_server(debug=True, port=4050)

