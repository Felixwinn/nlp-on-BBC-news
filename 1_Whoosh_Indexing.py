import os
from shutil import rmtree
from whoosh import index
from whoosh.fields import Schema, TEXT
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

if __name__ == "__main__":
    schema = Schema(file=TEXT(stored=True), topic=TEXT(stored=True), title=TEXT(stored=True), content=TEXT(stored=True))
    if os.path.exists("index_directory"):
        rmtree("index_directory")
    os.mkdir("index_directory")
    index_object = index.create_in("index_directory", schema)
    index_writer = index_object.writer()
    for topic in os.scandir("bbc"):
        if topic.name ==".DS_Store": #metadata if you're on a Mac
            continue
        for file in os.scandir(topic.path):
            print(f"Parsing file {file.name} from {topic.name}...")
            with open(file) as input_file:
                title = input_file.readline().strip()
                content = input_file.read()
            index_writer.add_document(file=file.name, topic=topic.name, title=title, content=content)
    index_writer.commit()