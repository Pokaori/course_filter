from uuid import uuid4

from flask import request, send_file, jsonify
from flask_restx import Resource, Namespace
from PIL import Image, ImageFilter
from io import BytesIO
from flask_restx.reqparse import FileStorage

from utils import conv_pil_to_bytes, prepare_watermark, merge_watermark, add_cors

ns = Namespace("images", description="images operations")

parser = ns.parser()
parser.add_argument('image', type=FileStorage, location='files', required=True)

watermark_parser = ns.parser()
watermark_parser.add_argument('image', type=FileStorage, location='files', required=True)
watermark_parser.add_argument('watermark', type=FileStorage, location='files', required=True)

HOST = "http://127.0.0.1:5000"


def save_image(img: BytesIO) -> str:
    image_id = uuid4()
    with open(f"images/{image_id}.png", "wb") as f:
        f.write(img.getbuffer())
    return HOST + f"/images/{image_id}"


@ns.route('/sharp', endpoint='sharp-image')
class ImageSharp(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.SHARPEN)
        image_link = save_image(conv_pil_to_bytes(img))
        return jsonify({"link": image_link})


@ns.route('/smooth', endpoint='smooth-image')
class ImageSmooth(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.SMOOTH)
        image_link = save_image(conv_pil_to_bytes(img))
        return jsonify({"link": image_link})


@ns.route('/gray', endpoint='gray-image')
class ImageGray(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.convert("L")
        image_link = save_image(conv_pil_to_bytes(img))
        return jsonify({"link": image_link})


@ns.route('/find_edges', endpoint='find-edges')
class ImageFindEdges(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.convert("L").filter(ImageFilter.SMOOTH).filter(ImageFilter.FIND_EDGES)
        image_link = save_image(conv_pil_to_bytes(img))
        return jsonify({"link": image_link})


@ns.route('/red', endpoint='red-image')
class ImageRed(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue = img.split()
        zeroed_band = red.point(lambda _: 0)
        red_merge = Image.merge("RGB", (red, zeroed_band, zeroed_band))
        image_link = save_image(conv_pil_to_bytes(red_merge))
        return jsonify({"link": image_link})


@ns.route('/blue', endpoint='blue-image')
class ImageBlue(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue = img.split()
        zeroed_band = red.point(lambda _: 0)
        blue_merge = Image.merge("RGB", (zeroed_band, zeroed_band, blue))
        image_link = save_image(conv_pil_to_bytes(blue_merge))
        return jsonify({"link": image_link})


@ns.route('/green', endpoint='green-image')
class ImageGreen(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        red, green, blue = img.split()
        zeroed_band = red.point(lambda _: 0)
        green_merge = Image.merge("RGB", (zeroed_band, green, zeroed_band))
        image_link = save_image(conv_pil_to_bytes(green_merge))
        return jsonify({"link": image_link})


@ns.route('/watermark', endpoint='watermark')
class ImageWatermark(Resource):
    @ns.expect(watermark_parser)
    @add_cors
    def post(self):
        watermark = Image.open(BytesIO(request.files['watermark'].read()))
        watermark = prepare_watermark(watermark)
        img = Image.open(BytesIO(request.files['image'].read()))
        image_link = save_image(conv_pil_to_bytes(merge_watermark(img, watermark)))
        return jsonify({"link": image_link})


@ns.route('/blur', endpoint='blur-image')
class ImageBlur(Resource):
    @ns.expect(parser)
    @add_cors
    def post(self):
        img = Image.open(BytesIO(request.files['image'].read()))
        img = img.filter(ImageFilter.GaussianBlur)
        image_link = save_image(conv_pil_to_bytes(img))
        return jsonify({"link": image_link})


@ns.route('/<image_id>', endpoint='image-result')
class ImageResponse(Resource):

    def get(self, image_id):
        with open(f"images/{image_id}.png", "rb") as f:
            bytes = BytesIO(f.read())
        return send_file(bytes, mimetype="image/*")