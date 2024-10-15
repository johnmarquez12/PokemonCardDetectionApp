import argparse
import os
import image_generator_helper
from pathlib import Path

def main():
    # Create the argument parser
    output_width = 640
    output_height = 640

    parser = argparse.ArgumentParser(description="Process images and optionally handle bounding boxes and backgrounds.")
    
    # Define the flags and arguments
    parser.add_argument('--images', type=str, help='Path to the directory containing images.', required=True)
    parser.add_argument('--labels', type=str, help='If specified, process bounding boxes for the images.')
    parser.add_argument('--backgrounds', type=str, help='Path to the directory containing background images.', required=True)
    parser.add_argument('--output_width', type=int, help='output width of images')
    parser.add_argument('--output_height', type=int, help='output height of images')
    parser.add_argument('--output_dir', type=str, help='Output Directory of Images', required=True)

    # Parse the command-line arguments
    args = parser.parse_args()

    if not os.path.isdir(args.images):
        print(f"Error: The directory {args.images} does not exist.")
        return
    
    if args.bounding_boxes:
        image_generator_helper.process_with_bounding_boxes(images_path=Path(args.images), bounding_boxes_path=Path(args.labels), backgrounds_path=Path(args.backgrounds), output_path=Path(args.output_dir))
        return
    
    image_generator_helper.process_without_bounding_boxes(images_path=Path(args.images), 
        bounding_boxes_path=Path(args.bounding_boxes),
        backgrounds_path=Path(args.backgrounds))

if __name__ == "__main__":
    main()