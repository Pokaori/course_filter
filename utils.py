from io import BytesIO
from PIL import ImageFilter, Image


def conv_pil_to_bytes(pil_image):
    img_io = BytesIO()
    pil_image.save(img_io, "PNG")
    img_io.seek(0)
    return img_io


def prepare_watermark(img_logo: Image):
    img_logo = img_logo.convert("L")
    threshold = 50
    img_logo = img_logo.point(lambda x: 255 if x > threshold else 0)
    img_logo = img_logo.resize((img_logo.width // 2, img_logo.height // 2))
    img_logo = img_logo.filter(ImageFilter.CONTOUR)
    return img_logo.point(lambda x: 0 if x == 255 else 255)


def merge_watermark(image, watermark):
    new_image = image.copy()
    new_image.paste(watermark, mask=watermark)
    new_data = new_image.getdata()
    old_data = image.getdata()
    data = []
    for index, value in enumerate(new_data):
        if value != old_data[index]:
            res = []
            for i, v in enumerate(value):
                res.append(30 + old_data[index][i])
            data.append(tuple(res))
        else:
            data.append(value)
    new_image.putdata(data)
    return new_image
