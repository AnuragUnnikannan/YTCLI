import os
import platform
osname = platform.system()

# Importing and Installing dependencies

try:
    from youtubesearchpython import VideosSearch
    from pick import pick
    from pytube import Playlist
    import sqlite3
except:
    if osname == "Linux":
        pkgmgr = "pip3"
        os.system("sudo apt install mpv")
        os.system("sudo apt install python3-pip")
    else:
        pkgmgr = "pip"
        os.system("choco install mpv")
    os.system(pkgmgr+" install youtube-search-python")
    os.system(pkgmgr+" install pick")
    os.system(pkgmgr+" install pytube")
    os.system(pkgmgr+" install youtube-dl")
    from youtubesearchpython import VideosSearch
    from pick import pick
    from pytube import Playlist
    import sqlite3


# To manipulate data in database

def change(query, data=[]):
    con = sqlite3.connect("playlist.db")
    cur = con.cursor()
    if len(data) == 0:
        cur.execute(query)
    else:
        # for queries having many attribute values to insert
        cur.executemany(query, data)
    con.commit()


# To fetch data from database

def fetch(query):
    con = sqlite3.connect("playlist.db")
    cur = con.cursor()
    res = cur.execute(query)
    li = res.fetchall()
    return li

# To avoid misalignment of titles due to emojis and other characters

def cleanTitle(s):
    title = ''
    spl_char = '[@ _!#$%^&*()<>?/\|}.{~:]'
    for i in s:
        if i.isalpha() or i.isdigit() or i in spl_char:
            title = title + i
    return title

# To search for a particular song

def search(osname):
    s = ''
    while True:
        s = input("Search: ")
        if s == "\q":
            break
        else:
            videosSearch = VideosSearch(s, limit=21)
            r = videosSearch.result()
            disp_li = []
            li = []
            if osname == "Linux":
                os.system("clear")
            else:
                os.system("cls")

            for i in r["result"]:
                title = i["title"][:50]
                title = cleanTitle(title)
                if len(title) < 50:
                    title = title + " "*(50 - len(title))
                duration = i["duration"]
                views = i["viewCount"]["short"]
                disp_li.append("{0}\t\t{1}\t\t{2}".format(
                    title, duration, views))
                li.append(i["link"])

            play(disp_li, li)  # sending data to display search details

# To prompt the user to select a song and play it

def play(disp_li, li):
    title = "Choose video:"
    disp_li.append("Back")
    option, index = pick(disp_li, title, indicator='=>',
                         default_index=0)  # displays menu
    if index == len(disp_li)-1:
        return
    else:
        print(option, index)
        print("\n", li[index])
        command = "mpv {0} --no-video".format(li[index])
        os.system(command)

# To add new playlist

def addPlaylist(name, link):
    query = "CREATE TABLE IF NOT EXISTS Playlist(id, name, link)"
    change(query)
    query = "SELECT id FROM Playlist"
    id = 0
    li = fetch(query)

    # Setting playlist id
    if len(li) == 0:
        id = 1
    else:
        # id will be stored as str but converting to int for usage
        id = int(max(li)[0]) + 1

    data = [(str(id), name, link)]
    query = "INSERT INTO Playlist VALUES(?, ?, ?)"
    change(query, data)
    print("Playlist added")

# To prompt the user to select a playlist

def getPlaylist():
    query = "SELECT id, name FROM Playlist"
    li = fetch(query)
    disp_li = []
    for i in li:
        disp_li.append(" ".join(i))
    title = "Choose playlist:"
    option, index = pick(disp_li, title, indicator='=>',
                         default_index=0)  # displays playlist menu
    index = index+1
    query = "SELECT link FROM Playlist WHERE id='"+str(index)+"'"
    li = fetch(query)
    url = li[0][0]
    name = disp_li[index-1].split(' ')[1]  # storing playlist name
    playlist = Playlist(url)  # obtaining video urls from playlist

    # saving all urls to a .m3u file named by name of playlist
    with open(name+'.m3u', 'w') as f:
        for i in playlist:
            f.write(i+"\n")
    return name

# To prompt the user to select a playlist for deletion

def delPlaylist(osname):
    name = getPlaylist()
    query = "DELETE FROM Playlist WHERE name='"+name + \
        "'"  # deleting playlist record from database
    change(query)

    # deleting .m3u file
    if osname == "Linux":
        os.system("rm "+name+".m3u")
    else:
        os.system("del "+name+".m3u")
    print("Playlist Deleted")


if __name__ == "__main__":
    while(True):
        title = "\n\n What would you like to do? :"
        menu = ["Start Playlist", "Add Playlist",
                "Delete Playlist", "Search", "Exit"]
        options, index = pick(menu, title, indicator='=>', default_index=0)
        if index == 0:
            name = getPlaylist()
            os.system("mpv "+name+".m3u --no-video --shuffle")
        elif index == 1:
            name = input("Enter playlist name:")
            link = input("Enter url:")
            addPlaylist(name, link)
        elif index == 2:
            delPlaylist(osname)
        elif index == 3:
            search(osname)
        elif index == 4:
            exit()