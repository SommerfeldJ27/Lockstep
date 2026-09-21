from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

app = Ursina()


# ============================================================
# CONFIG
# ============================================================

WINDOW_TITLE = "FPS Game"

PLAYER_SPEED = 5
PLAYER_SENSITIVITY = 40
GRAVITY = 1

WEAPON_BOB_SPEED = 10
WEAPON_BOB_AMOUNT = 0.015


# ============================================================
# WINDOW
# ============================================================

window.title = WINDOW_TITLE
window.show_fps_counter = True
window.vsync = True

mouse.locked = True


# ============================================================
# WORLD / MAP
# ============================================================

def create_world():

    global ground

    # Main floor
    ground = Entity(
        model='cube',
        scale=(50, 1, 50),
        position=(0, 0, 0),
        collider='box',
        color=color.rgb(0, 255, 0)
    )

    # --------------------------------------------------------
    # OUTER WALLS
    # --------------------------------------------------------

    for i in range(-20, 21, 4):

        # Back wall
        Entity(
            model='cube',
            scale=(4, 4, 1),
            position=(i, 2, -20),
            collider='box',
            color=color.gray
        )

        # Front wall
        Entity(
            model='cube',
            scale=(4, 4, 1),
            position=(i, 2, 20),
            collider='box',
            color=color.gray
        )

        # Left wall
        Entity(
            model='cube',
            scale=(1, 4, 4),
            position=(-20, 2, i),
            collider='box',
            color=color.gray
        )

        # Right wall
        Entity(
            model='cube',
            scale=(1, 4, 4),
            position=(20, 2, i),
            collider='box',
            color=color.gray
        )

    # --------------------------------------------------------
    # COVER
    # --------------------------------------------------------

    cover_positions = [
        (6, 1, 0),
        (-6, 1, 0),

        (0, 1, 6),
        (0, 1, -6),

        (10, 1, 10),
        (-10, 1, 10),

        (10, 1, -10),
        (-10, 1, -10)
    ]

    for pos in cover_positions:

        Entity(
            model='cube',
            scale=(2, 2, 2),
            position=pos,
            collider='box',
            color=color.rgb(90, 70, 60)
        )


# ============================================================
# PLAYER
# ============================================================

def create_player():

    global player
    global pitch

    player = FirstPersonController()

    player.position = (0, 8, 0)

    player.speed = PLAYER_SPEED
    player.gravity = GRAVITY

    pitch = 0


# ============================================================
# SOUND
# ============================================================

rifle_fire_sfx = Audio(
    'assets/sounds/rifle_fire.wav',
    autoplay=False,
    volume=0.6
)

pistol_fire_sfx = Audio(
    'assets/sounds/pistol_fire.wav',
    autoplay=False,
    volume=0.6
)

reload_sfx = Audio(
    'assets/sounds/reload.wav',
    autoplay=False,
    volume=0.8
)

hit_sfx = Audio(
    'assets/sounds/hit.wav',
    autoplay=False,
    volume=1.0
)


# ============================================================
# WEAPON DATA
# ============================================================

weapons = {

    "rifle": {
        "damage": 25,
        "ammo": 30,
        "mag": 30,
        "recoil": 1.2,
        "reload_time": 1.5,
        "fire_rate": 0.12
    },

    "pistol": {
        "damage": 18,
        "ammo": 12,
        "mag": 12,
        "recoil": 0.6,
        "reload_time": 1.0,
        "fire_rate": 0.2
    }
}


current_weapon = "rifle"

can_shoot = True
reloading = False


# ============================================================
# RECOIL
# ============================================================

recoil = Vec3(0, 0, 0)
target_recoil = Vec3(0, 0, 0)


# ============================================================
# HUD
# ============================================================

crosshair = Entity(
    parent=camera.ui,
    model='quad',
    scale=0.008,
    color=color.white,
    z=-10
)


ammo_text = Text(
    "",
    parent=camera.ui,
    position=(0.7, -0.45),
    scale=2,
    color=color.white
)


