import base64
import numpy as np
import cv2


def opencv_to_base64(img, ext):
    _, im_arr = cv2.imencode('.' + ext, img)  # Numpy one-dim array representative of the img
    im_bytes = im_arr.tobytes()
    im_b64 = base64.b64encode(im_bytes)
    return im_b64


def base64_to_opencv(im_b64):
    im_bytes = base64.b64decode(im_b64)
    im_arr = np.frombuffer(im_bytes, dtype=np.uint8)  # Numpy one-dim array representative of the img
    img = cv2.imdecode(im_arr, flags=cv2.IMREAD_COLOR)
    return img
