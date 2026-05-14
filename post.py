"""HALHAFARM - Daily Facebook Publisher (Morning 9h + Evening 18h)"""
import os, json, urllib.request, urllib.parse, sys
from datetime import datetime

PAGE_TOKEN = os.environ["FB_USER_TOKEN"]   # permanent page token
PAGE_ID    = os.environ["FB_PAGE_ID"]
SESSION    = os.environ.get("SESSION", "morning")

# Morning videos (9:00) — Set 1
VIDEOS_MORNING = [
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

# Evening videos (18:00) — Set 2
VIDEOS_EVENING = [
    "video_B01_quality.mp4",
    "video_B02_recipes.mp4",
    "video_B03_roosters.mp4",
    "video_B04_egg_benefits.mp4",
    "video_B05_olive_benefits.mp4",
    "video_B06_delivery.mp4",
    "video_B07_seasons.mp4",
    "video_B08_compare.mp4",
    "video_B09_farm_life.mp4",
    "video_B10_order_now.mp4",
]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}", flush=True)

def publish_video(video_id):
    data = urllib.parse.urlencode({
        "published": "true",
        "access_token": PAGE_TOKEN
    }).encode()
    req = urllib.request.Request(
        f"https://graph.facebook.com/{video_id}",
        data=data, method="POST"
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())

# Select config based on session
if SESSION == "evening":
    videos_list = VIDEOS_EVENING
    state_file  = "state_evening.json"
    ids_file    = "video_ids_v2.json"
    label       = "EVENING 18:00"
else:
    videos_list = VIDEOS_MORNING
    state_file  = "state.json"
    ids_file    = "video_ids.json"
    label       = "MORNING 9:00"

log(f"Session: {label}")

# Load state
state = {"next_index": 0, "total_posted": 0}
if os.path.exists(state_file):
    with open(state_file) as f:
        state = json.load(f)

# Load video IDs
if not os.path.exists(ids_file):
    log(f"ERROR: {ids_file} not found!")
    sys.exit(1)
with open(ids_file) as f:
    video_ids = json.load(f)

idx      = state["next_index"] % len(videos_list)
filename = videos_list[idx]
log(f"Video {idx+1}/{len(videos_list)}: {filename}")

if filename not in video_ids:
    log(f"ERROR: {filename} not in {ids_file}")
    sys.exit(1)

video_id = video_ids[filename]
log(f"Video ID: {video_id}")
log("Publishing...")
result = publish_video(video_id)
log(f"Result: {result}")

if result.get("success") or result.get("id"):
    state["next_index"]   = (idx + 1) % len(videos_list)
    state["total_posted"] = state.get("total_posted", 0) + 1
    state["last_post"] = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "video": filename,
        "video_id": video_id,
        "session": label
    }
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)
    log(f"SUCCESS! Total {label}: {state['total_posted']}")
    log(f"Next: {videos_list[state['next_index']]}")
else:
    log(f"FAILED: {result}")
    sys.exit(1)
