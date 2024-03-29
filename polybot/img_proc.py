from pathlib import Path
from matplotlib.image import imread, imsave
import random


def rgb2gray(rgb):
    r, g, b = rgb[:, :, 0], rgb[:, :, 1], rgb[:, :, 2]
    gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    return gray


class Img:

    def __init__(self, path):
        """
        Do not change the constructor implementation
        """
        self.path = Path(path)
        self.data = rgb2gray(imread(path)).tolist()

    def save_img(self):
        """
        Do not change the below implementation
        """
        new_path = self.path.with_name(self.path.stem + '_filtered' + self.path.suffix)
        imsave(new_path, self.data, cmap='gray')
        return new_path

    def blur(self, blur_level=16):

        height = len(self.data)
        width = len(self.data[0])
        filter_sum = blur_level ** 2

        result = []
        for i in range(height - blur_level + 1):
            row_result = []
            for j in range(width - blur_level + 1):
                sub_matrix = [row[j:j + blur_level] for row in self.data[i:i + blur_level]]
                average = sum(sum(sub_row) for sub_row in sub_matrix) // filter_sum
                row_result.append(average)
            result.append(row_result)

        self.data = result

    def contour(self):
        for i, row in enumerate(self.data):
            res = []
            for j in range(1, len(row)):
                res.append(abs(row[j-1] - row[j]))

            self.data[i] = res

    def rotate(self):
        # explanation: each row would become a column. (last row -> first column)
        # so I iterate over the rows (reversed, starting from the last one),
        # and I take always the first element of the row, push it into my new row.
        # this way my row becomes my column ....

        res = []
        for i in range(len(self.data[0])):
            rotated_row = []
            for sublist in reversed(self.data): # iterating over the rows backwards
                if sublist:
                    rotated_row.append(sublist[0]) # takes the first element of each row
                    del sublist[0]

            res.append(rotated_row)
        self.data = res

    def salt_n_pepper(self):
        # the approach : randomly change pixels into 0 or 255 .
        # we need to decide the noise_amount we want to add .
        noise_amount = 0.2
        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                rnd = random.random()
                if rnd < noise_amount:
                    self.data[i][j] = 0 # black noise
                elif rnd > 1 - noise_amount:
                    self.data[i][j] = 255 # white noise
                else:
                    pass # no noise, keep going

    def concat(self, other_img, direction='horizontal'):
        # explaining the approach
        # if the direction is horizontal as given then I need to make sure the 2 images has the same row numbers .
        # otherwise I'll need to adjust the dimensions by adding 0 or 255 rows to the image with fewer rows.
        matrix1 = self.data
        matrix2 = other_img.data
        num_rows_matrix1 = len(matrix1)
        num_rows_matrix2 = len(matrix2)
        if num_rows_matrix1 == num_rows_matrix2:
            for i in range(len(matrix1)):
                matrix1[i].extend(matrix2[i]) # Concatenate rows horizontally
            self.data = matrix1
        else:
            raise RuntimeError("can not concatenate images of different dimensions")


    def segment(self):

        for i in range(len(self.data)):
            for j in range(len(self.data[i])):
                if self.data[i][j] > 100:
                    self.data[i][j] = 255
                else:
                    self.data[i][j] = 0
