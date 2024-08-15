
from pathlib import Path
import pandas as pd
from PIL import Image
import imagehash
from typing import List, Dict

class PokemonCardMatcher:

    def __init__(self, path: Path):
        required_columns = ['Filename','Phash16','Phash32','Phash64','Phash128','Phash256']

        if not path.exists():
            raise FileNotFoundError("Could not find path to csv")
        
        self.df = pd.read_csv(path)
        self.validate_columns(required_columns)
        self._IMAGE_WIDTH = 240
        self._IMAGE_HEIGHT = 330

    def validate_columns(self, required_columns):
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        if missing_columns:
            raise ValueError(f"The following required columns are missing from the CSV: {', '.join(missing_columns)}")

    def get_top_n_matches(self, image: Image, n=5, hash_size=16) -> List[Dict[str, float]]:
        resized_image = image.resize((self._IMAGE_WIDTH, self._IMAGE_HEIGHT)).convert('L')
        phash = imagehash.phash(resized_image, hash_size=hash_size)
        
        distances = [
            {'filename': filename, 'distance': phash - imagehash.hex_to_hash(phash_str)}
            for filename, phash_str in zip(self.df['Filename'], self.df[f'Phash{hash_size}'])
        ]

        # Sort and return the top n matches
        return sorted(distances, key=lambda x: x['distance'])[:n]
