from flask import Flask,request,jsonify
from flask_cors import CORS,cross_origin
import cv2
import base64

def start_server(color_string,generate_image_function):

    app = Flask(__name__)
    CORS(app)

    def prepare_image(color_string):

        print('GENERATING IMAGE')

        img = generate_image_function(color_string)
        img[img>255] = 255
        img[img<0] = 0
        img = img.astype('uint8')
        _,img_bytes = cv2.imencode('.png', cv2.cvtColor(img,cv2.COLOR_RGB2BGR))
        img_base64 = str(base64.b64encode(img_bytes),'utf-8')

        print('GENERATION DONE')

        return img_base64

    @app.route('/get-color-string', methods=['GET'])
    @cross_origin()
    def get_color_string():
        return jsonify({
            'color-string':color_string,
            'image':prepare_image(color_string)
        })

    @app.route('/set-color-string', methods=['POST'])
    @cross_origin()
    def set_color_string():
        color_string = request.get_data().decode("utf-8")
        print('RECEIVED COLOR STRING:')
        print('\n')
        print(color_string)
        print('\n')

        img = prepare_image(color_string)

        return jsonify({
                    'color-string':color_string,
                    'image': img
                })

    app.run(debug=True,use_reloader=False)