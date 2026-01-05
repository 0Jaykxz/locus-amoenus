from flask import Flask
from config import configure_all
import webbrowser, sys, os, threading, re 

opened = False

def open_browser():
    global opened
    if not opened:
        opened = True
        webbrowser.open("http://127.0.0.1:5000")

def resource_path(path):
    try:
        base = sys._MEIPASS
    except Exception:
        base = os.path.abspath(".")
    return os.path.join(base, path)

app = Flask(__name__, template_folder=resource_path("templates"),
    static_folder=resource_path("static"))

configure_all(app)

threading.Timer(1, open_browser).start()
app.run(debug=True, port=5000) #Mudar o debug para True no modo de desenvolvimento