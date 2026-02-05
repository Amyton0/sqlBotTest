import json
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from models.video import Video
from models.video_snapshot import VideoSnapshot
load_dotenv()

DB_PASSWORD = os.getenv("DB_PASSWORD")

engine = create_engine(f'postgresql://postgres:{DB_PASSWORD}@localhost/sqlbot')

with open('videos.json') as f:
    json_data = f.read()

data = json.loads(json_data)

for video_json in data["videos"]:
    session = Session(engine)
    video_id = video_json["id"]
    video = Video(id=video_id)
    session.add(video)
    for key, val in video_json.items():
        if key == "id":
            continue
        if key != "snapshots":
            setattr(video, key, val)
            continue
        for snapshot_json in val:
            snapshot_id = snapshot_json["id"]
            snapshot = VideoSnapshot(id=snapshot_id)
            session.add(snapshot)
            snapshot.video_id = video_id
            for snapshot_key, snapshot_val in snapshot_json.items():
                if snapshot_key == "id":
                    continue
                setattr(snapshot, snapshot_key, snapshot_val)
    session.commit()
