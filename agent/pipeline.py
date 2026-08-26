import json
from pathlib import Path

from .researcher import research_app


OUTPUT_FILE = Path("data/first_pass.json")


def load_apps():
    with open(
        "data/apps.json",
        "r",
        encoding="utf-8",
    ) as f:
        return json.load(f)


def save_results(results):
    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_FILE.write_text(
        json.dumps(
            results,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )


def run_first_pass():

    apps = load_apps()

    results = []

    total = len(apps)

    print(
        f"Starting first-pass research for {total} apps..."
    )

    for index, app in enumerate(apps, start=1):

        print()
        print(
            f"[{index}/{total}] Researching {app['name']}..."
        )

        try:

            result = research_app(app)

            results.append(
                result.model_dump()
            )

            # Save after EVERY successful app
            save_results(results)

            print(
                f"[{index}/{total}] {app['name']} COMPLETE"
            )

        except Exception as e:

            print(
                f"[{index}/{total}] {app['name']} FAILED: {e}"
            )

            # Preserve everything completed so far
            save_results(results)

            continue

    print()
    print(
        f"First-pass research finished."
    )

    print(
        f"Successful apps: {len(results)}/{total}"
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )

    return results