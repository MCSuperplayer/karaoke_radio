import vlc
import db

instance,player = None, None

def init():
    global instance,player
    instance = vlc.Instance()
    player = instance.media_player_new()

def play_track(track):
    song = db.get_track(track)
    title = song['name']
    source = song['source']
    media = instance.media_new(gdrive_url(track))
    db.track_played(track)
    player.set_media(media)
    player.play()
    return {'name':song['name'], 'id':song['id'], 'art':song['art']}

def get_progress():
    pos = player.get_position()
    if not pos:
        return 0
    return pos

def gdrive_url(id):
    return "https://drive.google.com/uc?export=download&id="+id

def is_playing():
    return player.is_playing()
