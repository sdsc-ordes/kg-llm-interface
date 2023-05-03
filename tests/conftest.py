import gzip
from pathlib import Path
import pytest
import shutil
import tempfile

from aikg.utils.io import download_file

TEST_SCHEMA_URL = "https://www.pokemonkg.org/ontology/ontology.nt"
TEST_INSTANCES_URL = "https://www.pokemonkg.org/download/dump/poke-a.nq.gz"


@pytest.fixture(scope="module")
def instance_file() -> Path:
    """Download and gunzip remote instance test file."""
    gz_path = tempfile.NamedTemporaryFile(suffix=".nq.gz", delete=False).name
    download_file(TEST_INSTANCES_URL, gz_path)
    path = gz_path.removesuffix(".gz")
    # gunzip downloaded file
    with gzip.open(gz_path, "rb") as f_in:
        with open(path, "wb") as f_out:
            shutil.copyfileobj(f_in, f_out)

    return Path(path)


@pytest.fixture(scope="module")
def schema_file() -> Path:
    """Download remote schema test file."""
    path = tempfile.NamedTemporaryFile(suffix=".nt", delete=False).name
    download_file(TEST_SCHEMA_URL, path)
    return Path(path)


@pytest.fixture(scope="module")
def small_instance_file(instance_file) -> Path:
    """Create a small instance file for testing, truncated to 100 lines."""
    path = tempfile.NamedTemporaryFile(suffix=".nq", delete=False).name

    with open(instance_file) as f, open(path, "w") as f_out:
        for i, line in enumerate(f):
            if i > 100:
                break
            f_out.write(line)
    return Path(path)
