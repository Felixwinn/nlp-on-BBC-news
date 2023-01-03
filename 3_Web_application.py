from flask import Flask, render_template, request
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import sqlite3
from string import punctuation
from collections import Counter
import plotly
import plotly.express as px
import pandas as pd
import json

##Third task: the Web application
app = Flask(__name__)
SEARCH_INDEX = open_dir("index_directory")
QUERY_PARSER = QueryParser("content", SEARCH_INDEX.schema)

#display the search form in the browser to search in the Whoosh index
@app.route("/")
def home():
    """Home page"""
    topic_name = []
    for topic in os.scandir("bbc"):
        if topic.name !=".DS_Store":
            topic_name.append(topic.name)
    top10 = {}
    top10_business = []
    top10_entertainment = []
    top10_politics = []
    top10_sport = []
    top10_tech = []
    with sqlite3.connect("topics.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic='business' ORDER BY weight DESC LIMIT 10")
        for topic, word, weight in cursor:
            top10_business.append(word)
            top10[topic] = top10_business
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic='entertainment' ORDER BY weight DESC LIMIT 10")
        for topic, word, weight in cursor:
            top10_entertainment.append(word)
            top10[topic] = top10_entertainment
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic='politics' ORDER BY weight DESC LIMIT 10")
        for topic, word, weight in cursor:
            top10_politics.append(word)
            top10[topic] = top10_politics
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic='sport' ORDER BY weight DESC LIMIT 10")
        for topic, word, weight in cursor:
            top10_sport.append(word)
            top10[topic] = top10_sport
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic='tech' ORDER BY weight DESC LIMIT 10")
        for topic, word, weight in cursor:
            top10_tech.append(word)
            top10[topic] = top10_tech
    conn.close()
    return render_template("home_search.html", topic_name=topic_name, top10=top10)

@app.route("/search", methods=["GET"])
def search():
    """Search words"""
    query = request.args["query"]
    with SEARCH_INDEX.searcher() as searcher:
        parsed_query = QUERY_PARSER.parse(query)
        results = searcher.search(parsed_query, limit=100)
        total = len(results)
        return render_template("results.html", results=results, total=total, query=query)

@app.route("/text/<topic>/<filename>")
def get_text(topic, filename):
    """Return full text of file"""
    full_path = f"bbc/{topic}/{filename}"
    with open(full_path) as input_file:
        text = input_file.read()
    text1 = text.lower()
    for punc in punctuation:
        text1 = text1.replace(punc, "")
    word_list = text1.split()
    stopwords = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what", "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "would", "could", "upon", "might", "hamilton", "jay", "madison"]
    filtered_wordlist = [word for word in word_list if word not in stopwords]
    top10_word = Counter(filtered_wordlist).most_common(10)
    list1 = []
    for list in top10_word:
        list1.append(list[0])
    return render_template("text.html", text=text, list1=list1)

@app.route("/topic/<topic>")
def topic(topic):
    top20 = []
    with sqlite3.connect("topics.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT topic, word, weight FROM topics WHERE topic=? ORDER BY weight DESC LIMIT 20", [topic])
        for topic, word, weight in cursor:
            word_weight = (word, weight)
            top20.append(word_weight)
    conn.close()
    df = pd.DataFrame(top20, columns = ['Word', 'Weight'])
    df.set_index("Word", inplace=True)
    fig = px.histogram(df, title=f"Word weights for {topic}")
    fig.update_layout(xaxis_title = "Word Weights")
    fig.update_layout(yaxis_title = "Word Weights Frequency")
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    #fig.show()
    return render_template("histogram.html", plot_json=plot_json)
#use px.bar can show the graph with x-axis is each of the top 20 words and y-axis is word weights for each word

#try to create a data series
# top20 = {}
#     with sqlite3.connect("topics.db") as conn:
#         cursor = conn.cursor()
#         cursor.execute("SELECT topic, word, weight FROM topics WHERE topic=? ORDER BY weight DESC LIMIT 20", [topic])
#         for topic, word, weight in cursor:
#             top20[word] = weight
#     df = pd.DataFrame(top20.values(), index=top20.keys())
#     fig = px.histogram(df, title=f"Word weights for {topic}")
#     fig.update_layout(xaxis_title = "top")
#     plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
#     #fig.show()
#     return render_template("histogram.html", plot_json=plot_json)

#debug:        
#export FLASK_ENV=development

