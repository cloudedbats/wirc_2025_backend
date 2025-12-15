from picamera2 import Picamera2
import cv2
import numpy
import pathlib
import PIL
import io

# picam2_a = Picamera2(0)
picam2_b = Picamera2(1)

config_b = picam2_b.create_video_configuration(main={'format': 'YUYV', 'size': (256, 192)})
picam2_b.configure(config_b)
picam2_b.start()

dir_path = pathlib.Path("/home/wurb/TEST")
if not dir_path.exists():
    dir_path.mkdir()

counter = 0
while counter <= 200:
    image_array = picam2_b.capture_array("main")
    image_array = image_array[:,:,0]
    # image_array = image_array[:,:,1]
    image_array = cv2.normalize(image_array, None, 0, 255, cv2.NORM_MINMAX)
    # image_array = image_array.transpose()
    # image_array = cv2.flip(image_array, 1)
    # image_array = cv2.rotate(image_array, cv2.ROTATE_90_CLOCKWISE)
    # image_array = cv2.rotate(image_array, cv2.ROTATE_90_COUNTERCLOCKWISE)

    image_array = cv2.applyColorMap(image_array, cv2.COLORMAP_INFERNO)
    file_path = pathlib.Path(dir_path, "thermal_" + str(counter) + ".png")
    cv2.imwrite(str(file_path), image_array)

    # test_jpeg = cv2.imencode('.jpg', image_array)
    # print(test_jpeg)

    jpg = PIL.Image.fromarray(image_array)
    tmpFile = io.BytesIO()
    jpg.save(tmpFile,'JPEG')

    print(str(len(tmpFile.getvalue())))

    print("Counter: ", counter)
    counter += 1


# picam2_a.stop()
picam2_b.stop()
