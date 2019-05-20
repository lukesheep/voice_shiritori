
import sqlite3
from pykakasi import kakasi, wakati

# open connection with the db, the cursor object, getting the needed data to
# create my dictionary table
conn = sqlite3.connect("wnjpn.db")
cursor = conn.cursor()
kanjiword = cursor.execute("select lemma from word where lang='jpn' and pos='n' ").fetchall()
kanji_list = list(kanjiword)
initial = list()
ending = list()
reading = list()
adjusted_kanji = list()

# setting up the kakasi lybrary to convert every word to hiragana
kakasi = kakasi()
kakasi.setMode("H", None)
kakasi.setMode("K", "H")
kakasi.setMode("J", "H")
kakasi.setMode("s", False)
kakasi.setMode("C", True)
kakasi.setMode("E", None)
kakasi.setMode("a", None)
converter = kakasi.getConverter()

# converting everyword and preparing the lists of Data
for x in kanji_list:
    text = str(x)
    adjusted = text[2:-3]  # the ("word") is like that, so getting rid it
    adjusted_kanji.append(adjusted)
    furigana = converter.do(adjusted)
    reading.append(furigana)
    initial.append(furigana[0])
    ending.append(furigana[-1])

# creating the table using parameter for safety and inputing the data
cursor.execute("DROP TABLE shiritori_dict")

createDict = """CREATE TABLE IF NOT EXISTS shiritori_dict (
 id integer PRIMARY KEY,
 kanji text NOT NULL,
 reading text NOT NULL,
 first text,
 last text,
 type text
);"""
cursor.execute(createDict)

for y in range(1, len(adjusted_kanji)):
    insert = """ INSERT INTO shiritori_dict(id,kanji,reading,first,last)
    VALUES (?,?,?,?,?) """
    values = (y, adjusted_kanji[y], reading[y], initial[y], ending[y])
    cursor.execute(insert, values)
conn.commit()
cursor.close()
