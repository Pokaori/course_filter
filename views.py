from flask import request, send_file
from flask_restx import Resource, Namespace
from PIL import Image, ImageFilter
from io import BytesIO
from flask_restx.reqparse import FileStorage
from utils import conv_pil_to_bytes, prepare_watermark, merge_watermark

ns = Namespace("images", description="images operations")

parser = ns.parser()
parser.add_argument('image', type=FileStorage, location='files', required=True)

watermark_parser = ns.parser()
watermark_parser.add_argument('image', type=FileStorage, location='files', required=True)
watermark_parser.add_argument('watermark', type=FileStorage, location='files', required=True)


@ns.route('/sharp', endpoint='sharp-image')
class ImageSharp(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.SHARPEN)
        return send_file(conv_pil_to_bytes(img), mimetype="image/*")


@ns.route('/smooth', endpoint='smooth-image')
class ImageSmooth(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.SMOOTH)
        return send_file(conv_pil_to_bytes(img), mimetype="image/*")


@ns.route('/gray', endpoint='gray-image')
class ImageGray(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.convert("L")
        return send_file(conv_pil_to_bytes(img), mimetype="image/*")


@ns.route('/find_edges', endpoint='find-edges')
class ImageFindEdges(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.convert("L").filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES)
        return send_file(conv_pil_to_bytes(img), mimetype="image/*")


@ns.route('/red', endpoint='red-image')
class ImageRed(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue, _ = img.split()
        zeroed_band = red.point(lambda _: 0)
        red_merge = Image.merge("RGB", (red, zeroed_band, zeroed_band))
        return send_file(conv_pil_to_bytes(red_merge), mimetype="image/*")


@ns.route('/blue', endpoint='blue-image')
class ImageBlue(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue, _ = img.split()
        zeroed_band = red.point(lambda _: 0)
        blue_merge = Image.merge("RGB", (zeroed_band, zeroed_band, blue))
        return send_file(conv_pil_to_bytes(blue_merge), mimetype="image/*")


@ns.route('/green', endpoint='green-image')
class ImageGreen(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue, _ = img.split()
        zeroed_band = red.point(lambda _: 0)
        green_merge = Image.merge("RGB", (zeroed_band, green, zeroed_band))
        return send_file(conv_pil_to_bytes(green_merge), mimetype="image/*")


@ns.route('/watermark', endpoint='watermark')
class ImageWatermark(Resource):
    @ns.expect(watermark_parser)
    def post(self):
        watermark = Image.open(BytesIO(request.files['watermark'].read()))
        watermark = prepare_watermark(watermark)
        img = Image.open(BytesIO(request.files['image'].read()))
        return send_file(conv_pil_to_bytes(merge_watermark(img, watermark)), mimetype="image/*")


@ns.route('/blur', endpoint='blur-image')
class ImageBlur(Resource):
    @ns.expect(parser)
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.GaussianBlur)
        return send_file(conv_pil_to_bytes(img), mimetype="image/*")
