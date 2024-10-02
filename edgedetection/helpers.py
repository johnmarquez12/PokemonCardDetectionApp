from PIL import Image
import os

def resize_image_save(filepath, new_name):
    with Image.open(filepath) as img:
        resized_img = img.resize((240,330))
        resized_img.save(os.path.join('pokemon-tcg-test-images', f'{new_name}_resized.png'))

def resize_image_greyscale_save(filepath, new_name):
    with Image.open(filepath) as img:
        resized_img = img.resize((240,330)).convert('L')
        resized_img.save(os.path.join('pokemon-tcg-test-images', f'{new_name}_greyresized.png'))


