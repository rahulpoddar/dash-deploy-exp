from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import pandas as pd
import re
import string
from nltk.tokenize import word_tokenize, sent_tokenize

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
    
