import requests
from pathlib import Path

from tqdm import tqdm


def download_file(url: str, output_path: Path):
    # send a GET request to the URL to download the file. Stream since it's large
    response = requests.get(url, stream=True)

    # open the file in binary mode and write the contents of the response to it in chunks
    # This is a large file, so be prepared to wait.
    with open(output_path, "wb") as f:
        for chunk in tqdm(response.iter_content(chunk_size=8192)):
            if chunk:
                f.write(chunk)
