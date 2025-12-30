import asyncio
import json
import subprocess
from pathlib import Path
import hashlib
from random import random
from app.config import POSTER_DIR

def get_file_hash(path: str) -> str:
    """Generate a consistent hash for a file path"""
    #TODO: Add date based hashing, so it's not file dependant
    return hashlib.md5(path.encode("utf-8")).hexdigest()

async def get_video_metadata(path: str) -> dict:
    """
    Uses ffprobe to fetch metadata: duration, width, height, codec, etc.
    Returns a dict.
    """
    cmd = [
        "ffprobe",
        "-v", "error",
        "-print_format", "json",
        "-show_format",
        "-show_streams",
        path
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffprobe error: {stderr.decode().strip()}")
    
    return json.loads(stdout.decode())

async def generate_poster(path: str, length_in_seconds: float) -> str:
    """
    Generate a poster image from a random frame.
    Returns the poster path relative to MEDIA_ROOT.
    """
    file_hash = get_file_hash(path)
    poster_path = POSTER_DIR / f"{file_hash}.jpg"

    random_time = int(length_in_seconds * (0.05 + random() * 0.85))

    cmd = [
        "ffmpeg",
        "-y",
        "-ss", str(random_time),
        "-i", path,
        #"-vf", "thumbnail,scale=320:-1",
        "-q:v", "2",
        "-frames:v", "1",
        str(poster_path)
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg poster error: {stderr.decode()}")
    
    return str(poster_path.relative_to(POSTER_DIR))