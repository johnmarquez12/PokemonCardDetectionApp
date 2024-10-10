import cv2
import random
import numpy as np
from pathlib import Path
import os

def process_with_bounding_boxes(images_path: Path, bounding_boxes_path: Path, backgrounds_path: Path, output_path: Path, output_width=640, output_height=640):
    for image_path in images_path.iterdir():
        if image_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
            image_name = image_path.stem

            img = cv2.imread(str(image_path))

            bounding_box_file = bounding_boxes_path / f"{image_name}.txt"
            obb_points = read_obb_points(bounding_box_file)

            for background_path in backgrounds_path.iterdir():
                if background_path.suffix.lower() in ['.jpg', '.png', '.jpeg']:
                    background_img = cv2.imread(str(background_path))

                    superimposed_img, new_obb_points = superimpose_image(img, background_img, obb_points)
                    superimposed_img_scaled = scale_image(superimposed_img, (output_width, output_height))

                    new_filename = image_name + background_path.stem

                    print(f"Saving files into new name: {new_filename}")

                    save_all(new_filename, superimposed_img_scaled, new_obb_points, output_path) 

def process_without_bounding_boxes(images_path: Path, backgrounds_path: Path, output_path: Path, output_width=640, output_height=640):
    pass

def save_all(filename, image: cv2.typing.MatLike, points, output_path: Path):
    save_obb_points(points, filename, output_path / "labels", 0)
    save_image(image, filename, output_path / "images")

def apply_transformation(points, matrix):
    """Applies a transformation matrix to OBB points."""
    points = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    transformed_points = cv2.perspectiveTransform(points, matrix)
    return transformed_points.reshape(-1, 2).tolist()

def superimpose_image(image: cv2.typing.MatLike , background: cv2.typing.MatLike, obb_points):
    image_scaled = scale_image_to_background(image, background)

    img_h, img_w = image_scaled.shape[:2]
    bg_h, bg_w = background.shape[:2]

    obb_points_abs = [(x * img_w, y * img_h) for x, y in obb_points]
    
    scale_factor = random.uniform(0.25, 0.9)
    new_img_w = int(img_w * scale_factor)
    new_img_h = int(img_h * scale_factor)
    resized_image = cv2.resize(image, (new_img_w, new_img_h))

    x_offset = random.randint(0, bg_w - new_img_w)
    y_offset = random.randint(0, bg_h - new_img_h)
    background[y_offset:y_offset+new_img_h, x_offset:x_offset+new_img_w] = resized_image

    # Calculate the scaling matrix for the resize
    scaling_matrix = np.array([[scale_factor, 0, 0], 
                               [0, scale_factor, 0], 
                               [0, 0, 1]])
    
    transformed_obb_points = apply_transformation(obb_points_abs, scaling_matrix)

    # Translate the points by the offset where the image is placed on the background
    translated_obb_points = [(x + x_offset, y + y_offset) for x, y in transformed_obb_points]

    # Now normalize the OBB points relative to the background dimensions
    normalized_obb_points = [(x / bg_w, y / bg_h) for x, y in translated_obb_points]

    return background, normalized_obb_points

def scale_image(image: cv2.typing.MatLike, target_size=(640, 640)):    
    resized_image = cv2.resize(image, target_size)
    
    return resized_image

def scale_image_to_background(image: cv2.typing.MatLike, background: cv2.typing.MatLike) -> cv2.typing.MatLike:
    # Get dimensions of the original image and background
    img_h, img_w, _ = image.shape
    bg_h, bg_w, _ = background.shape

    bg_aspect_ratio = bg_w / bg_h

    # Scaling based on the aspect ratio of the background
    if bg_aspect_ratio > 1:
        # Background is wider than tall, scale by height
        scale_factor = bg_h / img_h
    else:
        # Background is taller than wide, scale by width
        scale_factor = bg_w / img_w

    # Calculate new image dimensions after scaling
    new_img_w = int(img_w * scale_factor)
    new_img_h = int(img_h * scale_factor)

    # Ensure the scaled image fits within the background bounds (just in case)
    if new_img_w > bg_w:
        new_img_w = bg_w
    if new_img_h > bg_h:
        new_img_h = bg_h

    # Resize the image
    resized_image = cv2.resize(image, (new_img_w, new_img_h))

    # Now the image fits within the background, return the resized image
    return resized_image

