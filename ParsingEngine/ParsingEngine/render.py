from staticjinja import Site
from pathlib import Path
import json

if __name__ == "__main__":
    context = {
        "news": json.loads(Path("news-data.json").read_text())[0]
    }

    site = Site.make_site(env_globals=context)

    # enable automatic reloading

    site.render(use_reloader=True)
