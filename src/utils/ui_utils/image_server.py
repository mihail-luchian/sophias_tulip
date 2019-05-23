from flask import Flask,request,jsonify
from flask_cors import CORS,cross_origin
import cv2
import base64

def start_server(color_string,generate_image_function):

    app = Flask(__name__)
    CORS(app)

    def get_image(color_string):
        img = generate_image_function(color_string)
        img[img>255] = 255
        img[img<0] = 0
        img = img.astype('uint8')
        _,img_bytes = cv2.imencode('.png', cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
        img_base64 = str(base64.b64encode(img_bytes),'utf-8')
        return img_base64

    @app.route('/get-color-string', methods=['GET'])
    @cross_origin()
    def get_color_string():
        return jsonify({
            'color-string':color_string,
            'image':get_image(color_string)
        })

    @app.route('/set-color-string', methods=['POST'])
    @cross_origin()
    def set_color_string():
        color_string = request.get_data().decode("utf-8")
        print('RECEIVED COLOR STRING:')
        print(color_string)
        return jsonify({
            'color-string':color_string,
            'image':get_image(color_string)
        })

    app.run(debug=True,use_reloader=False)