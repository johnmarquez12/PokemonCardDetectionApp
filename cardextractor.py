import cv2
import numpy as np

class CardExtractor: 

    def extract_card(image, canny_threshold1=50, canny_threshold2=150, output_size=(240, 330), min_area=60000):

        width = output_size[0]
        height = output_size[1]

        kernel = np.ones((5,5), np.uint8)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (3, 3), 0)
        edges = cv2.Canny(blur, canny_threshold1, canny_threshold2)
        edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel=kernel)
        # edges = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # retval, edges = cv2.threshold(gray, thresh=100, maxval=255, type=cv2.THRESH_BINARY_INV)
        # Find contours and filter for cards using contour area
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # Find the largest contour, assuming it's the Pokémon card
            largest_contour = max(contours, key=cv2.contourArea)

            # Approximate the contour to a polygon (should be a quadrilateral)
            epsilon = 0.02 * cv2.arcLength(largest_contour, True)
            approx = cv2.approxPolyDP(largest_contour, epsilon, True)
            if cv2.contourArea(largest_contour) > min_area:
            # Check if the approximated contour has 4 points (i.e., it's a quadrilateral)
                if len(approx) == 4:
                    # print(largest_contour)

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
                    # Sort the points in clockwise order
                    # points = np.array(sorted(approx.reshape(4, 2), key=lambda x: x[0] + x[1]))

                    # # Define the destination points for the perspective transform
                    # (tl, tr, br, bl) = points
                    # dst = np.array([[0, 0], [output_size[0] - 1, 0], [output_size[0] - 1, output_size[1] - 1], [0, output_size[1] - 1]], dtype="float32")

                    # # Compute the perspective transform matrix and apply it
                    # M = cv2.getPerspectiveTransform(points.astype("float32"), dst)
                    # warped = cv2.warpPerspective(frame, M, output_size)

                    # return warped, edges

        # If no contours or no valid quadrilateral contour was found, return None
        return None, edges





