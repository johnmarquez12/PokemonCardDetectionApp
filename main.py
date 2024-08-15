import numpy as np
import cv2
import imagehash
from PIL import Image
import pandas as pd
import os
from pokemoncardmatcher import PokemonCardMatcher
from pathlib import Path
from cardextractor import CardExtractor

card_matcher = PokemonCardMatcher(path=Path("pokemon-tcg-image-data.csv"))

def display_cards(distances):
    print('Top n closest images:')

    for entry in distances[:1]:
        filename = entry['filename']
        distance = entry['distance']
        print(f'{filename} with distance {distance}')
        image_path = os.path.join('pokemon-tcg-images', filename.removesuffix('.png'), filename)
        read_image = cv2.imread(image_path)

        if read_image is not None:
            cv2.imshow("detected card", read_image)

def convert_to_pillow(cv_image):
    cv_rgb_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(cv_rgb_image)
    return pil_image

def main():
    # Initialize the webcam
    cap = cv2.VideoCapture(1)

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            break
        
        x, y, w, h = 200, 200, 480, 660  # x and y are the top-left corner, w is width, h is height
        roi = frame[y:y+h, x:x+w]
        cv2.rectangle(frame, (x - 5, y - 5), (x+w + 10, y+h + 10), (0, 255, 0), 2)
        # cv2.rectangle(frame, (x + 10, y + 10), (x+40+240, y+40+330), (255, 255, 0), 2)

        # Display the original frame with edges and the cropped card
        # concatenated = cv2.hconcat([frame, edges])
        cv2.imshow('camera', frame)

        # Detect and crop the Pokémon card
        key = cv2.waitKey(1) & 0xFF

        # if key == ord('d'):
        cropped_card, edges = CardExtractor.extract_card(roi, canny_threshold1=50, canny_threshold2=140)
        cv2.imshow('edges', edges)
    
        if cropped_card is not None:
            cv2.imshow('Cropped Card', cropped_card)
            img = convert_to_pillow(cropped_card)
            distances = card_matcher.get_top_n_matches(img, hash_size=32)
            display_cards(distances)

        if key == ord('q'):
            break

    # When everything is done, release the capture
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
