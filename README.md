# HALHAFARM - Auto Facebook Posts

Posts 1 video per day to the Halha Farm Facebook page automatically.

## Setup
1. Add secret `FB_USER_TOKEN` in Settings → Secrets → Actions
2. Videos are pre-uploaded to Facebook as drafts (IDs in video_ids.json)
3. GitHub Actions publishes one video per day at 9:00 AM Morocco time

## Token refresh
When token expires (~60 days), get a new one from:
https://developers.facebook.com/tools/explorer/
Then update the secret in GitHub Settings → Secrets → Actions → FB_USER_TOKEN
