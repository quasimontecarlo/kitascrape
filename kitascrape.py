import os
import re
import requests
import argparse
from bs4 import BeautifulSoup

### cli arguments build
parser = argparse.ArgumentParser(
        prog = "kitascrape",
        description = "this tools scrapes japan's kitamura camera scan website",
        epilog = "your life must be good now that my job is over")
parser.add_argument("-u", "--url", type=str, required=True, help = "the url link to kitamura's scanned pics")
parser.add_argument("-o", "--out", default = "", help = "the output location on disk where the images will be saved, default value is the current folder you're runnign this tool from")

args = parser.parse_args()
url = args.url
directory = args.out

BASE_URL = "https://fs.kitamura.jp"
# Replace this with the actual URL you are viewing in your browser
GALLERY_URL = url

# Set headers to mimic a browser
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# Create a folder to save your high-res files
if directory is None:
    output_folder = "%s/kitamura_output" % directory
else:
    output_folder = "kitamura_output"
os.makedirs(output_folder, exist_ok=True)

# Fetch the page content
response = requests.get(GALLERY_URL, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Find all grid items
grid_items = soup.find_all("a", class_="grid_item")
print(f"Found {len(grid_items)} images in the grid.")

for index, item in enumerate(grid_items):
    img_tag = item.find("img")
    if not img_tag or not img_tag.get("alt"):
        continue

    alt_content = img_tag["alt"]

    # Extract the download path using regular expressions
    match = re.search(r'href=["\'](/photo/image_download/[^"\']+)["\']', alt_content)

    if match:
        download_path = match.group(1)
        full_download_url = BASE_URL + download_path

        # Extract the ID to use as a filename
        photo_id = download_path.split("/")[-1]
        filename = os.path.join(output_folder, f"{photo_id}.jpg")

        print(f"[{index+1}/{len(grid_items)}] Downloading high-res ID {photo_id}...")

        # Download and save the high-res file
        print(full_download_url)
        img_response = requests.get(full_download_url, headers=headers)
        if img_response.status_code == 200:
            with open(filename, "wb") as f:
                f.write(img_response.content)
        else:
            print(f"Failed to download ID {photo_id}. Status code: {img_response.status_code}")

print("Download complete!")