weapon_text = Text(
    "",
    parent=camera.ui,
    position=(0.7, -0.40),
    scale=1.5,
    color=color.gray
)


# ------------------------------------------------------------
# HITMARKER
# ------------------------------------------------------------

hitmarker = Entity(
    parent=camera.ui,
    model='quad',
    scale=0.01,
    color=color.red,
    enabled=False,
    z=-9
)


def show_hitmarker():

    hitmarker.enabled = True
    hitmarker.scale = 0.018

    invoke(hide_hitmarker, delay=0.08)


def hide_hitmarker():

    hitmarker.enabled = False
    hitmarker.scale = 0.01


# ============================================================
# GUN MODELS
# ============================================================

# ------------------------------------------------------------
# RIFLE
# ------------------------------------------------------------

rifle = Entity(
    parent=camera,
    model='cube',
    color=color.black,
    scale=(0.18, 0.12, 0.6),
    position=(0.35, -0.35, 0.7),
    rotation=(0, 0, 0)
)


# Rifle barrel

rifle_barrel = Entity(
    parent=rifle,
    model='cube',
    color=color.dark_gray,
    scale=(0.65, 0.65, 0.8),
    position=(0, 0, 0.65)
)


# Rifle stock

rifle_stock = Entity(
    parent=rifle,
    model='cube',
    color=color.gray,
    scale=(0.9, 0.8, 0.5),
    position=(0, 0, -0.45)
)


# ------------------------------------------------------------
# PISTOL
# ------------------------------------------------------------

pistol = Entity(
    parent=camera,
    model='cube',
    color=color.gray,
    scale=(0.12, 0.1, 0.35),
    position=(0.35, -0.38, 0.6),
    rotation=(0, 0, 0),
    enabled=False
)


# Pistol barrel

pistol_barrel = Entity(
    parent=pistol,
    model='cube',
    color=color.black,
    scale=(0.7, 0.7, 0.9),
    position=(0, 0, 0.55)
)


# Pistol grip

pistol_grip = Entity(
    parent=pistol,
    model='cube',
    color=color.dark_gray,
    scale=(0.8, 1.4, 0.6),
    position=(0, -0.55, -0.15),
    rotation=(12, 0, 0)
)


# ============================================================
# WEAPON ANIMATION STATE
# ============================================================

rifle_base_position = Vec3(
    rifle.position.x,
    rifle.position.y,
    rifle.position.z
)

pistol_base_position = Vec3(
    pistol.position.x,
    pistol.position.y,
    pistol.position.z
)


rifle_base_rotation = Vec3(
    rifle.rotation.x,
    rifle.rotation.y,
    rifle.rotation.z
)

pistol_base_rotation = Vec3(
    pistol.rotation.x,
    pistol.rotation.y,
    pistol.rotation.z
)


weapon_kick = 0
weapon_bob_time = 0


# ============================================================
# WEAPON SWITCHING
# ============================================================

def update_guns():

    rifle.enabled = current_weapon == "rifle"
    pistol.enabled = current_weapon == "pistol"


# ============================================================
# WEAPON FIRE ANIMATION
# ============================================================

def fire_weapon_animation():

    global weapon_kick

    weapon_kick = 1


# ============================================================
# RELOAD ANIMATION
# ============================================================

def start_reload_animation():

    global reloading

    if current_weapon == "rifle":

        rifle.animate_position(
            rifle_base_position + Vec3(0.08, -0.18, -0.12),
            duration=0.25,
            curve=curve.out_quad
        )

        rifle.animate_rotation(
            rifle_base_rotation + Vec3(-12, 3, 4),
            duration=0.25,
            curve=curve.out_quad
        )

        invoke(finish_reload_animation, delay=0.65)

    else:

        pistol.animate_position(
            pistol_base_position + Vec3(0.08, -0.18, -0.1),
            duration=0.2,
            curve=curve.out_quad
        )

        pistol.animate_rotation(
            pistol_base_rotation + Vec3(-10, 3, 5),
            duration=0.2,
            curve=curve.out_quad
        )

        invoke(finish_reload_animation, delay=0.45)


