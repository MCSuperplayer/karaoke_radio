from datetime import datetime
import random
import db

tracklist = {}

def weight(score, last_played):
    last_time = datetime.fromisoformat(last_played)
    now = datetime.now()
    minutes = (now - last_time).total_seconds() / 60
    weight = minutes * (2 ** score)
    return weight

def calculate_weights():
    global tracklist
    all_tracks = db.get_all_tracks()
    for track in all_tracks:
        tracklist[track['id']] = {
                "id": track['id'],
                "weight": weight(track['score'], track['last_played'])
            }

def pick_next_song():
    global tracklist
    calculate_weights()
    chosen_id = random.choices(list(tracklist.keys()), weights=[t["weight"] for t in tracklist.values()], k=1)[0]
    tracklist = {}
    return chosen_id
