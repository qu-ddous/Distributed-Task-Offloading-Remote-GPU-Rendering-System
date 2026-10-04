import hashlib
from pathlib import Path
from typing import AsyncIterable

async def compute_sha256_stream(file_stream: AsyncIterable[bytes]) -> str:
    """
    Computes SHA-256 hash asynchronously chunk by chunk from a binary stream.
    """
    hasher = hashlib.sha256()
    async for chunk in file_stream:
        hasher.update(chunk)
    return hasher.hexdigest()

def compute_file_sha256(file_path: Path, chunk_size: int = 1024 * 1024) -> str:
    """
    Computes SHA-256 hash of a local file in chunks (default 1MB).
    """
    hasher = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(chunk_size):
            hasher.update(chunk)
    return hasher.hexdigest()
