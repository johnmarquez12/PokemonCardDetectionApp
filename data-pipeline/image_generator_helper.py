import cv2
import random
import numpy as np
from pathlib import Path
from readwritehelpers import save_all, read_obb_points
import cvzone

def process_with_bounding_boxes(images_path: Path, bounding_boxes_path: Path, backgrounds_path: Path, output_path: Path, output_width=640, output_height=640):
    for image_path in images_path.iterdir():
        if image_path.suffix.lower() in ['.jpg', '.png', '.jpeg', '.webp']:
            image_name = image_path.stem

            img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)

            bounding_box_file = bounding_boxes_path / f"{image_name}.txt"
            obb_points = read_obb_points(bounding_box_file)

            for background_path in backgrounds_path.iterdir():
                if background_path.suffix.lower() in ['.jpg', '.png', '.jpeg', '.webp']:
                    background_img = cv2.imread(str(background_path), cv2.IMREAD_UNCHANGED)

                    superimposed_img, new_obb_points = superimpose_image(img, background_img, obb_points)
                    superimposed_img_scaled = scale_image(superimposed_img, (output_width, output_height))

                    new_filename = image_name + background_path.stem

                    print(f"Saving files into new name: {new_filename}")

                    save_all(new_filename, superimposed_img_scaled, new_obb_points, output_path) 

def process_without_bounding_boxes(images_path: Path, backgrounds_path: Path, output_path: Path, output_width=640, output_height=640):
    pass


def apply_transformation(points, matrix):
    points = np.array(points, dtype=np.float32).reshape(-1, 1, 2)
    transformed_points = cv2.perspectiveTransform(points, matrix)
    return transformed_points.reshape(-1, 2).tolist()

def rotate_image_and_points(image: cv2.typing.MatLike, obb_points, angle: int):
    img_h, img_w = image.shape[:2]

    cos_angle = np.abs(np.cos(np.radians(angle)))
    sin_angle = np.abs(np.sin(np.radians(angle)))

    new_w = int(img_h * sin_angle + img_w * cos_angle)
    new_h = int(img_h * cos_angle + img_w * sin_angle)

    M = cv2.getRotationMatrix2D((img_w // 2, img_h // 2), angle, 1.0)

    # Adjust the matrix to move the image to the center of the new canvas
    M[0, 2] += (new_w - img_w) // 2
    M[1, 2] += (new_h - img_h) // 2
    
    transparent_img = np.zeros((new_h, new_w, 4), dtype=np.uint8)

    rotated_image = cv2.warpAffine(image, M, dsize=(new_w, new_h), dst=transparent_img, borderMode=cv2.BORDER_TRANSPARENT, flags=cv2.INTER_LINEAR)
    obb_points_arr = np.array(obb_points)

    obb_points_abs = obb_points_arr * [img_w, img_h]

    ones = np.ones((obb_points_abs.shape[0], 1))
    points_ones = np.hstack([obb_points_abs, ones])

    rotated_points = M.dot(points_ones.T).T

    obb_points_rotated_normalized = rotated_points[:, :2] / [new_w, new_h]

    return rotated_image, obb_points_rotated_normalized

def superimpose_image(image: cv2.typing.MatLike , background: cv2.typing.MatLike, obb_points):

    background = cv2.cvtColor(background, cv2.COLOR_BGR2BGRA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2BGRA)

    ## rotate image + points
    rotation_angle = random.uniform(-30, 30)

    rotated_img, rotated_obb_points = rotate_image_and_points(image, obb_points, rotation_angle)

    ## resize rotated image to ensure fits in bounds of background
    image_scaled = scale_image_to_background(rotated_img, background)

    ## scale down and fit into background
    img_h, img_w = image_scaled.shape[:2]
    bg_h, bg_w = background.shape[:2]

    obb_points_abs = [(x * img_w, y * img_h) for x, y in rotated_obb_points]
    
    scale_factor = random.uniform(0.25, 0.9)
    new_img_w = int(img_w * scale_factor)
    new_img_h = int(img_h * scale_factor)
    resized_image = cv2.resize(image_scaled, (new_img_w, new_img_h))

    x_offset = random.randint(0, bg_w - new_img_w)
    y_offset = random.randint(0, bg_h - new_img_h)
    superimposed_image = cvzone.overlayPNG(background, resized_image, [x_offset, y_offset])
    # background[y_offset:y_offset+new_img_h, x_offset:x_offset+new_img_w] = resized_image

    # Calculate the scaling matrix for the resize
    scaling_matrix = np.array([[scale_factor, 0, 0], 
                               [0, scale_factor, 0], 
                               [0, 0, 1]])
    
    ## normalize points onto background
    transformed_obb_points = apply_transformation(obb_points_abs, scaling_matrix)

    # Translate the points by the offset where the image is placed on the background
    translated_obb_points = [(x + x_offset, y + y_offset) for x, y in transformed_obb_points]

    # Now normalize the OBB points relative to the background dimensions
    normalized_obb_points = [(x / bg_w, y / bg_h) for x, y in translated_obb_points]

    return superimposed_image, normalized_obb_points

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

    resized_image = cv2.resize(image, (new_img_w, new_img_h))

    # Now the image fits within the background, return the resized image
    return resized_image









