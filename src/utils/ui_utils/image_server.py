from flask import Flask,request,jsonify
from flask_cors import CORS

def start_server(color_string):

    app = Flask(__name__)
    CORS(app)

    @app.route('/get-color-string', methods=['GET'])
    def get_color_string():
        return color_string

    @app.route('/set-color-string', methods=['POST'])
    def set_color_string():
        print(request.data)
        return jsonify(image='bla',color_string=request.data.decode("utf-8"))

    app.run(debug=True,use_reloader=False)