def finish_reload_animation():

    if current_weapon == "rifle":

        rifle.animate_position(
            rifle_base_position,
            duration=0.35,
            curve=curve.in_out_quad
        )

        rifle.animate_rotation(
            rifle_base_rotation,
            duration=0.35,
            curve=curve.in_out_quad
        )

    else:

        pistol.animate_position(
            pistol_base_position,
            duration=0.3,
            curve=curve.in_out_quad
        )

        pistol.animate_rotation(
            pistol_base_rotation,
            duration=0.3,
            curve=curve.in_out_quad
        )


# ============================================================
# ENEMIES
# ============================================================

class Enemy(Entity):

    def __init__(self, position=(0, 0, 0)):

        super().__init__(
            model='cube',
            color=color.red,
            position=position,
            scale=(1, 2, 1),
            collider='box'
        )

        self.hp = 100
        self.dead = False


    def take_damage(self, dmg):

        if self.dead:
            return

        self.hp -= dmg

        if self.hp <= 0:

            self.dead = True
            self.die()


    def die(self):

        self.enabled = False

        if self in enemies:
            enemies.remove(self)

        destroy(self)


# ============================================================
# ENEMY SPAWNS
# ============================================================

enemies = [

    Enemy(position=(5, 1, 10)),
    Enemy(position=(-5, 1, 10))

]


# ============================================================
# SHOOTING
# ============================================================

def set_can_shoot():

    global can_shoot

    can_shoot = True


def shoot():

    global can_shoot
    global target_recoil

    if reloading:
        return

    w = weapons[current_weapon]

    if not can_shoot:
        return

    if w["ammo"] <= 0:
        return

    # --------------------------------------------------------
    # FIRE COOLDOWN
    # --------------------------------------------------------

    can_shoot = False

    invoke(
        set_can_shoot,
        delay=w["fire_rate"]
    )

    # --------------------------------------------------------
    # AMMO
    # --------------------------------------------------------

    w["ammo"] -= 1

    # --------------------------------------------------------
    # SOUND
    # --------------------------------------------------------

    if current_weapon == "rifle":

        rifle_fire_sfx.play()

    else:

        pistol_fire_sfx.play()

    # --------------------------------------------------------
    # WEAPON ANIMATION
    # --------------------------------------------------------

    fire_weapon_animation()

    # --------------------------------------------------------
    # RECOIL
    # --------------------------------------------------------

    target_recoil.y += w["recoil"] * 0.4

    target_recoil.x += random.uniform(
        -0.08,
        0.08
    )

    # --------------------------------------------------------
    # HIT DETECTION
    # --------------------------------------------------------

    hit = raycast(
        camera.world_position,
        camera.forward,
        distance=100,
        ignore=[player]
    )

    if hit.hit and hit.entity:

        if hasattr(hit.entity, "take_damage"):

            target = hit.entity

            target.take_damage(
                w["damage"]
            )

            hit_sfx.play()

            show_hitmarker()

    # --------------------------------------------------------
    # CROSSHAIR FEEDBACK
    # --------------------------------------------------------

    crosshair.scale = 0.014

    invoke(
        reset_crosshair,
        delay=0.08
    )


def reset_crosshair():

    crosshair.scale = 0.008


# ============================================================
# RELOAD
# ============================================================

def reload():

    global reloading
    global can_shoot

    if reloading:
        return

    w = weapons[current_weapon]

    if w["ammo"] >= w["mag"]:
        return

    reloading = True
    can_shoot = False

    # sound

    reload_sfx.play()

    # animation

    start_reload_animation()

    # actual reload

    invoke(
        finish_reload,
        delay=w["reload_time"]
    )


def finish_reload():

    global reloading
    global can_shoot

    w = weapons[current_weapon]

    w["ammo"] = w["mag"]

    reloading = False
    can_shoot = True


# ============================================================
# INPUT
# ============================================================

