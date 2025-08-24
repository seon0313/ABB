from flask import Flask, render_template
import time
from gpiozero import Motor

app = Flask(__name__)

front = False
left = False
right = False
bottom = False

@app.route('/')
def main():
    return render_template('main.html')

def move():
    top_left = Motor(14,15,enable=18)
    bottom_left = Motor(23,24,enable=25)

    while True:
        top_left.forward(0.5)
        bottom_left.forward(0.5)


if __name__ == '__main__':
    import threading
    th = threading.Thread(target=move,daemon=True)
    th.start()
    app.run('0.0.0.0', 8181, True)