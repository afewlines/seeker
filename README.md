# seeker
hey my artist name is brad, seeker and i appreciate the branding, so i'll be classifying my main projects under this bad boy

# current tools
## _new!_ music player
the goal for this project is to make a personal, lightweight desktop (and eventually raspi based) music player

i don't like google play music's interface, so that's where this spawned

i have a cli gpm playlist-player that hooks up to an rc vlc server, but i'm stalling on that because i'm liking kivy so far
### outline of work
- testing ui so i can operate at a base level
  - queue display
  - current song
  - start playlist
    - possible pause/play
  - next song
  - previous song
  - time readout


- player interface
  - listener for ui
  - handles audio playback


- queue class
  - a class dedicated to the music queue
  - contains list of songs and vital information
  - handles next, previous, replay
  - __eventually__ enum for type of queue (local, gpm)
