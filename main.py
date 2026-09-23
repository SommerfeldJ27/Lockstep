from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random


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
# APP
# ============================================================

app = Ursina()

window.title = WINDOW_TITLE
window.borderless = False
window.fullscreen = False
window.exit_button.visible = True
window.fps_counter.enabled = True


# ============================================================
# WORLD
# ============================================================

ground = Entity(
    model='cube',
    scale=(50, 1, 50),
    position=(0, 0, 0),
    collider='box',
    color=color.rgb(0, 255, 0)
)


# Outer walls
for i in range(-20, 21, 4):

    Entity(
        model='cube',
        scale=(4, 4, 1),
        position=(i, 2, 20),
        collider='box',
        color=color.gray
    )

    Entity(
        model='cube',
        scale=(4, 4, 1),
        position=(i, 2, -20),
        collider='box',
        color=color.gray
    )

    Entity(
        model='cube',
        scale=(1, 4, 4),
        position=(20, 2, i),
        collider='box',
        color=color.gray
    )

    Entity(
        model='cube',
        scale=(1, 4, 4),
        position=(-20, 2, i),
        collider='box',
        color=color.gray
    )


# ============================================================
# COVER
# ============================================================

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
        color=color.brown
    )


# ============================================================
# PLAYER
# ============================================================

player = FirstPersonController()

player.position = (0, 8, 0)
player.speed = PLAYER_SPEED
player.gravity = GRAVITY
player.cursor.visible = False


# Store player's previous position for weapon bobbing
previous_player_position = Vec3(
    player.x,
    player.y,
    player.z
)


# ============================================================
# SOUNDS
# ============================================================

rifle_sfx = Audio(
    'assets/sounds/rifle_fire.wav',
    autoplay=False
)

pistol_sfx = Audio(
    'assets/sounds/pistol_fire.wav',
    autoplay=False
)

reload_sfx = Audio(
    'assets/sounds/reload.wav',
    autoplay=False
)

hit_sfx = Audio(
    'assets/sounds/hit.wav',
    autoplay=False
)


# ============================================================
# WEAPONS
# ============================================================