def input(key):

    global current_weapon

    # --------------------------------------------------------
    # SHOOT
    # --------------------------------------------------------

    if key == 'left mouse down':

        shoot()

    # --------------------------------------------------------
    # RELOAD
    # --------------------------------------------------------

    if key == 'r':

        reload()

    # --------------------------------------------------------
    # RIFLE
    # --------------------------------------------------------

    if key == '1':

        if not reloading:

            current_weapon = "rifle"

    # --------------------------------------------------------
    # PISTOL
    # --------------------------------------------------------

    if key == '2':

        if not reloading:

            current_weapon = "pistol"


# ============================================================
# UPDATE
# ============================================================

def update():

    global pitch
    global recoil
    global target_recoil
    global weapon_kick
    global weapon_bob_time

    # ========================================================
    # PLAYER LOOK
    # ========================================================

    player.rotation_y += (
        mouse.velocity[0]
        * PLAYER_SENSITIVITY
    )

    pitch -= (
        mouse.velocity[1]
        * PLAYER_SENSITIVITY
    )

    pitch = clamp(
        pitch,
        -90,
        90
    )

    camera.rotation_x = pitch


    # ========================================================
    # RECOIL
    # ========================================================

    target_recoil = lerp(
        target_recoil,
        Vec3(0, 0, 0),
        8 * time.dt
    )

    recoil = lerp(
        recoil,
        target_recoil,
        12 * time.dt
    )

    camera.rotation_x = (
        pitch
        - recoil.y * 0.6
    )

    camera.rotation_y = (
        recoil.x * 2
    )


    # ========================================================
    # WEAPON BOB
    # ========================================================

    moving = (
        held_keys['w']
        or held_keys['a']
        or held_keys['s']
        or held_keys['d']
    )

    if moving and not reloading:

        weapon_bob_time += time.dt * WEAPON_BOB_SPEED

        bob_x = (
            sin(weapon_bob_time)
            * WEAPON_BOB_AMOUNT
        )

        bob_y = (
            abs(cos(weapon_bob_time))
            * WEAPON_BOB_AMOUNT
        )

    else:

        bob_x = 0
        bob_y = 0


    # ========================================================
    # WEAPON KICK
    # ========================================================

    weapon_kick = lerp(
        weapon_kick,
        0,
        15 * time.dt
    )

    kick_back = weapon_kick * 0.08
    kick_up = weapon_kick * 0.04


    # ========================================================
    # APPLY RIFLE ANIMATION
    # ========================================================

    if current_weapon == "rifle" and not reloading:

        rifle.position = Vec3(
            rifle_base_position.x + bob_x,
            rifle_base_position.y + bob_y + kick_up,
            rifle_base_position.z - kick_back
        )

        rifle.rotation = Vec3(
            rifle_base_rotation.x - kick_up * 30,
            rifle_base_rotation.y,
            rifle_base_rotation.z
        )


    # ========================================================
    # APPLY PISTOL ANIMATION
    # ========================================================

    if current_weapon == "pistol" and not reloading:

        pistol.position = Vec3(
            pistol_base_position.x + bob_x,
            pistol_base_position.y + bob_y + kick_up,
            pistol_base_position.z - kick_back
        )

        pistol.rotation = Vec3(
            pistol_base_rotation.x - kick_up * 25,
            pistol_base_rotation.y,
            pistol_base_rotation.z
        )


    # ========================================================
    # ENEMY AI
    # ========================================================

    for e in enemies[:]:

        if not e:
            continue

        if e.dead:
            continue

        if distance(
            e.position,
            player.position
        ) < 20:

            e.look_at(
                player.position
            )

            e.position += (
                e.forward
                * time.dt
            )


    # ========================================================
    # HUD
    # ========================================================

    w = weapons[current_weapon]

    ammo_text.text = (
        f"{w['ammo']} / {w['mag']}"
    )

    weapon_text.text = (
        current_weapon.upper()
    )


# ============================================================
# START GAME
# ============================================================

create_world()
create_player()

update_guns()

app.run()