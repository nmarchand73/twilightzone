"""
Add Vulture's "Every Episode of The X-Files, Ranked" to x_files_episodes.json.
Source: https://www.vulture.com/article/every-episode-of-the-x-files-ranked.html

Vulture ranked 182 entries (two-parters = 1 entry) from worst (182) to best (1).
Lower vulture_rank = better episode. 1 = best (Clyde Bruckman's Final Repose).

Note: Vulture's list covers seasons 1-9 only (original run). Seasons 10-11 not ranked.
"""

import json
from pathlib import Path

# Vulture "Every Episode of The X-Files, Ranked" - (season, episode) -> rank
# Rank: 1=best, 182=worst. Two-parters share the same rank.
VULTURE_RANK_MAP = {
    (1, 1): 28,   # Pilot
    (1, 2): 47,   # Deep Throat
    (1, 3): 44,   # Squeeze
    (1, 4): 76,   # Conduit
    (1, 5): 175,  # The Jersey Devil
    (1, 6): 143,  # Shadows
    (1, 7): 167,  # Ghost in the Machine
    (1, 8): 14,   # Ice
    (1, 9): 178,  # Space
    (1, 10): 61,  # Fallen Angel
    (1, 11): 31,  # Eve
    (1, 12): 147, # Fire
    (1, 13): 68,  # Beyond the Sea
    (1, 14): 73,  # Gender Bender
    (1, 15): 118, # Lazarus
    (1, 16): 159, # Young at Heart
    (1, 17): 33,  # E.B.E.
    (1, 18): 139, # Miracle Man
    (1, 19): 177, # Shapes
    (1, 20): 29,  # Darkness Falls
    (1, 21): 23,  # Tooms
    (1, 22): 119, # Born Again
    (1, 23): 117, # Roland
    (1, 24): 18,  # The Erlenmeyer Flask
    (2, 1): 90,   # Little Green Men
    (2, 2): 137,  # The Host
    (2, 3): 158,  # Blood
    (2, 4): 136,  # Sleepless
    (2, 5): 19,   # Duane Barry
    (2, 6): 19,   # Ascension
    (2, 7): 166,  # 3
    (2, 8): 34,   # One Breath
    (2, 9): 138,  # Firewalker
    (2, 10): 74,  # Red Museum
    (2, 11): 174, # Excelsis Dei
    (2, 12): 160, # Aubrey
    (2, 13): 36,  # Irresistible
    (2, 14): 26,  # Die Hand Die Verletzt
    (2, 15): 156, # Fresh Bones
    (2, 16): 5,   # Colony
    (2, 17): 5,   # End Game
    (2, 18): 149, # Fearful Symmetry
    (2, 19): 122, # Død Kalm
    (2, 20): 17,  # Humbug
    (2, 21): 162, # The Calusari
    (2, 22): 91,  # F. Emasculata
    (2, 23): 135, # Soft Light
    (2, 24): 125, # Our Town
    (2, 25): 69,  # Anasazi
    (3, 1): 55,   # The Blessing Way
    (3, 2): 55,   # Paper Clip
    (3, 3): 32,   # D.P.O.
    (3, 4): 1,    # Clyde Bruckman's Final Repose (BEST)
    (3, 5): 142,  # The List
    (3, 6): 120,  # 2Shy
    (3, 7): 146,  # The Walk
    (3, 8): 57,   # Oubliette
    (3, 9): 87,   # Nisei
    (3, 10): 87,  # 731
    (3, 11): 38,  # Revelations
    (3, 12): 67,  # War of the Coprophages
    (3, 13): 77,  # Syzygy
    (3, 14): 49,  # Grotesque
    (3, 15): 86,  # Piper Maru
    (3, 16): 86,  # Apocrypha
    (3, 17): 8,   # Pusher
    (3, 18): 171, # Teso Dos Bichos
    (3, 19): 155, # Hell Money
    (3, 20): 4,   # Jose Chung's From Outer Space
    (3, 21): 46,  # Avatar
    (3, 22): 88,  # Quagmire
    (3, 23): 92,  # Wetwired
    (3, 24): 65,  # Talitha Cumi
    (4, 1): 48,   # Herrenvolk
    (4, 2): 3,    # Home
    (4, 3): 170,  # Teliko
    (4, 4): 72,   # Unruhe
    (4, 5): 100,  # The Field Where I Died
    (4, 6): 172,  # Sanguinarium
    (4, 7): 13,   # Musings of a Cigarette Smoking Man
    (4, 8): 109,  # Tunguska
    (4, 9): 109,  # Terma
    (4, 10): 11,  # Paper Hearts
    (4, 11): 121, # El Mundo Gira
    (4, 12): 59,  # Leonard Betts
    (4, 13): 53,  # Never Again
    (4, 14): 6,   # Memento Mori
    (4, 15): 133, # Kaddish
    (4, 16): 124, # Unrequited
    (4, 17): 56,  # Tempus Fugit
    (4, 18): 56,  # Max
    (4, 19): 131, # Synchrony
    (4, 20): 12,  # Small Potatoes
    (4, 21): 64,  # Zero Sum
    (4, 22): 150, # Elegy
    (4, 23): 63,  # Demons
    (4, 24): 60,  # Gethsemane
    (5, 1): 99,   # Redux I
    (5, 2): 99,   # Redux II
    (5, 3): 24,   # Unusual Suspects
    (5, 4): 20,   # Detour
    (5, 5): 7,    # The Post-Modern Prometheus
    (5, 6): 89,   # Christmas Carol
    (5, 7): 89,   # Emily
    (5, 8): 153,  # Kitsunegari
    (5, 9): 179,  # Schizogeny
    (5, 10): 151, # Chinga
    (5, 11): 168, # Kill Switch
    (5, 12): 2,   # Bad Blood
    (5, 13): 104, # Patient X
    (5, 14): 104, # The Red and the Black
    (5, 15): 101, # Travelers
    (5, 16): 102, # Mind's Eye
    (5, 17): 132, # All Souls
    (5, 18): 51,  # The Pine Bluff Variant
    (5, 19): 30,  # Folie à Deux
    (5, 20): 84,  # The End
    (6, 1): 115,  # The Beginning
    (6, 2): 54,   # Drive
    (6, 3): 10,   # Triangle
    (6, 4): 110,  # Dreamland I
    (6, 5): 110,  # Dreamland II
    (6, 6): 79,   # How the Ghosts Stole Christmas
    (6, 7): 103,  # Terms of Endearment
    (6, 8): 130,  # The Rain King
    (6, 9): 108,  # S.R. 819
    (6, 10): 39,  # Tithonus
    (6, 11): 145, # Two Fathers
    (6, 12): 145, # One Son
    (6, 13): 173, # Agua Mala
    (6, 14): 15,  # Monday
    (6, 15): 35,  # Arcadia
    (6, 16): 154, # Alpha
    (6, 17): 157, # Trevor
    (6, 18): 129, # Milagro
    (6, 19): 50,  # The Unnatural
    (6, 20): 78,  # Three of a Kind
    (6, 21): 22,  # Field Trip
    (6, 22): 106, # Biogenesis
    (7, 1): 114,  # The Sixth Extinction
    (7, 2): 114,  # Amor Fati
    (7, 3): 96,   # Hungry
    (7, 4): 83,   # Millennium
    (7, 5): 134,  # Rush
    (7, 6): 75,   # The Goldberg Variation
    (7, 7): 111,  # Orison
    (7, 8): 97,   # The Amazing Maleeni
    (7, 9): 148,  # Signs and Wonders (Vulture said S7E10, but S7E10 is Sein und Zeit; S7E9 is correct)
    (7, 10): 176, # Sein und Zeit
    (7, 11): 176, # Closure
    (7, 12): 27,  # X-Cops
    (7, 13): 181, # First Person Shooter
    (7, 14): 81,  # Theef
    (7, 15): 105, # En Ami
    (7, 16): 140, # Chimera
    (7, 17): 95,  # All Things
    (7, 18): 141, # Brand X
    (7, 19): 25,  # Hollywood A.D.
    (7, 20): 182, # Fight Club (WORST)
    (7, 21): 42,  # Je Souhaite
    (7, 22): 40,  # Requiem
    (8, 1): 80,   # Within
    (8, 2): 80,   # Without
    (8, 3): 94,   # Patience
    (8, 4): 52,   # Roadrunners
    (8, 5): 128,  # Invocation
    (8, 6): 41,   # Redrum
    (8, 7): 21,   # Via Negativa
    (8, 8): 112,  # Surekill
    (8, 9): 127,  # Salvage
    (8, 10): 165, # Badlaa
    (8, 11): 16,  # The Gift
    (8, 12): 98,  # Medusa
    (8, 13): 45,  # Per Manum
    (8, 14): 43,  # This Is Not Happening
    (8, 15): 43,  # Deadalive
    (8, 16): 93,  # Three Words
    (8, 17): 123, # Empedocles
    (8, 18): 62,  # Vienen
    (8, 19): 85,  # Alone
    (8, 20): 71,  # Essence
    (8, 21): 71,  # Existence
    (9, 1): 161,  # Nothing Important Happened Today I
    (9, 2): 161,  # Nothing Important Happened Today II
    (9, 3): 163,  # Dæmonicus
    (9, 4): 113,  # 4-D
    (9, 5): 144,  # Lord of the Flies
    (9, 6): 107,  # Trust No 1
    (9, 7): 58,   # John Doe
    (9, 8): 126,  # Hellbound
    (9, 9): 152,  # Provenance
    (9, 10): 152, # Providence
    (9, 11): 37,  # Audrey Pauley
    (9, 12): 169, # Underneath
    (9, 13): 66,  # Improbable
    (9, 14): 116, # Scary Monsters
    (9, 15): 180, # Jump the Shark
    (9, 16): 82,  # William
    (9, 17): 70,  # Release
    (9, 18): 9,   # Sunshine Days
    (9, 19): 164, # The Truth I
    (9, 20): 164, # The Truth II
}

VULTURE_SOURCE_URL = "https://www.vulture.com/article/every-episode-of-the-x-files-ranked.html"


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
            if key in VULTURE_RANK_MAP:
                ep["vulture_rank"] = VULTURE_RANK_MAP[key]
                ep["vulture_rank_source"] = VULTURE_SOURCE_URL
                count += 1

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added Vulture ranking to {count} episodes in {data_path}")


if __name__ == "__main__":
    main()
