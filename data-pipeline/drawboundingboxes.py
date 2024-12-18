import cv2
import numpy as np
import argparse

def draw_obbs(image_path, annotation_file):
    # Load the image
    image = cv2.imread(image_path)

    img_height, img_width = image.shape[:2]

    with open(annotation_file, 'r') as file:
        lines = file.readlines()
        for line in lines:
            # Split the line by spaces to extract the values
            values = line.strip().split()
            
            # Next 8 values are the coordinates (x1, y1, x2, y2, x3, y3, x4, y4)
            x1, y1 = float(values[1]) * img_width, float(values[2]) * img_height
            x2, y2 = float(values[3]) * img_width, float(values[4]) * img_height
            x3, y3 = float(values[5]) * img_width, float(values[6]) * img_height
            x4, y4 = float(values[7]) * img_width, float(values[8]) * img_height
            
            points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)

            points = points.reshape((-1, 1, 2))

            cv2.polylines(image, [points], isClosed=True, color=(0, 255, 0), thickness=2)

    cv2.imshow('Oriented Bounding Boxes', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def main():
    parser = argparse.ArgumentParser(description="Draw bounding boxes for yolov8 OBB")

    parser.add_argument('--image', type=str, help='Path to image', required=True)
    parser.add_argument('--label', type=str, help='Path to Yolov8 OBB txt file.', required=True)

    args = parser.parse_args()
    draw_obbs(args.image, args.label)

if __name__ == "__main__":
    main()
