import cv2
from flask import Flask, request, jsonify, send_file
from flask_swagger import swagger
from flask_restx import Resource, Api 

app = Flask(__name__)
api = Api(app)
clip_hist_percent = 1

@api.route('/api/hello')
class Greeting(Resource):
    def get(self):
        '''say hello'''
        return 'Hello world'

# Automatic brightness and contrast optimization with optional histogram clipping
@api.route('/api/agjust')
class AutoAdjust(Resource):
    @api.res  .response(201, 'Blog post successfully created.')
    def post(self):
        '''Automatic adjust brightness and contrast'''
        image = request.files[0]
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
        return send_file(auto_result, mimetype='image/jpg'), 200
        #(auto_result, alpha, beta),

if __name__ == '__main__':
    app.run(debug=True)

#img = cv2.imread("C:\\Users\\John\\Downloads\\doc.jpeg")
# auto_result, alpha, beta = automatic_brightness_and_contrast(img)
# print('alpha', alpha)
# print('beta', beta)
# cv2.imshow('auto_result', auto_result)
# cv2.waitKey()
#cv2.imwrite("C:\\Users\\John\\Downloads\\processed.jpeg", img)