weapons = {

    "rifle": {
        "damage": 25,
        "ammo": 30,
        "mag": 30,
        "recoil": 1.0,
        "reload_time": 1.5,
        "fire_rate": 0.12
    },

    "pistol": {
        "damage": 18,
        "ammo": 12,
        "mag": 12,
        "recoil": 0.6,
        "reload_time": 1.0,
        "fire_rate": 0.20
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
# CROSSHAIR
# ============================================================

crosshair_base_y = 0

crosshair_y = 0
target_crosshair_y = 0

crosshair_base_scale = 0.008

crosshair_scale = crosshair_base_scale
target_crosshair_scale = crosshair_base_scale


crosshair = Entity(
    parent=camera.ui,
    model='quad',
    color=color.white,
    scale=(crosshair_base_scale, crosshair_base_scale),
    position=(0, 0, 0),
    z=-10
)


hitmarker = Entity(
    parent=camera.ui,
    model='quad',
    color=color.red,
    scale=(0.01, 0.01),
    position=(0, 0, 0),
    z=-9,
    enabled=False
)


# ============================================================
# RIFLE MODEL
# ============================================================

rifle = Entity(
    parent=camera,
    model='cube',
    color=color.dark_gray,
    scale=(0.18, 0.18, 0.8),
    position=(0.45, -0.35, 0.8),
    rotation=(0, 0, 0)
)

rifle_barrel = Entity(
    parent=rifle,
    model='cube',
    color=color.black,
    scale=(0.35, 0.35, 1.2),
    position=(0, 0, 0.9)
)

rifle_stock = Entity(
    parent=rifle,
    model='cube',
    color=color.gray,
    scale=(0.8, 0.7, 0.45),
    position=(0, 0, -0.45)
)


# ============================================================
# PISTOL MODEL
# ============================================================

pistol = Entity(
    parent=camera,
    model='cube',
    color=color.dark_gray,
    scale=(0.16, 0.2, 0.55),
    position=(0.45, -0.35, 0.8),
    rotation=(0, 0, 0),
    enabled=False
)

pistol_barrel = Entity(
    parent=pistol,
    model='cube',
    color=color.black,
    scale=(0.8, 0.65, 0.7),
    position=(0, 0.05, 0.65)
)

pistol_grip = Entity(
    parent=pistol,
    model='cube',
    color=color.gray,
    scale=(0.9, 1.5, 0.8),
    position=(0, -0.6, -0.05),
    rotation=(15, 0, 0)
)


# ============================================================
# WEAPON BASE VALUES
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
    rifle.rotation_x,
    rifle.rotation_y,
    rifle.rotation_z
)

pistol_base_rotation = Vec3(
    pistol.rotation_x,
    pistol.rotation_y,
    pistol.rotation_z
)


# ============================================================
# WEAPON ANIMATION
# ============================================================

weapon_kick = 0
weapon_bob_time = 0


# ============================================================
# HUD
# ============================================================

ammo_text = Text(
    text="",
    position=(0.7, -0.45),
    scale=1.5
)

weapon_text = Text(
    text="",
    position=(0.7, -0.40),
    scale=1.2
)


# ============================================================
# ENEMY CLASS
# ============================================================

class Enemy(Entity):

    def __init__(self, position=(0, 1, 0)):

        super().__init__(
            model='cube',
            color=color.red,
            scale=(1, 2, 1),
            position=position,
            collider='box'
        )

        self.hp = 100

    def take_damage(self, amount):

        self.hp -= amount

        if self.hp <= 0:

            self.die()

    def die(self):

        if self in enemies:

            enemies.remove(self)

        destroy(self)

    def update(self):

        if not self.enabled:
            return

        distance = distance_xz(
            self.position,
            player.position
        )

        if distance < 20:

            direction = Vec3(
                player.x - self.x,
                0,
                player.z - self.z
            )

            if direction.length() > 0:

                direction = direction.normalized()

                self.position += (
                    direction *
                    time.dt *
                    1.2
                )


# ============================================================
# ENEMIES
# ============================================================

enemies = []

enemy_positions = [
    (8, 1, 8),
    (-8, 1, 8),
    (8, 1, -8),
    (-8, 1, -8),
    (12, 1, 0)
]

for pos in enemy_positions:

    enemies.append(
        Enemy(position=pos)
    )


# ============================================================
# HITMARKER
# ============================================================

def show_hitmarker():

    hitmarker.enabled = True

    invoke(
        hide_hitmarker,
        delay=0.08
    )


def hide_hitmarker():

    hitmarker.enabled = False


# ============================================================
# CROSSHAIR RESET
# ============================================================

def reset_crosshair():

    global target_crosshair_scale

    target_crosshair_scale = crosshair_base_scale


# ============================================================
# SHOOT COOLDOWN
# ============================================================

def set_can_shoot():

    global can_shoot

    can_shoot = True


# ============================================================
# FIRE ANIMATION
# ============================================================

def fire_weapon_animation():

    global weapon_kick

    weapon_kick = 1


# ============================================================
# SHOOT
# ============================================================

def shoot():

    global can_shoot
    global target_recoil
    global target_crosshair_y
    global target_crosshair_scale
    global weapon_kick

    if reloading:
        return

    weapon = weapons[current_weapon]

    if not can_shoot:
        return

    if weapon["ammo"] <= 0:
        return

    can_shoot = False

    invoke(
        set_can_shoot,
        delay=weapon["fire_rate"]
    )

    weapon["ammo"] -= 1


    # ========================================================
    # SOUND
    # ========================================================

    if current_weapon == "rifle":

        rifle_sfx.play()

    else:

        pistol_sfx.play()


    # ========================================================
    # GUN KICK
    # ========================================================

    fire_weapon_animation()


    # ========================================================
    # CAMERA RECOIL
    # ========================================================

    if current_weapon == "rifle":

        # Upward camera kick
        target_recoil.y += 1.6

        # Horizontal randomness
        target_recoil.x += random.uniform(
            -0.12,
            0.12
        )

        # Gun kick
        weapon_kick = 1.0

        # Crosshair movement
        target_crosshair_y += 0.035

    else:

        # Pistol kick
        target_recoil.y += 0.85

        target_recoil.x += random.uniform(
            -0.08,
            0.08
        )

        weapon_kick = 0.8

        target_crosshair_y += 0.022


    # Limit crosshair movement
    target_crosshair_y = min(
        target_crosshair_y,
        0.16
    )

    target_crosshair_scale = 0.014

    invoke(
        reset_crosshair,
        delay=0.08
    )


    # ========================================================
    # RAYCAST
    # ========================================================

    hit = raycast(
        camera.world_position,
        camera.forward,
        distance=100,
        ignore=[player]
    )

    if hit.hit:

        target = hit.entity

        if target and hasattr(
            target,
            "take_damage"
        ):

            target.take_damage(
                weapon["damage"]
            )

            hit_sfx.play()

            show_hitmarker()


# ============================================================
# RELOAD
# ============================================================

def reload_weapon():

    global reloading

    if reloading:
        return

    weapon = weapons[current_weapon]

    if weapon["ammo"] >= weapon["mag"]:
        return

    reloading = True

    reload_sfx.play()


    if current_weapon == "rifle":

        rifle.animate_position(
            rifle_base_position +
            Vec3(0, -0.25, -0.15),
            duration=0.25
        )

        rifle.animate_rotation(
            rifle_base_rotation +
            Vec3(20, 0, 0),
            duration=0.25
        )

        invoke(
            finish_reload,
            delay=weapon["reload_time"]
        )

        invoke(
            reset_rifle_position,
            delay=weapon["reload_time"]
        )

    else:

        pistol.animate_position(
            pistol_base_position +
            Vec3(0, -0.2, -0.1),
            duration=0.2
        )

        pistol.animate_rotation(
            pistol_base_rotation +
            Vec3(15, 0, 0),
            duration=0.2
        )

        invoke(
            finish_reload,
            delay=weapon["reload_time"]
        )

        invoke(
            reset_pistol_position,
            delay=weapon["reload_time"]
        )


# ============================================================
# FINISH RELOAD
# ============================================================

def finish_reload():

    global reloading

    weapon = weapons[current_weapon]

    weapon["ammo"] = weapon["mag"]

    reloading = False


# ============================================================
# RESET RIFLE
# ============================================================

def reset_rifle_position():

    rifle.animate_position(
        rifle_base_position,
        duration=0.25
    )

    rifle.animate_rotation(
        rifle_base_rotation,
        duration=0.25
    )


# ============================================================
# RESET PISTOL
# ============================================================

def reset_pistol_position():

    pistol.animate_position(
        pistol_base_position,
        duration=0.25
    )

    pistol.animate_rotation(
        pistol_base_rotation,
        duration=0.25
    )


# ============================================================
# SWITCH WEAPON
# ============================================================

def switch_weapon(weapon_name):

    global current_weapon

    if reloading:
        return

    current_weapon = weapon_name

    if current_weapon == "rifle":

        rifle.enabled = True
        pistol.enabled = False

    elif current_weapon == "pistol":

        rifle.enabled = False
        pistol.enabled = True


# ============================================================
# UPDATE
# ============================================================

def update():

    global recoil
    global target_recoil

    global weapon_kick
    global weapon_bob_time

    global previous_player_position

    global crosshair_y
    global target_crosshair_y

    global crosshair_scale
    global target_crosshair_scale


    # ========================================================
    # CAMERA RECOIL
    # ========================================================

    target_recoil = lerp(
        target_recoil,
        Vec3(0, 0, 0),
        10 * time.dt
    )

    recoil = lerp(
        recoil,
        target_recoil,
        25 * time.dt
    )


    # Apply recoil directly to the camera.
    #
    # Mouse movement remains normal.
    # Recoil temporarily pushes the camera upward.
    # Pulling the mouse downward fights it.
    # ========================================================

    player.camera_pivot.rotation_x -= (
        recoil.y
    )

    player.camera_pivot.rotation_y = (
        recoil.x * 2
    )


    # ========================================================
    # CROSSHAIR
    # ========================================================

    target_crosshair_y = lerp(
        target_crosshair_y,
        0,
        5 * time.dt
    )

    crosshair_y = lerp(
        crosshair_y,
        target_crosshair_y,
        14 * time.dt
    )

    crosshair_scale = lerp(
        crosshair_scale,
        target_crosshair_scale,
        20 * time.dt
    )

    crosshair.position = (
        0,
        crosshair_base_y + crosshair_y,
        0
    )

    crosshair.scale = (
        crosshair_scale,
        crosshair_scale
    )


    # ========================================================
    # GUN KICK RECOVERY
    # ========================================================

    weapon_kick = lerp(
        weapon_kick,
        0,
        15 * time.dt
    )


    # ========================================================
    # MOVEMENT DETECTION
    # ========================================================

    current_player_position = Vec3(
        player.x,
        player.y,
        player.z
    )

    movement_delta = (
        current_player_position -
        previous_player_position
    )

    horizontal_movement = Vec2(
        movement_delta.x,
        movement_delta.z
    ).length()


    is_moving = horizontal_movement > (
        0.001
    )


    previous_player_position = (
        current_player_position
    )


    # ========================================================
    # WEAPON BOB
    # ========================================================

    if player.grounded and is_moving:

        weapon_bob_time += (
            time.dt *
            WEAPON_BOB_SPEED
        )

        bob_x = (
            math.sin(weapon_bob_time)
            * WEAPON_BOB_AMOUNT
        )

        bob_y = (
            abs(
                math.cos(weapon_bob_time)
            )
            * WEAPON_BOB_AMOUNT
        )

    else:

        bob_x = 0
        bob_y = 0


    # ========================================================
    # GUN KICK
    # ========================================================

    kick_back = weapon_kick * 0.08

    kick_up = weapon_kick * 0.04


    # ========================================================
    # RIFLE
    # ========================================================

    if current_weapon == "rifle":

        rifle.position = (
            rifle_base_position
            + Vec3(
                bob_x,
                bob_y,
                -kick_back
            )
        )

        rifle.rotation = (
            rifle_base_rotation
            + Vec3(
                -kick_up * 30,
                0,
                0
            )
        )


    # ========================================================
    # PISTOL
    # ========================================================

    else:

        pistol.position = (
            pistol_base_position
            + Vec3(
                bob_x,
                bob_y,
                -kick_back
            )
        )

        pistol.rotation = (
            pistol_base_rotation
            + Vec3(
                -kick_up * 25,
                0,
                0
            )
        )


    # ========================================================
    # HUD
    # ========================================================

    weapon = weapons[current_weapon]

    ammo_text.text = (
        f"{weapon['ammo']} / "
        f"{weapon['mag']}"
    )

    weapon_text.text = (
        current_weapon.upper()
    )


# ============================================================
# INPUT
# ============================================================

def input(key):

    if key == 'left mouse down':

        shoot()

    elif key == 'r':

        reload_weapon()

    elif key == '1':

        switch_weapon("rifle")

    elif key == '2':

        switch_weapon("pistol")


# ============================================================
# START
# ============================================================

switch_weapon("rifle")

app.run()