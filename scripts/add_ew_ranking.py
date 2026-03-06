"""
Add Entertainment Weekly's "25 best X-Files episodes" ranking to x_files_episodes.json.
Source: https://ew.com/tv/best-x-files-episodes/

Maps (season, episode) -> ew_rank (1-25). Also adds ew_rank_source URL.
"""

import json
from pathlib import Path

# EW "The 25 best episodes of The X-Files" - (season, episode) -> rank
# Some ranks apply to multiple episodes (e.g. Squeeze/Tooms share rank 2, Dreamland two-parter shares 21)
EW_RANK_MAP = {
    (1, 1): 1,   # Pilot
    (1, 3): 2,   # Squeeze
    (1, 21): 2,  # Tooms
    (1, 8): 3,   # Ice
    (1, 13): 4,  # Beyond the Sea
    (2, 2): 5,   # The Host
    (2, 20): 6,  # Humbug
    (2, 25): 7,  # Anasazi
    (3, 4): 8,   # Clyde Bruckman's Final Repose
    (3, 12): 9,  # War of the Coprophages
    (3, 17): 10, # Pusher
    (3, 20): 11, # Jose Chung's From Outer Space
    (4, 2): 12,  # Home
    (4, 7): 13,  # Musings of a Cigarette Smoking Man
    (4, 10): 14, # Paper Hearts
    (4, 14): 15, # Memento Mori
    (4, 20): 16, # Small Potatoes
    (5, 5): 17,  # The Post-Modern Prometheus
    (5, 12): 18, # Bad Blood
    (6, 2): 19,  # Drive
    (6, 3): 20,  # Triangle
    (6, 4): 21,  # Dreamland I
    (6, 5): 21,  # Dreamland II
    (6, 6): 22,  # How the Ghosts Stole Christmas
    (6, 15): 23, # Arcadia
    (7, 12): 24, # X-Cops
    (10, 3): 25, # Mulder and Scully Meet the Were-Monster
}

EW_SOURCE_URL = "https://ew.com/tv/best-x-files-episodes/"


def main():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "web" / "data" / "x_files_episodes.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    count = 0
    for season in data.get("seasons", []):
        sn = season.get("season_number")
        for ep in season.get("episodes", []):
            en = ep.get("episode_number")
            key = (sn, en)
            if key in EW_RANK_MAP:
                ep["ew_rank"] = EW_RANK_MAP[key]
                ep["ew_rank_source"] = EW_SOURCE_URL
                count += 1

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added EW ranking to {count} episodes in {data_path}")


if __name__ == "__main__":
    main()
