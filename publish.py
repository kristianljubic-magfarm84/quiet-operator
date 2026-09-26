#!/usr/bin/env python3
"""Publish the next card to Instagram, then advance the queue.

Reads:  state.json -> next_index
        quotes.json -> the line for that index
Posts:  the pre-rendered card at docs/cards/NNN.png, served from raw.githubusercontent
Writes: state.json (the workflow commits it)

Exits non-zero on any failure so GitHub emails you. Never posts twice for one
index: state.json only advances after Instagram confirms the publish.
"""
import json, os, sys, time, urllib.error, urllib.parse, urllib.request

ROOT = os.path.dirname(os.path.abspath(__file__))
API = os.environ.get("IG_API_VERSION", "v23.0")
BASE = f"https://graph.facebook.com/{API}"
TOKEN = os.environ.get("IG_ACCESS_TOKEN")
IG_USER_ID = os.environ.get("IG_USER_ID")
DRY_RUN = os.environ.get("DRY_RUN") == "1"

HASHTAGS = {
    "decisions": "#leadership #decisionmaking #management #businessmindset "
                 "#executive #clarity #strategy #leadershipdevelopment",
    "speed": "#discipline #process #execution #operations #workethic "
             "#professionalism #businessgrowth #focus",
    "restraint": "#negotiation #communication #emotionalintelligence #composure "
                 "#leadershipskills #influence #selfcontrol #business",
    "patience": "#longterm #consistency #compounding #patience #career "
                "#buildinginpublic #resilience #stoicism",
}


def _call(url, params, method="GET"):
    try:
        if method == "POST":
            req = urllib.request.Request(
                url, data=urllib.parse.urlencode(params).encode(), method="POST")
        else:
            req = urllib.request.Request(url + "?" + urllib.parse.urlencode(params))
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {body}") from None


def die(msg):
    print(f"ERROR: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    cfg = json.load(open(os.path.join(ROOT, "config.json")))
    quotes = json.load(open(os.path.join(ROOT, "quotes.json")))
    state_path = os.path.join(ROOT, "state.json")
    state = json.load(open(state_path))

    idx = state["next_index"]
    entry = next((q for q in quotes if q["id"] == idx), None)
    if entry is None:
        die(f"queue exhausted at index {idx} — top up quotes.json "
            f"(bank currently ends at {max(q['id'] for q in quotes)})")

    card = os.path.join(ROOT, "docs", "cards", f"{idx:03d}.png")
    if not os.path.exists(card):
        die(f"card not rendered: {card} — run build_cards.py and commit")

    if "REPLACE_ME" in cfg["github_user"]:
        die("config.json still says REPLACE_ME — set github_user to your GitHub username")

    image_url = (f"https://raw.githubusercontent.com/{cfg['github_user']}"
                 f"/{cfg['github_repo']}/main/docs/cards/{idx:03d}.png")
    caption = f"{entry['text']}\n\n·\n\n{HASHTAGS.get(entry['pillar'], '')}"

    print(f"index {idx} | {entry['pillar']} | {entry['text']}")
    print(f"image  {image_url}")

    if DRY_RUN:
        print("DRY_RUN — nothing posted")
        return
    if not TOKEN or not IG_USER_ID:
        die("IG_ACCESS_TOKEN and IG_USER_ID must both be set")

    # 1. container
    try:
        c = _call(f"{BASE}/{IG_USER_ID}/media",
                  {"image_url": image_url, "caption": caption, "access_token": TOKEN},
                  method="POST")
    except Exception as e:
        die(f"container creation failed: {e}\n"
            f"Usual causes: token invalid (see the Monday health check), or the image "
            f"URL is not publicly reachable — open it in a browser to check.")
    cid = c.get("id")
    if not cid:
        die(f"no container id in response: {c}")

    # 2. wait for Instagram to fetch the image
    for _ in range(20):
        st = _call(f"{BASE}/{cid}", {"fields": "status_code,status", "access_token": TOKEN})
        if st.get("status_code") == "FINISHED":
            break
        if st.get("status_code") == "ERROR":
            die(f"container errored: {st.get('status')}")
        time.sleep(5)
    else:
        die("container never reached FINISHED after 100s")

    # 3. publish
    try:
        r = _call(f"{BASE}/{IG_USER_ID}/media_publish",
                  {"creation_id": cid, "access_token": TOKEN}, method="POST")
    except Exception as e:
        die(f"publish failed: {e}")
    print(f"published: {r}")

    # 4. advance only after success
    state["next_index"] = idx + 1
    state.setdefault("history", []).append({"index": idx, "media_id": r.get("id")})
    state["history"] = state["history"][-60:]
    with open(state_path, "w") as f:
        json.dump(state, f, indent=1)
    print(f"next_index -> {idx + 1}")


if __name__ == "__main__":
    main()
