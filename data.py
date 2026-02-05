import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from models.video import Video
from models.video_snapshot import VideoSnapshot

engine = create_engine('postgresql://postgres:postgres@localhost/sqlbot', echo=True)

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
