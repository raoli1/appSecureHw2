from flask import Flask
from flask import render_template
from flask import request
import string
import inflect
import pyodbc
import json
app = Flask(__name__)

def connectToDatabase():
    server = 'raoliserver.database.windows.net'
    database = 'English_word_list'
    username = 'raoli'
    password = 'Wmcy941013'
    driver= '{ODBC Driver 17 for SQL Server}'
    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
    return cnxn

def prepareWordDictionary():
    dict = {}
    cnxn = connectToDatabase()
    cursor = cnxn.cursor()
    cursor.execute("SELECT DISTINCT word FROM wordList")
    row = cursor.fetchone()
    while row:
        dict[str(row[0]).strip()] = True
        row = cursor.fetchone()
    return dict

def helpSpellCheck(text):
    dictWrong = {}
    outputString = ''
    inflectEng = inflect.engine()
    dict = prepareWordDictionary()
    allCorrect = True
    words = str(text).split()
    for rawWord in words:
        rawWord = rawWord.strip(string.punctuation+' ')
        word = rawWord.lower()
        wordTemp = word 
        inflectEng.singular_noun(wordTemp)
        if word and not word.isdigit() and not dict.get(word) and  not dict.get(wordTemp):
            allCorrect = False
            dictWrong[rawWord] = True
    if allCorrect == True:
        return "All of your spellings are correct."
    for wrongWord in dictWrong:
        outputString += "<br>The word \'%s\' is not in our dictionary.</br>"%(wrongWord)
    return outputString

@app.route("/")
def welcome():
    return render_template('homepage.html')
        
@app.route("/", methods=['POST'])
def spellCheck():
    text = request.get_data(as_text=True)
    if text.isspace() or len(text)==0:
        return json.dumps("Text Box cannot be Empty.")
    response = helpSpellCheck(text)
    return json.dumps(response)
        
        


