import requests
import os
from PIL import Image
from io import BytesIO


BASE_DIR = "dataset"
SPLITS = {
     "test": 180
}
SIZE = 512  
CLASS_NAME = "INVALID"

# Ensure folders exist
for split in SPLITS:
    dir_path = os.path.join(BASE_DIR, split, CLASS_NAME)
    os.makedirs(dir_path, exist_ok=True)

# Download and save images
count = 1
for split, num_images in SPLITS.items():
    for i in range(num_images):
        try:
            url = f"https://picsum.photos/{SIZE}/{SIZE}?random={count}"
            response = requests.get(url)
            image = Image.open(BytesIO(response.content)).convert('L')  # Convert to grayscale
            filename = f"invalid_{count:04d}.jpg"
            save_path = os.path.join(BASE_DIR, split, CLASS_NAME, filename)
            image.save(save_path)
            print(f"[{split}] Saved: {filename}")
            count += 1
        except Exception as e:
            print(f"Error at image {count}: {e}")

print(f"\nDownload complete: {count-1} images saved across {len(SPLITS)} folders.")
