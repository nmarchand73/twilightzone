"""
Add composite ranking to x_files_episodes.json based on mean of normalized EW and Vulture ranks.

Both rankings use lower = better. We normalize each to 0-1 (0=best, 1=worst), average them,
then assign composite_rank 1, 2, 3... by sorting ascending (lower composite_norm = better).

- Episodes with BOTH ranks: composite_norm = (ew_norm + vulture_norm) / 2
- Episodes with only EW (e.g. S10-11): composite_norm = ew_norm (Vulture doesn't rank these)
- Episodes with only Vulture: treat missing EW as 1.0 (not in top 25), so composite_norm = (1.0 + vulture_norm) / 2
- Episodes with neither: no composite_rank
"""

import json
from pathlib import Path

EW_MAX = 25
VULTURE_MAX = 182


def main():
    root = Path(__file__).resolve().parent.parent
    data_path = root / "web" / "data" / "x_files_episodes.json"
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Collect all episodes with at least one rank, compute normalized score
    scored = []
    for season in data.get("seasons", []):
        for ep in season.get("episodes", []):
            ew = ep.get("ew_rank")
            vulture = ep.get("vulture_rank")
            if ew is None and vulture is None:
                continue
            # Normalize to 0-1 (0=best, 1=worst)
            if ew is not None:
                ew_norm = (ew - 1) / (EW_MAX - 1) if EW_MAX > 1 else 0
            else:
                ew_norm = None
            if vulture is not None:
                vulture_norm = (vulture - 1) / (VULTURE_MAX - 1) if VULTURE_MAX > 1 else 0
            else:
                vulture_norm = None
            if ew_norm is not None and vulture_norm is not None:
                composite_norm = (ew_norm + vulture_norm) / 2
            elif ew_norm is not None:
                composite_norm = ew_norm  # EW-only (e.g. S10-11)
            else:
                composite_norm = (1.0 + vulture_norm) / 2  # Vulture-only: treat missing EW as worst
            scored.append((composite_norm, ep))

    # Sort by composite_norm ascending (lower = better), assign ranks
    scored.sort(key=lambda x: (x[0], x[1].get("episode_number_overall", 0)))
    for rank, (_, ep) in enumerate(scored, start=1):
        ep["composite_rank"] = rank
        ep["composite_rank_source"] = "Mean of normalized EW + Vulture rankings"

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Added composite_rank to {len(scored)} episodes in {data_path}")
    print(f"  Top 5: {[(e.get('title_original'), e.get('composite_rank')) for _, (_, e) in enumerate(scored[:5])]}")


if __name__ == "__main__":
    main()
