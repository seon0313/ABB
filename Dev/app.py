from flask import Flask, render_template, send_file


app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')

@app.route('/cam')
def cam():
    return render_template('cam.html')
@app.route('/control')
def control():
    return render_template('control.html')
@app.route('/image')
def image():
    return render_template('image.html')

@app.route('/file/<path:path>')
def file(path: str):
    return send_file(f'./files/{path}')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9181, debug=True)