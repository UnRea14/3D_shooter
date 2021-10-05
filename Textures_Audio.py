from ursina import *

app = Ursina()

# Textures
background_texture = load_texture('assets/Textures/Game_Lobby.jpg')
sky_texture = load_texture('assets/Textures/Game_Sky.png')
gun_texture = load_texture('assets/Textures/Game_Gun.png')
ground_texture = load_texture('assets/Textures/Game_Floor.png')
box_texture = load_texture('assets/Textures/Game_Box.png')

# Audio
background_music = Audio('assets/Sounds/background.mp3', autoplay=False)
gunfire_sound = Audio('assets/Sounds/gunfire.wav', autoplay=False)
enemy_fire_sound = Audio('assets/Sounds/gunfire.wav', autoplay=False, volume=0.5)
reload_sound = Audio('assets/Sounds/reload.wav', autoplay=False)
hurt_sound = Audio('assets/Sounds/hurt.wav', autoplay=False, volume=3)
lost_sound = Audio('assets/Sounds/lose.wav', autoplay=False)
win_sound = Audio('assets/Sounds/win.wav', autoplay=False)
hit_sound = Audio('assets/Sounds/hit.wav', autoplay=False, volume=10)
