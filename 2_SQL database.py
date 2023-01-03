import os
from collections import Counter
import sqlite3
from string import punctuation

class Topic:

    def __init__(self, name, words_to_filter, words=None, relative_weights=None):
        self.name = name
        """the topic name for the Topic object"""
        if words is None:
            self.words = []
        else:
            self.words = words
        """a list of all words in the topic"""
        self.words_to_filter = set(words_to_filter)
        """a set containing words to filter"""
        if relative_weights is None:
            self.relative_weights = {}
        else:
            self.relative_weights = dict(relative_weights)
        """a dictionary which holds the relative weight for each word within the topic"""

    def add_words(self, words):
        """add words to the object, take a list of strings as an argument"""
        words = self.words + list(words)
        filtered_words = [word for word in words if word not in self.words_to_filter]
        self.words.extend(filtered_words)
    
    def calculate_weights(self):
        """number_of_occurrences_of_word / total_number_of_words"""
        #word_count = {}
        word_count = Counter(self.words)
        for word in word_count:   
            relative_weights =  word_count[word] / len(self.words)
            self.relative_weights[word] = relative_weights
    
    def store_to_sql(self):
        """store the words weights to a SQLite database"""
        with sqlite3.connect("topics.db") as conn:
            cursor = conn.cursor()
            cursor.execute("""CREATE TABLE IF NOT EXISTS topics (topic text, word text, weight int)""")
            for word in self.relative_weights:
                cursor.execute("INSERT INTO topics (topic, word, weight) VALUES (?, ?, ?)", (self.name, word, self.relative_weights[word]))
            # for word in self.words:
            #     cursor.execute("INSERT INTO topics (topic, word, weight) VALUES (?, ?, ?)", (self.name, word, self.relative_weights[word]))
            conn.commit()
        conn.close()

"""a function that takes a file path as an argument"""
"""ruturn a list of all the words in that text"""
"""remove all punctuation and lowercase the words"""
def add_words_from_text(filepath):
    with open(filepath) as file_object:
        text = file_object.read()
    text = text.lower()
    for punc in punctuation:
        text = text.replace(punc, "")
    word_list = text.split()
    return word_list

if __name__ == "__main__":
#compile a list of words that occur in every topic (intersection between all word lists)
    Business_Words = []
    Entertainment_Words = []
    Politics_Words = []
    Sport_Words = []
    Tech_Words = []
    Common_Words = []
    for topic in os.scandir("bbc"):
        if topic.name == "business": 
            for file in os.scandir(topic.path):
                Business_Words += add_words_from_text(file.path)
            #print(Business_Words)
        if topic.name == "entertainment":
            for file in os.scandir(topic.path):
                Entertainment_Words += add_words_from_text(file.path)
            #print(Entertainment_Words)
        if topic.name == "politics":
            for file in os.scandir(topic.path):
                Politics_Words += add_words_from_text(file.path)
        if topic.name == "sport":
            for file in os.scandir(topic.path):
                Sport_Words += add_words_from_text(file.path)
        if topic.name == "tech":
            for file in os.scandir(topic.path):
                Tech_Words += add_words_from_text(file.path)
    Common_Words = [word for word in Business_Words if word in Entertainment_Words and word in Politics_Words and word in Sport_Words and word in Tech_Words]
    #print(Common_Words)
    
    #Build a topic object for each folder
    #store the word wegihts to a SQLite database
    words_to_filter = Common_Words
    for topic in os.scandir("bbc"):
        name = topic.name
        if name == "business":
            business = Topic(name, words_to_filter)
            business.add_words(Business_Words)
            #print(business.words[0:20])
            business.calculate_weights()
            # for word in business.words:
            #     print(business.relative_weights.keys())
            #print(business.relative_weights)
            business.store_to_sql()
            # with sqlite3.connect("topics.db") as conn:
            #     cursor = conn.cursor()
            #     cursor.execute("SELECT topic, word, weight FROM topics LIMIT 10")
            #     for row in cursor:
            #         print(row[1])
        if name == "entertainment":
            entertainment = Topic(name, words_to_filter)
            entertainment.add_words(Entertainment_Words)
            entertainment.calculate_weights()
            entertainment.store_to_sql()
        if name == "politics":
            politics = Topic(name, words_to_filter)
            politics.add_words(Politics_Words)
            politics.calculate_weights()
            politics.store_to_sql()
        if name == "sport":
            sport = Topic(name, words_to_filter)
            sport.add_words(Sport_Words)
            sport.calculate_weights()
            sport.store_to_sql()
        if name == "tech":
            tech = Topic(name, words_to_filter)
            tech.add_words(Tech_Words)
            tech.calculate_weights()
            tech.store_to_sql()
