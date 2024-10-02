import cv2
import numpy as np
from typing import Tuple

class CardExtractor: 
    
    def __init__(self) -> None:
        pass

    def preprocess_image(self, image, canny_threshold1=50, canny_threshold2=150) -> cv2.typing.MatLike:
        kernel = np.ones((5,5), np.uint8)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        bilateral_filter = cv2.bilateralFilter(gray, 15, 75, 75)
        # otsu_thresh, _ = cv2.threshold(bilateral_filter, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        th = cv2.adaptiveThreshold(bilateral_filter, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 25, 5)

        # lower_thresh = int(otsu_thresh * 0.2)
        # upper_thresh = int(otsu_thresh * 0.5)

        edges = cv2.Canny(th, canny_threshold1, canny_threshold2)

        # frameDial = cv2.dilate(edges, kernel, iterations=2)
        # frameThreshold = cv2.erode(frameDial, kernel, iterations=1)
        
        # edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel=kernel)

        return edges


    def extract_card(self, image, canny_threshold1=50, canny_threshold2=150, output_size=(240, 330), min_area=70000) -> Tuple[cv2.typing.MatLike, cv2.typing.MatLike]:

        width = output_size[0]
        height = output_size[1]
        
        # edges = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # retval, edges = cv2.threshold(gray, thresh=100, maxval=255, type=cv2.THRESH_BINARY_INV)
        # Find contours and filter for cards using contour area

        edges = self.preprocess_image(image)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour, assuming it's the Pokémon card
            largest_contour = max(contours, key=cv2.contourArea)    
            hull = cv2.convexHull(largest_contour)

            # Approximate the contour to a polygon (should be a quadrilateral)
            epsilon = 0.02 * cv2.arcLength(hull, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)

            if cv2.contourArea(largest_contour) > min_area:
            # Check if the approximated contour has 4 points (i.e., it's a quadrilateral)
                if len(approx) == 4 and self.contour_matches_aspect_ratio(largest_contour):
                    points = []

                    for point in approx:
                        x, y = point[0]
                        points.append([x, y])

                    card = np.float32(points)
                    x1, y1 = points[0]
                    x2, y2 = points[1]
                    x3, y3 = points[2]
                    x4, y4 = points[3]

                    # distance formula
                    # sqrt( (x2-x1)^2 + (y2-y1)^2 )
                    # This should make it so if it's cocked it still gets put into up, down regardless if it's cocked
                    # left or cocked right
                    if np.sqrt(np.square(x1 - x2) + np.square(y1 - y2)) < np.sqrt(np.square(x1 - x4) + np.square(y1 - y4)):
                        # top point goes to top right
                        cardWarped = np.float32([[width, 0], [0, 0], [0, height], [width, height]])
                    else:
                        # top point goes to top left
                        cardWarped = np.float32([[0, 0], [0, height], [width, height], [width, 0]])

                    matrix = cv2.getPerspectiveTransform(card, cardWarped)
                    imgOutput = cv2.warpPerspective(image, matrix, (width, height))
                    return imgOutput, edges

        # If no contours or no valid quadrilateral contour was found, return None
        return None, edges

    def contour_matches_aspect_ratio(self, contour, dimensions=(3.5, 2.5), tolerance=0.1) -> bool:
        expected_aspect_ratio = dimensions[0] / dimensions[1]

        (x, y, w, h) = cv2.boundingRect(contour)

        aspect_ratio = float(w) / h if w > h else float(h) / w

        return (expected_aspect_ratio - tolerance) <= aspect_ratio <= (expected_aspect_ratio + tolerance)





