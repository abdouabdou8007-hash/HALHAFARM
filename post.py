"""
HALHAFARM - GitHub Actions Daily Facebook Publisher
Publishes the next draft video on the Facebook page
"""
import os, json, urllib.request, urllib.parse, sys
from datetime import datetime

USER_TOKEN = os.environ["FB_USER_TOKEN"]
PAGE_ID    = os.environ["FB_PAGE_ID"]
STATE_FILE = "state.json"
IDS_FILE   = "video_ids.json"

VIDEOS = [
    "video_01_breeds.mp4",
    "video_02_broiler.mp4",
    "video_03_fertilized.mp4",
    "video_04_consumption_eggs.mp4",
    "video_05_olive_oil.mp4",
    "video_06_morning.mp4",
    "video_07_natural_feed.mp4",
    "video_08_chicks.mp4",
    "video_09_farm_to_table.mp4",
    "video_10_offers.mp4",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def get_page_token():
    url = f"https://graph.facebook.com/{PAGE_ID}?fields=access_token&access_token={USER_TOKEN}"
    with urllib.request.urlopen(url, timeout=15) as r:
        return json.loads(r.read())["access_token"]

def publish_video(video_id, page_token):
    data = urllib.parse.urlencode({
        "published": "true",
        "access_token": page_token
    }).encode()
    req = urllib.request.Request(
        f"https://graph.facebook.com/{video_id}",
        data=data, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# Load state
state = {"next_index": 0, "total_posted": 0}
if os.path.exists(STATE_FILE):
    with open(STATE_FILE) as f:
        state = json.load(f)

# Load video IDs
with open(IDS_FILE) as f:
    video_ids = json.load(f)

idx = state["next_index"] % len(VIDEOS)
filename = VIDEOS[idx]

log(f"Video {idx+1}/10: {filename}")

if filename not in video_ids:
    log(f"ERROR: no video_id found for {filename}")
    sys.exit(1)

video_id = video_ids[filename]
log(f"Video ID: {video_id}")

log("Getting page token...")
page_token = get_page_token()
log("Token OK")

log("Publishing...")
result = publish_video(video_id, page_token)
log(f"Result: {result}")

if result.get("success") or result.get("id"):
    state["next_index"] = (idx + 1) % len(VIDEOS)
    state["total_posted"] = state.get("total_posted", 0) + 1
    state["last_post"] = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "video": filename,
        "video_id": video_id
    }
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)
    log(f"SUCCESS! Total posted: {state['total_posted']}")
    log(f"Next: {VIDEOS[state['next_index']]}")
else:
    log(f"FAILED: {result}")
    sys.exit(1)
