import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output, State
from flask import Flask
import os
import requests
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import re
import string
from nltk.tokenize import word_tokenize, sent_tokenize

server = Flask(__name__)
server.secret_key = os.environ.get('secret_key', 'secret')
app = dash.Dash(name = __name__, server = server)
#app.config.supress_callback_exceptions = True

df = pd.read_csv('https://raw.githubusercontent.com/rahulpoddar/dash-deploy-exp/master/TASK1_annotated_1.csv', encoding='latin1')

tasks = df['Kaggle Task name'].unique().tolist()

def data_prep(inpt): 
    clean_data = []
    article3 = ' '.join(inpt)
    result=re.sub("\d+\.", " ", article3)
    clean_data.append(result)
            
    clean_data = pd.DataFrame(clean_data)
    clean_data.columns = ['Remediation']
    clean_data['Remediation'] = clean_data['Remediation'].astype('str')

    clean_data1 = clean_data['Remediation']
    clean_data2 = []
    regex = r"(?<!\d)[-,_;:()](?!\d)"
    for i in range(1):
        result2 = re.sub(regex,'',clean_data1.loc[i])
        clean_data2.append(result2)
    clean_data2 = pd.DataFrame(clean_data2)
    clean_data2.columns = ['Remediation']
    clean_data2['Remediation'] = clean_data2['Remediation'].astype('str')
    
    return (clean_data2)

def _create_dictionary_table(text_string) -> dict:
   
    # Removing stop words
    stop_words = set(stopwords.words("english"))
        
    words = word_tokenize(text_string)
    
    # Reducing words to their root form
    stem = PorterStemmer()
    
    # Creating dictionary for the word frequency table
    frequency_table = dict()
    for wd in words:
        wd = stem.stem(wd)
        if wd in stop_words:
            continue
        if wd in frequency_table:
            frequency_table[wd] += 1
        else:
            frequency_table[wd] = 1

    return frequency_table

def _calculate_sentence_scores(sentences, frequency_table) -> dict:   

    # Algorithm for scoring a sentence by its words
    sentence_weight = dict()

    for sentence in sentences:
        sentence_wordcount = (len(word_tokenize(sentence)))
        sentence_wordcount_without_stop_words = 0
        for word_weight in frequency_table:
            if word_weight in sentence.lower():
                sentence_wordcount_without_stop_words += 1
                if sentence[:7] in sentence_weight:
                    sentence_weight[sentence[:7]] += frequency_table[word_weight]
                else:
                    sentence_weight[sentence[:7]] = frequency_table[word_weight]

        sentence_weight[sentence[:7]] = sentence_weight[sentence[:7]] /        sentence_wordcount_without_stop_words
      
    return sentence_weight

def _calculate_average_score(sentence_weight) -> int:
   
    # Calculating the average score for the sentences
    sum_values = 0
    for entry in sentence_weight:
        sum_values += sentence_weight[entry]

    # Getting sentence average value from source text
    average_score = (sum_values / len(sentence_weight))

    return average_score

def _get_article_summary(sentences, sentence_weight, threshold):
    sentence_counter = 0
    article_summary = ''

    for sentence in sentences:
        if sentence[:7] in sentence_weight and sentence_weight[sentence[:7]] >= (threshold):
            article_summary += " " + sentence
            sentence_counter += 1

    return article_summary

def _run_article_summary(article):
    
    #creating a dictionary for the word frequency table
    frequency_table = _create_dictionary_table(article)

    #tokenizing the sentences
    sentences = sent_tokenize(article)

    #algorithm for scoring a sentence by its words
    sentence_scores = _calculate_sentence_scores(sentences, frequency_table)

    #getting the threshold
    threshold = _calculate_average_score(sentence_scores)

    #producing the summary
    article_summary = _get_article_summary(sentences, sentence_scores, 1 * threshold)

    return article_summary

def _output(inpt):
    new = []
    df = data_prep(inpt)
    df_rem = df['Remediation']
    #sentences = sent_tokenize(df_rem[0])
    summary_results = _run_article_summary(df_rem[0])
    new.append(summary_results)
    return(new)
'''
def generate_summary(task):
    return 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.'
'''
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
            ], id = 'sub-task-questions-main'),
    html.Div([html.H3('Response Summary'),
    html.Div(id = 'task-summary'),
    html.Div(id = 'search-summary')], id = 'task-summary-main'),
    
    html.Div([
            html.H3('Search Results'),
            html.Div(id = 'search-results'),
            html.Div(id = 'query-results')
            ], id = 'search-results-main')
])

@app.callback(
    dash.dependencies.Output('task-summary', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def update_summary(value):
    if value != None:
        dff = df[df['Kaggle Task name'] == value]
        return _output(dff['Output'].tolist())[0]    


@app.callback(
    dash.dependencies.Output('search-results', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def update_search_results(value):
    if value != None:
        dff = df[df['Kaggle Task name'] == value]
        return generate_table(dff)


@app.callback(
    dash.dependencies.Output('sub-task-questions', 'children'),
    [dash.dependencies.Input('task-dropdown', 'value')])
def sub_task_questions(value):
    if value != None:
        dff = df[df['Kaggle Task name'] == value]
        results = dff['Search'].unique().tolist()
        return html.P(results)
   
@app.callback(
        Output('query-results', 'children'),
         [Input('submit-button-state', 'n_clicks')],
         [State('general-search', 'value')]
         )
def populate_search_results(n_clicks, value):
    if value != '':
        query = value
        response = requests.post("https://nlp.biano-ai.com/develop/test", json={"texts": [query]})
        predictions = response.json()['predictions']
        pred_df = pd.DataFrame(predictions[0])
        pred_df.columns = ['Distance', 'Document id_', 'Output']
        return generate_table(pred_df)
    
@app.callback(
        Output('search-summary', 'children'),
         [Input('submit-button-state', 'n_clicks')],
         [State('general-search', 'value')]
         )
def generate_search_summary(n_clicks, value):
    if value != '':
        query = value
        response = requests.post("https://nlp.biano-ai.com/develop/test", json={"texts": [query]})
        predictions = response.json()['predictions']
        pred_df = pd.DataFrame(predictions[0])
        return _output(pred_df['text'].tolist())[0]

if __name__ == '__main__':
    app.run_server(debug=True)
