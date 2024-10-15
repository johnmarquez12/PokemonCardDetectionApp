import albumentations as A
import cv2
import argparse
from pathlib import Path
import shutil
import read_write_helpers


def augment_image(image):
    augmentations = [   
                        A.GaussNoise(var_limit=(10.0, 50.0), p=0.66), 
                        A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.66),
                        A.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.2, p=0.25),
                        A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.33),
                        A.Blur(blur_limit=7, p=0.5),
                        A.HueSaturationValue(hue_shift_limit=0, sat_shift_limit=40, val_shift_limit=0, p=0.5),
                        A.CLAHE(clip_limit=4.0, tile_grid_size=(8, 8), p=0.33),
                        A.ISONoise(color_shift=(0.01, 0.05), intensity=(0.1, 0.5), p=0.33),
                    ]
    
    transform = A.Compose(augmentations)

    augmented = transform(image=image)
    aug_image = augmented['image']

    return aug_image

def main():

    parser = argparse.ArgumentParser(description="Process images and optionally handle bounding boxes and backgrounds.")
    
    # Define the flags and arguments
    parser.add_argument('--images', type=str, help='Path to the directory containing images.', required=True)
    parser.add_argument('--labels', type=str, help='Path to the directory containing labels.', required=True)

    # Parse the command-line arguments
    args = parser.parse_args()

    images_path = Path(args.images)
    obb_path = Path(args.labels)

    for image_path in images_path.iterdir():
        if image_path.suffix.lower() in ['.jpg', '.png', '.jpeg', '.webp']:
            image_name = image_path.stem
            obb_file = obb_path / f"{image_name}.txt"

            image = cv2.imread(str(image_path))

            for i in range(5):
                augmented_image = augment_image(image)
                read_write_helpers.save_image(augmented_image, f"{image_name}_{i + 1}", images_path)

                new_obb_file = obb_path / f"{image_name}_{i + 1}.txt"
                shutil.copy(obb_file, new_obb_file)
                
if __name__ == "__main__":
    main()