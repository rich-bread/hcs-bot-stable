from flask import Flask
from threading import Thread

app = Flask("HCS-BOT")

@app.route("/")
def main():
    message = "HCS-BOT起動中"
    return message

def run():
    app.run("0.0.0.0", port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()