def read_obb_points(filepath: Path):
    with filepath.open('r') as file:
        lines = file.readlines()
        # Iterate over each line in the file
        for line in lines:
            # Split the line by spaces to extract the values
            values = line.strip().split()
            
            # Next 8 values are the coordinates (x1, y1, x2, y2, x3, y3, x4, y4)
            x1, y1 = float(values[1]) , float(values[2]) 
            x2, y2 = float(values[3]) , float(values[4]) 
            x3, y3 = float(values[5]) , float(values[6]) 
            x4, y4 = float(values[7]) , float(values[8]) 
            
            # Create an array of points (OpenCV expects the points in integer format)
            return [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]

def save_obb_points(obb_points, filename, output_dir: Path, class_index):
    output_file = output_dir / f"{filename}.txt"
    output_dir.mkdir(parents=True, exist_ok=True)

    with output_file.open('w') as file:
        
        (x1, y1), (x2, y2), (x3, y3), (x4, y4) = obb_points
        
        # Format the bounding box into the YOLO OBB format
        formatted_line = f"{class_index} {x1:.6f} {y1:.6f} {x2:.6f} {y2:.6f} {x3:.6f} {y3:.6f} {x4:.6f} {y4:.6f}\n"
        
        # Write the formatted line to the file
        file.write(formatted_line)

def save_image(image: cv2.typing.MatLike, filename, output_dir: Path):
    output_file = output_dir / f"{filename}.jpg"
    output_dir.mkdir(parents=True, exist_ok=True)

    success = cv2.imwrite(str(output_file), image)

    if success:
        print(f"Image saved successfully to {output_file}")
    else:
        print(f"Failed to save image: {output_file}")


# og_image = cv2.imread('/home/ajxz12/projects/pokemoncarddetection/data-pipeline/generated/images/SV05_EN_50_png.rf.4b3b041bd71800d81501489b95e5a477background.jpg')
# obb_points = read_obb_points('pokemoncardslabs.v1i.yolov8-obb/train/labels/slab1_webp.rf.7a205e379663f44c0de5afe1ee5793fd.txt')
# background = cv2.imread('background.jpeg')

# new_bg, points = superimpose_image(og_image, background, obb_points)
# new_bg = scale_image(new_bg)

new_bg = cv2.imread('generated/images/SV05_EN_50_png.rf.4b3b041bd71800d81501489b95e5a477background.jpg')
points = read_obb_points(Path('generated/labels/SV05_EN_50_png.rf.4b3b041bd71800d81501489b95e5a477background.txt'))
img_height, img_width = new_bg.shape[:2]

# Next 8 values are the coordinates (x1, y1, x2, y2, x3, y3, x4, y4)
x1, y1 = float(points[0][0]) * img_width, float(points[0][1]) * img_height
x2, y2 = float(points[1][0]) * img_width, float(points[1][1]) * img_height
x3, y3 = float(points[2][0]) * img_width, float(points[2][1]) * img_height
x4, y4 = float(points[3][0]) * img_width, float(points[3][1]) * img_height

# Create an array of points (OpenCV expects the points in integer format)
points = np.array([[x1, y1], [x2, y2], [x3, y3], [x4, y4]], np.int32)

# Reshape the points to the format required by OpenCV
points = points.reshape((-1, 1, 2))

# Draw the OBB (closed polygon) on the image (you can change the color and thickness)
cv2.polylines(new_bg, [points], isClosed=True, color=(0, 255, 0), thickness=2)

# Show the resulting image with the OBBs
cv2.imshow('Oriented Bounding Boxes', new_bg)
cv2.waitKey(0)
cv2.destroyAllWindows()



