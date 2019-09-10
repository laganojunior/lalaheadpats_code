from PIL import Image
import numpy as np
import math

w = 1024
h = 1024

image_data = np.zeros((h, w, 3), dtype=np.uint8)

for i in range(h):
    y =  1.0 - (i + 1) / h

    for j in range(w):
        x = j / w

        expected_tickets_first_round = 20 + 180 * x ** 2 + 200 * x ** 6
        expected_tickets_final_round = 20 * x + 180 * x ** 3 + 200 * x ** 6 + 20 * y + 180 * y ** 3

        if y >= x:
            pixel = [255, 255, 255]
        else:
            if expected_tickets_final_round > expected_tickets_first_round:
                pixel = [132, 186, 91]
            else:
                pixel = [211, 94, 96]

        if (abs(x - round(x, 1)) < 0.001) or (abs(y - round(y, 1)) < 0.001):
            pixel = [125, 125, 125]

        image_data[i, j] = pixel

image = Image.fromarray(image_data, 'RGB')
image.save('graph1.png')
