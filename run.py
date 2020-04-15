'''import dash
import dash_html_components as html
import dash_core_components as dcc
import pandas as pd
from dash.dependencies import Input, Output, State
#import requests

#url = 'https://raw.githubusercontent.com/rahulpoddar/dash-deploy-exp/master/TASK1_annotated_1.csv'
df = pd.read_csv('https://raw.githubusercontent.com/rahulpoddar/dash-deploy-exp/master/TASK1_annotated_1.csv', encoding='latin1')

tasks = df['Kaggle Task name'].unique().tolist()

def generate_summary(task):
    return 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'

def generate_table(dff):
    rows = []
    for i in range(len(dff)):
        row = []
        for col in ['Document id_', 'Output']:
            value = dff.iloc[i][col]
            if col == 'Document id_':
                cell = html.Td(html.A(href='https://www.google.com/', children = value))
            else:
                cell = html.Td(children = value)
            row.append(cell)
        rows.append(html.Tr(row))
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in ['Document ID', 'Search Output']]) ] +
        # Body
        rows
    )

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
        html.Div([
        html.H1('COVID-19 Open Research Dataset Challenge (CORD-19)'),
        html.H3('Search a task:'),
        dcc.Dropdown(
        id='task-dropdown',
        options=[
            {'label': i, 'value': i} for i in tasks 
        ],
        placeholder="Select a task",
    ),
    html.H3('Or type a general query:'),
    dcc.Input(id = 'general-search', type = 'text', placeholder = 'Type a query', value = ''),
    html.Button(id='submit-button-state', n_clicks=0, children='Submit'),
    ]),
    
    html.Div([
            html.H3('Sub-Task Questions'),
            html.Div(id = 'sub-task-questions')
            ]),
    html.Div([html.H3('Response Summary', id = 'task-summary-heading'),
    html.Div(id = 'task-summary')]),
    
    html.Div([
            html.H3('Search Results'),
            html.Div(id = 'search-results'),
            html.Div(id = 'query-results')
            ])
])


@app.callback(
    dash.dependencies.Output('task-summary', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def update_summary(value):
    return generate_summary(value)


@app.callback(
    dash.dependencies.Output('search-results', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def update_search_results(value):
    dff = df[df['Kaggle Task name'] == value]
    return generate_table(dff)


@app.callback(
    dash.dependencies.Output('sub-task-questions', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def sub_task_questions(value):
    dff = df[df['Kaggle Task name'] == value]
    results = dff['Search'].unique().tolist()
    return html.P(results)
   
@app.callback(
        Output('query-results', 'children'),
         [Input('submit-button-state', 'n_clicks')],
         [State('general-search', 'value')]
         )
def populate_search_results(n_clicks, value):
    query = value
    response = requests.post("https://nlp.biano-ai.com/develop/test", json={"texts": [query]})
    predictions = response.json()['predictions']
    pred_df = pd.DataFrame(predictions[0])
    pred_df.columns = ['Distance', 'Document id_', 'Output']
    return generate_table(pred_df)
'''
