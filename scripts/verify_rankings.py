"""
Verify EW and Vulture rankings against source articles.
Cross-checks (season, episode) + title_original against expected mappings.
Reports any mismatches.
"""

import json
from pathlib import Path

# Expected title -> (season, ep) for key check episodes
EW_SPOT_CHECKS = {
    (1, 1): "Pilot",
    (1, 3): "Squeeze",
    (1, 21): "Tooms",
    (3, 4): "Clyde Bruckman's Final Repose",
    (5, 12): "Bad Blood",
    (10, 3): "Mulder and Scully Meet the Were-Monster",
}

VULTURE_SPOT_CHECKS = {
    (1, 1): ("Pilot", 28),
    (3, 4): ("Clyde Bruckman's Final Repose", 1),  # Best
    (5, 12): ("Bad Blood", 2),
    (7, 20): ("Fight Club", 182),  # Worst
    (7, 9): ("Signs and Wonders", 148),
    (7, 10): ("Sein und Zeit", 176),  # Two-parter with Closure
}

def norm(s):
    return (s or "").replace('"', '').replace('‡', '').strip()

def main():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "web" / "data" / "x_files_episodes.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Build lookup: (season, ep) -> episode dict
    lookup = {}
    for season in data.get("seasons", []):
        sn = season.get("season_number")
        for ep in season.get("episodes", []):
            en = ep.get("episode_number")
            lookup[(sn, en)] = ep

    errors = []
    ok = 0

    # EW verification
    print("=== EW Ranking Verification ===")
    for (s, e), expected_title in EW_SPOT_CHECKS.items():
        ep = lookup.get((s, e))
        if not ep:
            errors.append(f"EW: Missing (S{s}E{e})")
            continue
        actual = norm(ep.get("title_original", ""))
        if expected_title.lower() not in actual.lower() and actual.lower() not in expected_title.lower():
            errors.append(f"EW: (S{s}E{e}) expected '{expected_title}', got '{actual}'")
        else:
            ew = ep.get("ew_rank")
            print(f"  S{s}E{e} {actual} -> ew_rank={ew} OK")
            ok += 1

    # Vulture verification
    print("\n=== Vulture Ranking Verification ===")
    for (s, e), (expected_title, expected_rank) in VULTURE_SPOT_CHECKS.items():
        ep = lookup.get((s, e))
        if not ep:
            errors.append(f"Vulture: Missing (S{s}E{e})")
            continue
        actual = norm(ep.get("title_original", ""))
        v_rank = ep.get("vulture_rank")
        title_ok = expected_title.lower() in actual.lower() or actual.lower() in expected_title.lower()
        rank_ok = v_rank == expected_rank
        if not title_ok:
            errors.append(f"Vulture: (S{s}E{e}) expected title '{expected_title}', got '{actual}'")
        if not rank_ok:
            errors.append(f"Vulture: (S{s}E{e}) {actual} expected rank {expected_rank}, got {v_rank}")
        if title_ok and rank_ok:
            print(f"  S{s}E{e} {actual} -> vulture_rank={v_rank} OK")
            ok += 1

    # Count totals
    ew_count = sum(1 for ep in lookup.values() if ep.get("ew_rank"))
    vulture_count = sum(1 for ep in lookup.values() if ep.get("vulture_rank"))
    print(f"\n=== Summary ===")
    print(f"  Episodes with ew_rank: {ew_count} (expected 27)")
    print(f"  Episodes with vulture_rank: {vulture_count} (expected 200 for S1-9)")
    print(f"  Spot checks passed: {ok}")

    if errors:
        print("\n=== ERRORS ===")
        for e in errors:
            print(f"  {e}")
        return 1
    print("\nAll verifications passed.")
    return 0

if __name__ == "__main__":
    exit(main())
