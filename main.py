import db
import radio_logic
import player
import tkinter as tk
from PIL import Image,ImageTk
import time
import threading
import os

db.init()
thread_db = False
player.init()
#db.scan()

forced_queue = []
current_track = None
next_track = None
player_thread_run = True
root = tk.Tk()

def player_loop():
    global forced_queue,current_track,next_track, player_thread_run, thread_db, cover_art_path
    if not thread_db:
        db.init()
        thread_db = True
    while player_thread_run:
        if not player.is_playing():
            cur = player.play_track(next_track['id'])
            current_track = {'name':cur['name'],'id':cur['id']}
            cover_art_path = (cur['art'])
            next = radio_logic.pick_next_song()
            song = db.get_track(next)
            next_track = {'name':song['name'],'id':song['id']}
            time.sleep(10)
        time.sleep(0.5)

def cover_art():
    global cover_art_path,bg_img
    if cover_art_path == "##DONE":
        return
    if not cover_art_path:
        cover_art_path = "./local/default.webp"
    elif not os.path.isfile(cover_art_path):
        cover_art_path = "./local/default.webp"
    img = Image.open(cover_art_path)
    img = img.resize((120,120), Image.LANCZOS).convert("RGBA")
    bg_img = ImageTk.PhotoImage(img)
    cover_art_path = "##DONE"

cover_art_path = None
bg_img = None
cover_art()
player_thread = threading.Thread(target=player_loop)

def exit_program():
    global player_thread_run
    player_thread_run = False
    player_thread.join()
    root.destroy()

def open_controls():
    win = tk.Toplevel(root)
    win.title("Player Controls")
    win.geometry("300x200")

first_id = radio_logic.pick_next_song()
first_track = db.get_track(first_id)
next_track = {'name':first_track['name'],'id':first_track['id']}
current_track = next_track

root.overrideredirect(True)
root.configure(bg="black")
root.attributes("-topmost",True)
root.geometry("620x120+3220+1424")

canvas = tk.Canvas(root,width=620,height=120,bg="black",highlightthickness=0)
canvas.pack(fill="both",expand=True)

title_text = canvas.create_text(130,20,anchor="nw",text="Current Song Title",fill="white",font=("Terminus-TTF",10,"bold"))
next_text = canvas.create_text(130,70,anchor="nw",text="Next Song Title",fill="#aaaaaa",font=("Terminus-TTF",9))

bar_bg = canvas.create_rectangle(130,50,610,56,fill="#222",width=0)
bar_fg = canvas.create_rectangle(130,50,610,56,fill="white",width=0)

control_button = tk.Button(root,text="C",command=open_controls,bg="#333",fg="white",bd=0,highlightthickness=0,font=("Terminus-TTF",9))
control_button.place(x=590,y=90,width=20,height=20)

exit_button = tk.Button(root,text="X",command=exit_program)
exit_button.place(x=590,y=10,width=20,height=20)

cover_item = canvas.create_image(0,0,anchor="nw",image=bg_img)

def update_ui():
    global bg_img
    canvas.itemconfig(title_text,text=current_track['name'])
    canvas.itemconfig(next_text,text=next_track['name'])
    x_end = 130 + int(480*player.get_progress())
    canvas.coords(bar_fg,130,50,x_end,56)
    if not cover_art_path == "##DONE":
        cover_art()
        canvas.itemconfig(cover_item,image=bg_img)

    root.after(100,update_ui)

db.close()
player_thread.start()
update_ui()
root.mainloop()
