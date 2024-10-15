import cv2
import argparse
import os
import image_generator_helper
from pathlib import Path
import read_write_helpers


def main():
    # Create the argument parser
    output_width = 640
    output_height = 640

    parser = argparse.ArgumentParser(description="Resize images in a directory")
    
    # Define the flags and arguments
    parser.add_argument('--folder', type=str, help='Path to the directory containing images.', required=True)

    args = parser.parse_args()

    folder_path = Path(args.folder)

    for image_path in folder_path.iterdir():
        extension = image_path.suffix.lower()
        if extension in ['.jpg', '.png', '.jpeg', '.webp', '.jfif']:
            img = cv2.imread(str(image_path), cv2.IMREAD_UNCHANGED)
            img = image_generator_helper.scale_image(img)
            os.remove(str(image_path))
            read_write_helpers.save_image(img, image_path.stem, folder_path)
            

if __name__ == "__main__":
    main()