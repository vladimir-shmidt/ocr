import cv2
from flask import Flask, request, jsonify, send_file
from flask_restx import Resource, Api, reqparse
from werkzeug.datastructures import FileStorage
import numpy
import io

app = Flask(__name__)
api = Api(app)

upload_parser = api.parser()
upload_parser.add_argument('file', location='files', type=FileStorage, required=True)

@api.route('/api/hello')
class Greeting(Resource):
    def get(self):
        '''say hello'''
        return 'Hello world'

# Automatic brightness and contrast optimization with optional histogram clipping
@api.route('/api/agjust')
@api.expect(upload_parser)
@api.response(200, description='return adjusted image')
@api.produces(['image/jpeg'])
class AutoAdjust(Resource):
    def post(self):
        '''Automatic adjust brightness and contrast'''
        clip_hist_percent = 1
        if not request.files:
            return 'file was not specified', 422
        f = request.files['file']
        npimg = numpy.fromfile(f, numpy.uint8)
        image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Calculate grayscale histogram
        hist = cv2.calcHist([gray],[0],None,[256],[0,256])
        hist_size = len(hist)

        # Calculate cumulative distribution from the histogram
        accumulator = []
        accumulator.append(float(hist[0]))
        for index in range(1, hist_size):
            accumulator.append(accumulator[index -1] + float(hist[index]))

        # Locate points to clip
        maximum = accumulator[-1]
        clip_hist_percent *= (maximum/100.0)
        clip_hist_percent /= 2.0

        # Locate left cut
        minimum_gray = 0
        while accumulator[minimum_gray] < clip_hist_percent:
            minimum_gray += 1

        # Locate right cut
        maximum_gray = hist_size -1
        while accumulator[maximum_gray] >= (maximum - clip_hist_percent):
            maximum_gray -= 1

        # Calculate alpha and beta values
        alpha = 255 / (maximum_gray - minimum_gray)
        beta = -minimum_gray * alpha

        auto_result = cv2.convertScaleAbs(image, alpha=alpha, beta=beta)
        
        _, buf = cv2.imencode('.jpeg', auto_result)
        return send_file(io.BytesIO(buf.tobytes()), mimetype='image/jpeg')

if __name__ == '__main__':
    app.run(debug=True, host=0.0.0.0)