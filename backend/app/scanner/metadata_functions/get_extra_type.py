from typing import Optional
from pathlib import Path
import re
from app.models.movie import MOVIE_EXTRA_TYPE

def get_extra_type(file_name: Path) -> tuple[ Optional[MOVIE_EXTRA_TYPE], Optional[str] ]:
    EXTRA_RE = re.compile(r"-(trailer|behindthescenes|makingoff)$")
    m = EXTRA_RE.search(file_name.stem)

    if m:
        parent_movie_file_name = file_name.stem.removesuffix(f"-{m.group(1)}")

        match m.group(1):
            case "trailer":
                return (MOVIE_EXTRA_TYPE.TRAILER, parent_movie_file_name)
            case "behindthescenes":
                return (MOVIE_EXTRA_TYPE.BEHIND_THE_SCENES, parent_movie_file_name)
            case "makingoff":
                return (MOVIE_EXTRA_TYPE.MAKING_OFF, parent_movie_file_name)
            
    return (None, None)