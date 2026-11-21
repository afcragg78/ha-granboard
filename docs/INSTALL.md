# Granboard For Home Assistant: Complete Setup Guide

This guide walks you through everything from a fresh install to lights, sounds, and a dashboard. You don't need to be a developer. Wherever it says **Settings > ...**, that's the Home Assistant sidebar menu.

> **This project is unofficial and is not affiliated with, endorsed by, or supported by Granboard / GRAN Darts.** The Bluetooth protocol is community reverse-engineered.

## Contents

1. [What You Need](#1-what-you-need)
2. [Set Up Bluetooth (Adapter Or ESPHome Proxy)](#2-set-up-bluetooth-adapter-or-esphome-proxy)
3. [Install With HACS](#3-install-with-hacs)
4. [Install Manually (Without HACS)](#4-install-manually-without-hacs)
5. [Add Your Board](#5-add-your-board)
6. [What You Get (Entities)](#6-what-you-get-entities)
7. [Configure Options](#7-configure-options)
8. [Custom Sounds](#8-custom-sounds)
9. [Using The Official Granboard App (Kill Switch)](#9-using-the-official-granboard-app-kill-switch)
10. [Playing Games (Actions)](#10-playing-games-actions)
11. [Board Lights During Games](#11-board-lights-during-games)
12. [LED Ring Light (Between Games)](#12-led-ring-light-between-games)
13. [WLED Sections (Lights Around The Board)](#13-wled-sections-lights-around-the-board)
14. [WLED And Room Lights Automations](#14-wled-and-room-lights-automations)
15. [Dashboard Examples](#15-dashboard-examples)
16. [Updating](#16-updating)
17. [Troubleshooting](#17-troubleshooting)
18. [Uninstalling](#18-uninstalling)

---

## 1. What You Need

| Item | Details |
|---|---|
| Home Assistant | **2025.1 or newer** (Home Assistant OS, Supervised, Container, or Core). Some newer dashboard card features in the examples need a recent release. |
| Dartboard | A **Granboard 3 / 3s** with Bluetooth. Other Granboards that advertise the same Bluetooth service may work but haven't been tested. |
| Bluetooth | A Bluetooth adapter Home Assistant can use, **or** (recommended) an **ESPHome Bluetooth proxy** near the board. See [section 2](#2-set-up-bluetooth-adapter-or-esphome-proxy). The connection has to be *connectable* (active). Passive-only proxies won't work. |
| HACS | Optional, but it makes installing and updating easy. See [hacs.xyz](https://hacs.xyz). |
| Speaker | Optional, for custom sounds: any Home Assistant `media_player`. |
| WLED / Smart Lights | Optional, for room effects. |

**Important things to know before you start:**

- **The board takes one Bluetooth connection at a time.** While Home Assistant is connected, the official Granboard app can't connect, and the other way round. **Close the Granboard app (swipe it away) on every phone and tablet** before adding the board. You can hand the board back to the app at any time; see [section 9](#9-using-the-official-granboard-app-kill-switch).
- Bluetooth range through a cabinet and a wall is short. Most missed hits and disconnects are range problems.

## 2. Set Up Bluetooth (Adapter Or ESPHome Proxy)

### Option A: A Bluetooth Adapter On The Home Assistant Machine

1. Plug in a supported USB Bluetooth adapter (or use the built-in one).
2. Go to **Settings > Devices & Services**. Home Assistant usually discovers it as **Bluetooth**. Click **Add**.
3. That's it, as long as the dartboard is within a few metres with nothing big in the way. If the board is in another room, use Option B.

### Option B: An ESPHome Bluetooth Proxy (Recommended)

An ESP32 board (about $5 to $10) running ESPHome, placed **close to the dartboard or inside the dart cabinet**, gives a much stronger, steadier link than a USB adapter across the house. It connects to Home Assistant over Wi-Fi.

1. Install the **ESPHome Device Builder** add-on (**Settings > Add-ons > Add-on Store > ESPHome**), or use the [web installer](https://esphome.io/projects/?type=bluetooth) and pick **Bluetooth Proxy**.
2. Create a new device and use a config like this. The important lines are the two `active: true`, which let the proxy *connect* to the board, not just listen.

```yaml
esphome:
  name: dart-cabinet-proxy
  friendly_name: Dart Cabinet Proxy

esp32:
  board: esp32dev          # match your ESP32 board
  framework:
    type: esp-idf          # recommended for Bluetooth proxies

wifi:
  ssid: !secret wifi_ssid
  password: !secret wifi_password

api:
logger:
ota:
  - platform: esphome

esp32_ble_tracker:
  scan_parameters:
    active: true

bluetooth_proxy:
  active: true
```

3. Install it on the ESP32, power it inside or right next to the cabinet (a USB phone charger is fine), and adopt it in **Settings > Devices & Services > ESPHome**.
4. Home Assistant uses the proxy automatically. You don't need to pick it anywhere.

**Tips:**

- Keep the proxy within about 1 to 2 metres of the board, with no metal between them.
- Use Wi-Fi with a good signal, or an Ethernet ESP32 (such as an Olimex ESP32-POE) for the best reliability.
- Each proxy can hold only a few active connections at once. A dedicated proxy for the dartboard is best.

## 3. Install With HACS

1. Open **HACS** in the sidebar.
2. Click the **⋮** menu (top right) and choose **Custom repositories**.
3. In **Repository**, paste `https://github.com/afcragg78/ha-granboard`. In **Type** (or **Category**), choose **Integration**. Click **Add**, then close the dialog.
4. Search HACS for **Granboard**, open it, and click **Download** (choose the latest version), then **Download** again.
5. **Restart Home Assistant**: **Settings > System > ⋮ (or the power icon) > Restart Home Assistant**. The integration won't appear until you restart.

## 4. Install Manually (Without HACS)

1. Download the latest release ZIP from the [Releases page](https://github.com/afcragg78/ha-granboard/releases) (**Source code (zip)**).
2. Unzip it and copy the folder `custom_components/granboard` into your Home Assistant config folder, so you end up with:
   ```
   /config/custom_components/granboard/__init__.py
   /config/custom_components/granboard/manifest.json
   ...
   ```
   Use the **File editor**, **Samba share**, or **Studio Code Server** add-on to reach `/config`. Create the `custom_components` folder if it doesn't exist.
3. **Restart Home Assistant.**

To update a manual install, delete the old `granboard` folder, copy in the new one, and restart.

## 5. Add Your Board

1. **Close the Granboard app** on every phone and tablet.
2. Turn the board on. While it waits for a connection, the board's light flashes red.
3. **Automatic discovery:** after a minute or so, **Settings > Devices & Services** shows a **Discovered: GRANBOARD** card. Click **Add**, then **Submit**.
4. **Manual setup** (if nothing is discovered): click **+ Add Integration**, search **Granboard**, and in **Board** pick it from the list, or type its Bluetooth address (six pairs like `AA:BB:CC:11:22:33`; dashes or lower case are fine). An address you type is accepted even if the board isn't visible yet, and the integration keeps trying in the background.
   - You can find the address in **Settings > Devices & Services > Bluetooth > Configure / Advertisement Monitor**, or in the ESPHome proxy's logs. Look for the name `GRANBOARD`.
5. The board is added as **Granboard XXXX** (the last four characters of its address), or by its advertised name if that's different. You can rename the device; entity IDs follow the device name, for example `sensor.granboard_5547_game`.
6. Within a few seconds the **Connected** sensor turns **on** and the board stops flashing. Press a bed and the **Last Hit** sensor updates.

The integration keeps the board connected and reconnects by itself (it backs off gradually and retries as soon as the board advertises again). The first ~2 seconds of hits after connecting are ignored, because the board can replay its last hit when it connects.

## 6. What You Get (Entities)

Find them on the device page: **Settings > Devices & Services > Granboard > (your board)**. In the IDs below, `<board>` is your device name in lower case with underscores, for example `granboard_5547`.

| Entity | ID | What It Does |
|---|---|---|
| Switch **Granboard Connection** | `switch.<board>_granboard_connection` | The kill switch. Off disconnects and holds no connection, so the official app can connect. |
| Button **Release Board** | `button.<board>_release_board` | One tap turns the kill switch off. |
| Binary Sensor **Connected** | `binary_sensor.<board>_connected` | On while the Bluetooth link is up. |
| Sensor **Last Hit** | `sensor.<board>_last_hit` | `T20`, `D16`, `S5`, `SB` (25), `DB` (50), `MISS`, with number, multiplier, score, ring and raw frame as attributes. |
| Sensor **Game** | `sensor.<board>_game` | `idle`, `playing` or `finished`. Its attributes hold the whole game (scores, players, colors, darts, checkout, stats). Not stored in history. |
| Sensor **Last Raw Frame** | `sensor.<board>_last_raw_frame` | Diagnostic: the last frame exactly as the board sent it. |
| Sensor **Signal Strength** | `sensor.<board>_signal_strength` | Diagnostic: RSSI from the board's last advertisement. It only updates while the board is *not* connected, because the board stops advertising once it's connected. |
| Light **LED Ring** | `light.<board>_led_ring` | The board's LED ring as a light between games. See [section 12](#12-led-ring-light-between-games). |
| Select **Ring Palette** | `select.<board>_ring_palette` | Palette for LED Ring effects (configuration). |
| Number **Ring Speed** | `number.<board>_ring_speed` | 0 to 255, default 128 (configuration). |
| Number **Ring Intensity** | `number.<board>_ring_intensity` | 0 to 255, default 128 (configuration). |
| Text **Ring Color 2** | `text.<board>_ring_color_2` | Second color as `#RRGGBB`, empty by default (configuration). |

**Events** (for automations): `granboard_hit`, `granboard_award`, `granboard_turn`, `granboard_button` and `granboard_sound`. See [section 14](#14-wled-and-room-lights-automations) and the README's Events list.

## 7. Configure Options

Go to **Settings > Devices & Services > Granboard > Configure** (on newer versions, the ⚙ cog next to the entry). A menu offers **General**, **Sounds**, **Sound Volumes** and **WLED Sections**. Changes apply right away, with no restart needed.

### General

| Option | Default | What It Does |
|---|---|---|
| **Board Button Ends The Turn** | On | During a game, pressing the button on the board moves to the next player (and plays the circular wipe). Turn it off if you use the button for something else. The button always fires a `granboard_button` event either way. |
| **Next Dart After A Full Turn Starts The Next Player** | On | If someone throws a 4th dart without anyone pressing Next Player (for example, forgot to pull the darts), that dart starts the next player's turn and counts for them instead of being ignored. Turn it off if you'd rather extra darts be ignored until Next Player is pressed. |
| **Repeat Hit Window (ms)** | 250 | The board often sends the same hit 2 or 3 times for one dart. A hit identical to the previous one that arrives within this many milliseconds is ignored. 0 turns the filter off, and the maximum is 2000. Raise it (300 to 500) if single darts count twice. Lower it if two quick darts in the same bed only count once. |
| **Light The Board On Hits** | On | Drives the board's LED ring during games like the Granboard app: each dart blinks its segment in the thrower's color, awards play effects, and a circular wipe in the next player's color runs between turns. See [section 11](#11-board-lights-during-games). |

### Sounds And Sound Volumes

See [section 8](#8-custom-sounds).

### WLED Sections

See [section 13](#13-wled-sections-lights-around-the-board).

## 8. Custom Sounds

You can play your own MP3 for every hit type, award and game moment on any Home Assistant speaker.

### Step 1: Put Your Sound Files In Home Assistant

**Option A: The `www` folder (simplest)**

1. With the **File editor**, **Samba share** or **Studio Code Server** add-on, create the folder `/config/www/granboard/sounds/`.
2. Copy your MP3s into it, for example `/config/www/granboard/sounds/ton80.mp3`.
3. **If you just created `/config/www` for the first time, restart Home Assistant once** so it starts serving that folder.
4. Files in `/config/www/` are served at `/local/`. So `/config/www/granboard/sounds/ton80.mp3` is entered as:
   ```
   /local/granboard/sounds/ton80.mp3
   ```
   Test it by opening `http://YOUR-HA-ADDRESS:8123/local/granboard/sounds/ton80.mp3` in a browser.

> Files in `www` can be read by anyone who can reach your Home Assistant without logging in. Don't put private files there.

**Option B: The Media folder**

1. Upload the files in **Media > My media** (or copy them to `/media/`, for example `/media/darts/ton80.mp3`).
2. Enter them as a media-source path:
   ```
   media-source://media_source/local/darts/ton80.mp3
   ```

Use simple file names without spaces (for example `triple_20.mp3`). Short clips (under 2 seconds) work best, because a new sound replaces the one playing.

### Step 2: Pick The Speaker And Sounds

Go to **Configure > Sounds**:

- **Speaker**: any `media_player` (Google/Nest, Sonos, an AV receiver, VLC, browser_mod, and so on). If you leave it empty, sounds still fire the `granboard_sound` event (see the tip below).
- One text box per moment. Enter a path in the format above, or leave it empty for no sound.

| Field | When It Plays |
|---|---|
| **Any Hit (Fallback)** | Any scoring dart that has no more specific sound. |
| **Single** / **Double** / **Triple** | A single, double or triple. |
| **Triple 20** | T20 (falls back to Triple, then Any Hit). |
| **Outer Bull** / **Inner Bull (Bullseye)** | 25 / 50. |
| **Miss** | A miss. |
| **Ton (100+)** / **Ton 40** / **High Ton (151+)** / **Ton 80** | Turn totals (x01 and Count-Up). |
| **Hat Trick** | Three bulls in one turn. |
| **Three In A Bed** | Three darts in the same bed. |
| **White Horse** | Three different trebles on Cricket numbers. |
| **Bust** | x01 bust. |
| **Checkout** | x01 finish. |
| **Winner** | Someone wins. |
| **Next Player / Board Clear** | The turn changes (board button, Next Player, or auto next). |
| **Game Start** | A new game starts. |

**One sound plays per dart.** If a dart earns an award, the award sound plays instead of the hit sound. Priority, highest first: Winner, Checkout, Bust, Ton 80, Hat Trick, White Horse, Three In A Bed, High Ton, Ton 40, Ton.

### Step 3 (Optional): Sound Volumes

**Configure > Sound Volumes** has one box per sound, from 0 to 60 %. The integration sets the speaker to that volume just before the sound plays. Leave a box empty to leave the speaker's volume alone. **The integration never sets a volume above 60 %.** It doesn't put the old volume back afterwards, so if you use this with a speaker you also play music on, consider using it only for a dedicated speaker.

**Tip:** every sound also fires a `granboard_sound` event with `sound` (the field name, such as `ton_80`) and `url`. With [browser_mod](https://github.com/thomasloven/hass-browser_mod) you can play it on the dashboard tablet instead of a speaker:

```yaml
automation:
  - alias: Darts Sounds On The Tablet
    triggers:
      - trigger: event
        event_type: granboard_sound
    actions:
      - action: media_player.play_media
        target:
          entity_id: media_player.your_tablet_browser
        data:
          media_content_id: "{{ trigger.event.data.url }}"
          media_content_type: music
```

## 9. Using The Official Granboard App (Kill Switch)

Because the board only takes one connection:

1. Turn **Granboard Connection** off, or press **Release Board**. Home Assistant disconnects at once and makes **no** connection attempts (no retries, no reconnecting when the board advertises), so the board is free.
2. Open the Granboard app and connect as usual.
3. When you're done, **close the app completely**, then turn **Granboard Connection** back on. Home Assistant reconnects within a few seconds.

The switch state is saved, so a released board stays released across Home Assistant restarts. Deleting or disabling the integration also releases the board.

## 10. Playing Games (Actions)

Everything is done with actions (formerly called services), which you can call from dashboard buttons, scripts or automations. Test them in **Developer Tools > Actions**. Every action takes an optional `device_id` if you have more than one board; with one board, leave it out.

### Start A Game: `granboard.new_game`

| Field | Values | Default |
|---|---|---|
| `game` | `x01`, `cricket`, `count_up`, `around_the_clock` (or simply `301`, `501`, `701`) | required |
| `start` | x01 starting score: `301`, `501` or `701` | `501` |
| `double_out` | x01 must finish on a double or the bullseye | `false` |
| `rounds` | Round limit, 0 to 99. Count-Up defaults to 8; 0 means no limit for the others. | |
| `players` | List of names, in throwing order | `["Player 1"]` |
| `colors` | One color per player, in order: names (`red`, `blue`, `green`, `yellow`, `purple`, `orange`, `cyan`, `pink`, `white`, `teal`, `lime`, `gold`), hex (`"#ff8800"`), or `[r, g, b]`. Players without one get the default palette: red, blue, green, yellow, purple, orange, cyan, pink. | |

**501, double out, two players:**

```yaml
action: granboard.new_game
data:
  game: x01
  start: 501
  double_out: true
  players: [Andy, Sam]
  colors: [red, blue]
```

**301, straight out, custom hex colors:**

```yaml
action: granboard.new_game
data:
  game: "301"
  players: [Alex, Jordan, Casey]
  colors: ["#ff0000", "#00ff00", "#8000ff"]
```

**Cricket:**

```yaml
action: granboard.new_game
data:
  game: cricket
  players: [Andy, Sam]
```

**Count-Up (10 rounds):**

```yaml
action: granboard.new_game
data:
  game: count_up
  rounds: 10
  players: [Andy]
```

**Around The Clock:**

```yaml
action: granboard.new_game
data:
  game: around_the_clock
  players: [Andy, Sam]
```

### During The Game

| Action | What It Does |
|---|---|
| `granboard.next_player` | Ends the turn and moves to the next player, even with darts left (same as the board button). |
| `granboard.undo` | Takes back the last dart or turn change. Can be repeated. |
| `granboard.end_game` (**Clear Game**) | Clears the current or finished game back to a blank board. `undo` brings it back if you tapped it by mistake. |
| `granboard.throw` | Scores a dart without the board, for testing a dashboard: `segment` such as `T20`, `D16`, `S5`, `SB`, `DB`, `MISS`. |

```yaml
action: granboard.throw
data:
  segment: T20
```

### Rules In Short

- A turn is three darts. After the third dart (or a bust or a win), the next dart starts the next player when **Next Dart After A Full Turn Starts The Next Player** is on; otherwise it's ignored until Next Player.
- **x01:** going below zero, or with Double Out finishing on a non-double or leaving 1, is a bust, and the score goes back to the start of the turn. The bullseye counts as a double. A checkout suggestion is shown for 170 and under.
- **Cricket:** 15 to 20 and bull. Treble = 3 marks, bullseye = 2. Extra marks score while an opponent still has the number open. You win with everything closed and at least as many points as everyone else.
- **Count-Up:** highest total after the round limit.
- **Around The Clock:** 1 to 20, then bull. Any bed of the target number counts.

### Your Own Board Light Effects: `granboard.led`

Plays a one-off effect on the board's LED ring (only while connected). `color` defaults to the current player's color.

| `effect` | Uses |
|---|---|
| `segment` | `segment` (for example `T20`), `blinks` 1 to 3, `color`, `duration` |
| `blink` | Whole ring flashes once: `color`, `duration` |
| `wave` | Two-color wave: `color`, `color2` (default white), `duration` (speed) |
| `ring` | Whole ring stays lit in `color` |
| `numbers` | Keeps the listed `numbers` (1 to 20) lit in orange |
| `clear` | Turns the ring off |
| `sweep` | Each number in turn from `color` to `color2` (default green), then a flash |
| `wipe` | The between-turns circular wipe in `color` |
| `award` | Preview an award effect: `award` such as `ton_80`, `hat_trick`, `bust`, `winner`, `checkout` (with `segment`) |

```yaml
action: granboard.led
data:
  effect: wave
  color: red
  color2: "#0000ff"
```

## 11. Board Lights During Games

With **Light The Board On Hits** on:

- Each dart blinks its segment in the thrower's color: once for a single, twice for a double, three times for a triple. Triple 20 adds a wave, the outer bull flashes the ring, and the bullseye plays a red wave and flash.
- Awards have their own effects: Bullseye, Bust, Ton / Ton 40 / High Ton, Ton 80, Hat Trick, Three In A Bed, White Horse, Checkout and Winner.
- A circular wipe in the next player's color runs when the turn changes, like the app does when the darts are pulled.
- A new game plays a sweep around the ring.

Commands are queued at least 60 ms apart, a new dart replaces effects still waiting, and nothing is sent while the board is released or offline. A light command that fails never affects reading hits.

## 12. LED Ring Light (Between Games)

**LED Ring** (`light.<board>_led_ring`) lets you use the board's ring like a WLED light when no game is playing. Turn it on and pick a color, brightness and effect from the light's more-info dialog or a dashboard.

### Effects

| Effect | What It Does |
|---|---|
| **Solid** | Whole ring in one color. |
| **Blink** | Whole ring flashes steadily. |
| **Breathe** | Whole ring steps dimmer and brighter. Intensity = how deep. |
| **Heartbeat** | Double flash, pause. |
| **Wave** | The board's wave in your color and **Ring Color 2**, or pairs of palette colors. |
| **Color Cycle** | Whole ring glides along the palette (rainbow by default). |
| **Palette Steps** | Whole ring steps through palette colors, a few seconds each. Intensity = how many colors. |
| **Chase** | One number at a time goes around the ring. |
| **Rainbow Chase** | Chase in rainbow colors (or the palette). |
| **Bounce** | One number goes round and back (scanner). |
| **Circular Wipe** | Numbers light one by one around the ring, then it clears. |
| **Twinkle** | Random numbers blink. Intensity = how many. |
| **Fire Flicker** | Whole ring flickers in fire colors. Intensity = how much it dims. |
| **Police** | Whole ring flashes red, then blue. |
| **Lightning** | Random strikes in your color. Intensity = how often. |

### Settings

- **Ring Palette**: 64 WLED-style palettes, including Default, Color 1, Colors 1&2, Color Gradient, Rainbow, Rainbow Bands, Party, Ocean, Forest, Lava, Heat, Sunset, Pastel, Beach, Fire, Ice, Aurora, Tiamat, Sakura, Temperature, Candy and more (the full list is in the README). **Default** lets each effect use its own colors. Any other palette colors Color Cycle, Palette Steps, Wave, Chase, Rainbow Chase, Bounce, Circular Wipe, Twinkle and Fire Flicker. Very dark palettes (for example Semi Blue) look mostly off on the ring.
- **Ring Speed** (0 to 255, default 128): higher is faster, up to 4 times; lower is slower, down to 4 times.
- **Ring Intensity** (0 to 255, default 128): depth or density, as described in the table.
- **Ring Color 2** (`#RRGGBB`): the second color for Wave and the Colors 1&2 / Color Gradient palettes. Leave it empty to use the opposite of the light's color.

The light's on/off, color, brightness and effect, and all four settings, are restored after a restart.

### How It Works With Games

- **When a game starts**, the light steps aside. It stays "on" but shows `paused_for_game: true`, and the game lights run. If **Light The Board On Hits** is off, the ring is cleared for the game.
- **When the game ends or is cleared**, the light comes back once the last game effect has finished.
- **A dart outside a game** plays its normal hit flash, then the light comes back.
- **When the board reconnects**, the light is put back if it was on. Nothing is sent while the board is released or offline.

### Limits (To Protect The Board)

- Effects only use light commands that the community has documented and tested. Nothing experimental is sent.
- **At most 4 commands a second** (250 ms or more apart). Ring Speed can't go faster than that. A whole-ring color that hasn't changed isn't sent again.
- **No still per-number colors.** With the known commands the board can't hold different numbers in different colors (number blinks turn themselves off), so a palette shows up over time or as moving numbers, not as a still rainbow around the ring.
- Brightness is applied by dimming the color, because the board has no brightness setting.

## 13. WLED Sections (Lights Around The Board)

If you have several lights around the board (WLED strips, bulbs, or any Home Assistant light), the integration can make them react **where the dart lands**: the lights nearest the number glow in the player's color, with neighbouring lights getting a softer glow so it feels like one continuous light. Awards and turn changes send a light **sweeping round the board** from one light to the next.

### Set It Up

1. Go to **Settings > Devices & Services > Granboard > Configure > WLED Sections**.
2. Choose **Add A Light**:
   - **Light**: pick the light. Any light works; WLED lights are smoother (see below).
   - **Position**: where it sits around the board as you face it: **Top (20)**, **Top Right (18 / 4)**, **Right (6)**, **Bottom Right (15 / 2)**, **Bottom (3)**, **Bottom Left (7 / 16)**, **Left (11)**, **Top Left (9 / 12)**, or **Custom Angle**.
   - **Custom Angle (Degrees)**: only used with Custom Angle. 0 is the top (the 20), then clockwise: 90 is the 6, 180 is the 3, 270 is the 11. Each number is 18° apart.
   - **Spread (Degrees)**: how far either side of its position the light reacts. Leave 0 for automatic (360° shared evenly between the lights that are on). Use a bigger number for a long strip, a smaller one for a spot.
3. Repeat for each light. **Edit A Light** moves one, and **Remove Lights** takes lights out.
4. Optional, under **Settings**:

| Option | Default | What It Does |
|---|---|---|
| **Enable WLED Sections** | On | Master switch. It does nothing until at least one light is added. |
| **Hit Flash Length** | 700 ms | How long a hit lights the nearest lights before they go back (200 to 5000 ms). |
| **Only Use Lights That Are Already On** | On | Lights that are off are never touched. If you switch this off, a light that was off is lit for the effect and then turned back off. |

```
                      Top (20)  0°
      Top Left (9 / 12)            Top Right (18 / 4)
            315°                          45°

   Left (11)  270°          ●          90°  Right (6)

            225°                          135°
     Bottom Left (7 / 16)          Bottom Right (15 / 2)
                     Bottom (3)  180°
```

Numbers clockwise from the top, with their angles: 20 (0°), 1 (18°), 18 (36°), 4 (54°), 13 (72°), 6 (90°), 10 (108°), 15 (126°), 2 (144°), 17 (162°), 3 (180°), 19 (198°), 7 (216°), 16 (234°), 8 (252°), 11 (270°), 14 (288°), 9 (306°), 12 (324°), 5 (342°).

**Example:** two strips on the sides of the cabinet and one above the board. Add the top light as **Top (20)**, the left strip as **Left (11)** and the right strip as **Right (6)**. A dart in the 20 lights the top light; a T6 lights the right strip; a dart in the 13 (72°) lights the right strip fully and the top light softly. A Ton 80 sends the light round top → right → left, twice.


### What The Lights Do

| Moment | Lights |
|---|---|
| A single, double or triple | The light(s) nearest that number glow in the player's color; neighbours glow softer. |
| Outer Bull / Bullseye | Every light pulses (twice for the bullseye). |
| Ton, Ton 40, High Ton | One sweep round the lights in the player's color. |
| Ton 80, Hat Trick | Two sweeps. |
| Bust | One red sweep. |
| Checkout / Winner | Two rainbow sweeps. |
| Turn change | One sweep in the next player's color. |

A sweep goes round the board in order (clockwise from the top). Each light comes on as the previous one fades back, so it looks like one light travelling round. A new dart interrupts a running sweep straight away.

### Every Light Goes Back Exactly As It Was

- Before an effect, the integration remembers each light's state. Afterwards, it puts every light back (on or off, brightness, color, and the WLED effect, palette and segments).
- If one effect interrupts another, the lights still go back to how they were *before the first one*.
- **WLED lights** (from Home Assistant's WLED integration) are driven through WLED's own JSON API on your network, using WLED transitions, so animations are smooth. Their exact WLED state is saved and restored, without reloading presets. A WLED segment light only changes its own segment.
- Other lights use `light.turn_on` with a transition, and are restored from their saved Home Assistant state.
- Nothing polls: state is read once when an effect starts.

**Tip:** if you already have your own automations that flash WLED on `granboard_hit`, turn them off when you use WLED Sections, or both will fight over the lights.

## 14. WLED And Room Lights Automations

The integration fires events you can use in automations:

| Event | Useful Data |
|---|---|
| `granboard_hit` | `segment` (`T20`...), `number`, `multiplier`, `score`, `ring` (`single_inner`, `single_outer`, `double`, `treble`, `bull`, `bullseye`, `miss`, `unknown`), and during a game `player`, `player_index`, `color` (`#rrggbb` of the thrower) |
| `granboard_award` | `type` (`bullseye`, `ton`, `ton_40`, `high_ton`, `ton_80`, `hat_trick`, `three_in_a_bed`, `white_horse`, `bust`, `checkout`, `winner`), `player`, `color`, plus `score` / `segment` where they apply |
| `granboard_turn` | `player`, `player_index`, `color`, `round` when the turn changes |
| `granboard_button` | The board button was pressed |

For lights placed around the board, [WLED Sections](#13-wled-sections-lights-around-the-board) does this without any automations. For anything else, use the events. In the examples below, replace `light.your_wled` with your own light. They only act on lights that are **already on**, and they put the light back the way it was using a scene snapshot.

**Flash the thrower's color on every hit, then restore:**

```yaml
automation:
  - alias: Darts Hit Flash
    mode: single
    max_exceeded: silent        # ignore darts that land during a flash
    triggers:
      - trigger: event
        event_type: granboard_hit
    conditions:
      - condition: state
        entity_id: light.your_wled
        state: "on"
      - condition: template
        value_template: "{{ trigger.event.data.ring not in ['miss', 'unknown'] }}"
    actions:
      - action: scene.create
        data:
          scene_id: darts_before_flash
          snapshot_entities: [light.your_wled]
      - variables:
          hex: "{{ (trigger.event.data.color | default('#ffffff')).lstrip('#') }}"
      - action: light.turn_on
        target:
          entity_id: light.your_wled
        data:
          rgb_color: "{{ [hex[0:2] | int(base=16), hex[2:4] | int(base=16), hex[4:6] | int(base=16)] }}"
          brightness_pct: 100
          transition: 0
      - delay: "00:00:01"
      - action: scene.turn_on
        target:
          entity_id: scene.darts_before_flash
```

**Bigger effect for awards (WLED effect name, then restore):**

```yaml
automation:
  - alias: Darts Award Effect
    mode: restart
    triggers:
      - trigger: event
        event_type: granboard_award
    conditions:
      - condition: state
        entity_id: light.your_wled
        state: "on"
      - condition: template
        value_template: "{{ trigger.event.data.type in ['ton_80', 'hat_trick', 'winner', 'checkout', 'bullseye'] }}"
    actions:
      - action: scene.create
        data:
          scene_id: darts_before_award
          snapshot_entities: [light.your_wled]
      - action: light.turn_on
        target:
          entity_id: light.your_wled
        data:
          effect: "{{ 'Fireworks' if trigger.event.data.type in ['winner', 'checkout'] else 'Rainbow' }}"
      - delay: "00:00:04"
      - action: scene.turn_on
        target:
          entity_id: scene.darts_before_award
```

(WLED effect names come from the light's effect list; check yours in the light's more-info dialog.)

**Room light follows whose turn it is:**

```yaml
automation:
  - alias: Darts Turn Color
    triggers:
      - trigger: event
        event_type: granboard_turn
    conditions:
      - condition: state
        entity_id: light.your_wled
        state: "on"
    actions:
      - variables:
          hex: "{{ trigger.event.data.color.lstrip('#') }}"
      - action: light.turn_on
        target:
          entity_id: light.your_wled
        data:
          rgb_color: "{{ [hex[0:2] | int(base=16), hex[2:4] | int(base=16), hex[4:6] | int(base=16)] }}"
```

## 15. Dashboard Examples

Replace `<board>` with your device's ID part (for example `granboard_5547`).

### Simple Scoreboard (Built-In Cards Only)

```yaml
type: vertical-stack
cards:
  - type: markdown
    title: Darts
    content: |
      {% set g = states.sensor.<board>_game %}
      {% if g.state == 'idle' %}No game. Start one below.
      {% else %}
      **{{ g.attributes.game | replace('_', ' ') | title }}**, round {{ g.attributes.round }}
      {% for p in g.attributes.players %}
      {{ '▶' if loop.index0 == g.attributes.current_player else '  ' }} <font color="{{ p.color }}">**{{ p.name }}**</font>: {{ p.score }}
      {% endfor %}
      Darts left: {{ g.attributes.darts_left }}
      {% if g.attributes.checkout %} · Checkout: {{ g.attributes.checkout | join(' ') }}{% endif %}
      {% if g.attributes.winner is not none %}🏆 Winner!{% endif %}
      {% endif %}
  - type: grid
    columns: 4
    square: false
    cards:
      - type: button
        name: New 501
        icon: mdi:numeric-5-circle
        tap_action:
          action: perform-action
          perform_action: granboard.new_game
          data: {game: x01, start: 501, players: [Player 1, Player 2], colors: [red, blue]}
      - type: button
        name: Next Player
        icon: mdi:account-arrow-right
        tap_action:
          action: perform-action
          perform_action: granboard.next_player
      - type: button
        name: Undo
        icon: mdi:undo
        tap_action:
          action: perform-action
          perform_action: granboard.undo
      - type: button
        name: Clear Game
        icon: mdi:broom
        tap_action:
          action: perform-action
          perform_action: granboard.end_game
          confirmation:
            text: Clear the current game?
  - type: entities
    entities:
      - entity: binary_sensor.<board>_connected
        name: Connected
      - entity: sensor.<board>_last_hit
        name: Last Hit
      - entity: switch.<board>_granboard_connection
        name: Granboard Connection
```

### LED Ring Controls (Built-In Cards Only)

```yaml
type: vertical-stack
cards:
  - type: tile
    entity: light.<board>_led_ring
    name: LED Ring
    features:
      - type: light-brightness
  - type: entities
    entities:
      - entity: select.<board>_ring_palette
        name: Ring Palette
      - entity: number.<board>_ring_speed
        name: Ring Speed
      - entity: number.<board>_ring_intensity
        name: Ring Intensity
      - entity: text.<board>_ring_color_2
        name: Ring Color 2
```

Tap the LED Ring tile to open its color wheel and **Effect** list.

### Fancier Cards

If you use [button-card](https://github.com/custom-cards/button-card) and [card-mod](https://github.com/thomasloven/lovelace-card-mod), you can build big effect buttons that call `light.turn_on` with `effect: Chase` (and so on), and a swipeable row of palette buttons that call `select.select_option` on the Ring Palette. Example effect button:

```yaml
type: custom:button-card
entity: light.<board>_led_ring
name: Fire Flicker
icon: mdi:fire
show_state: false
tap_action:
  action: perform-action
  perform_action: light.turn_on
  target:
    entity_id: light.<board>_led_ring
  data:
    effect: Fire Flicker
styles:
  card:
    - height: 84px
    - border-radius: 18px
    - border: "[[[ return entity.attributes.effect === 'Fire Flicker' ? '2px solid var(--primary-color)' : 'none' ]]]"
```

## 16. Updating

**HACS:**

1. HACS shows an update for **Granboard** (also under **Settings > Updates**).
2. Open it and click **Update** (or **Download** and pick the newest version).
3. **Restart Home Assistant.** Updates don't take effect until you restart.
4. Read the [CHANGELOG](../CHANGELOG.md) for new options. Your settings, sounds and game are kept.

**Manual:** replace `/config/custom_components/granboard` with the new folder and restart.

## 17. Troubleshooting

### Some Hits Aren't Counted

- **Soft finger presses**: pressing a bed lightly with a finger often doesn't close the board's sensor, so the board never sends anything. Real darts (or a firm press) are much more reliable. Test with darts.
- **Range**: put an ESPHome Bluetooth proxy within 1 to 2 metres of the board ([section 2](#2-set-up-bluetooth-adapter-or-esphome-proxy)). Missed hits and disconnects often go away.
- **Same bed twice, fast**: two quick darts in the same bed within the **Repeat Hit Window** (default 250 ms) count once. Lower the window if that happens often.
- **Single darts counting twice**: raise the **Repeat Hit Window** to 300 to 500 ms.
- **Darts after the 3rd**: if **Next Dart After A Full Turn Starts The Next Player** is off, darts after the third are ignored until Next Player.
- **Right after connecting**: hits in the first ~2 seconds are ignored on purpose.

### The Board Doesn't Connect

- Close the Granboard app on **all** devices (it can hold the connection in the background).
- Check **Granboard Connection** is on.
- Make sure your adapter or proxy is *active* / connectable (`active: true` on an ESPHome proxy).
- Power-cycle the board. While it's flashing red, it's waiting for a connection.
- Check **Settings > System > Logs** for `Granboard ... not connected:` messages. "not visible to any connectable Bluetooth adapter or proxy" means it's out of range or only seen by passive scanners.

### It Keeps Disconnecting

- Usually range or Wi-Fi on the proxy. Move the proxy closer, improve its Wi-Fi, or use an Ethernet proxy.
- Avoid having several Bluetooth-heavy devices on the same proxy.
- The integration reconnects by itself. The **Connected** sensor shows when.

### The Board's LEDs Don't Light

- **Light The Board On Hits** must be on (**Configure > General**) for game lights.
- The board must be connected. Nothing is sent while it's released or offline.
- Try `granboard.led` with `effect: blink`, `color: red` in **Developer Tools > Actions**. If nothing lights, turn on debug logging and look for `LED write failed`.
- If the LED Ring light seems stuck, check its `paused_for_game` attribute. A game in progress takes over the ring; clear the game to get the light back.

### No Sound

- Open the file URL in a browser (`http://YOUR-HA:8123/local/granboard/sounds/file.mp3`). If it doesn't load, check the folder and file name, and restart after creating `/config/www` for the first time.
- Check the **Speaker** is chosen in **Configure > Sounds** and it can play MP3s (test with **Media > Browse media**).
- Some speakers (for example Google/Nest) need Home Assistant's **external or internal URL** set correctly in **Settings > System > Network** to load `/local/` files.

### "Unknown Frame" Warnings

The log says `Granboard ... sent unknown frame '...'` when the board sends a code the integration doesn't recognise. The dart is reported as `segment: unknown` and not scored. Note which bed you hit and [open an issue](https://github.com/afcragg78/ha-granboard/issues) with the warning line, so it can be added to the map.

### Turn On Debug Logging

Add this to `configuration.yaml` and restart (or use **Settings > Devices & Services > Granboard > ⋮ > Enable debug logging**, reproduce the problem, then disable it to download the log):

```yaml
logger:
  default: warning
  logs:
    custom_components.granboard: debug
```

This logs every raw frame from the board, every Bluetooth characteristic found when connecting, and LED write problems. Remove it when you're done, because it's chatty.

## 18. Uninstalling

1. **Settings > Devices & Services > Granboard > ⋮ > Delete**. This disconnects and releases the board right away.
2. In **HACS**, open **Granboard > ⋮ > Remove**. For a manual install, delete `/config/custom_components/granboard`.
3. **Restart Home Assistant.**
4. Optional clean-up:
   - Delete your sound files in `/config/www/granboard/` or `/media/`.
   - Remove dashboard cards, scripts and automations that use `granboard.*` actions or `granboard_*` events.
   - Remove the `custom_components.granboard` line from `logger:` if you added it.
   - To remove the custom repository too: **HACS > ⋮ > Custom repositories >** delete the entry.
