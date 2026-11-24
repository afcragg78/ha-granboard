<p align="center">
  <img src="images/logo.png" alt="Granboard for Home Assistant" width="200">
</p>

<h1 align="center">Granboard for Home Assistant</h1>

<p align="center">
  <b>Turn your Granboard 3 into a fully connected smart dartboard.</b><br>
  Live hits over Bluetooth, games scored inside Home Assistant, board lighting, WLED effects, and custom sounds.
</p>

<p align="center">
  <a href="https://hacs.xyz"><img src="https://img.shields.io/badge/HACS-Custom-41BDF5.svg" alt="HACS Custom"></a>
  <a href="https://github.com/afcragg78/ha-granboard/releases"><img src="https://img.shields.io/github/v/release/afcragg78/ha-granboard" alt="Latest release"></a>
  <img src="https://img.shields.io/badge/Home%20Assistant-2025.1%2B-18BCF2.svg" alt="Home Assistant 2025.1+">
</p>

<p align="center">
  <b>📖 <a href="docs/INSTALL.md">Complete Setup Guide</a></b> · <a href="#quick-start">Quick Start</a> · <a href="CHANGELOG.md">Changelog</a>
</p>

---

Home Assistant custom integration for the **Granboard 3** Bluetooth dartboard. It connects through Home Assistant's Bluetooth integration (a USB adapter or an ESPHome Bluetooth proxy), turns every dart into an event, and runs the game (x01, Cricket, Count-Up, Around The Clock) inside Home Assistant, so a dashboard only has to display it.

## Features

- **Live Hits** – every dart becomes a Home Assistant event and sensor update, with segment, score, and ring.
- **Games Built In** – x01 (with double out), Cricket, Count-Up, and Around The Clock, with undo, next player, and clear game.
- **Player Profiles** – save friends with a name, colour, initials and optional avatar, pick a lineup (Guest is a one-night slot), and track career stats (3-dart average, first-9, checkout %, 180s, Cricket MPR, a heat map and more).
- **Player Colors** – each player gets a sharp, fully saturated color on the board and on your lights.
- **Board Lighting** – hit flashes, award effects (Bullseye, Ton 80, Hat Trick and more), and the circular wipe between turns, like the official app.
- **LED Ring Light** – use the board's ring as a light between games, with 17 effects (including the board's own Rainbow Sweep) and 64 WLED-style palettes.
- **WLED Sections** – add lights placed around the board in Configure: the lights nearest each dart glow in the player's color, and awards and turn changes sweep round them, then every light goes back exactly as it was.
- **WLED And Lights** – fire automations from hits, turns, and awards to light up the room.
- **Custom Sounds** – pick your own MP3 for each hit, award, and game event in Configure.
- **App Kill Switch** – release the board with one tap so the official Granboard app can connect.
- **Darts Arena Card** – a ready-made panel dashboard for live scoring, the dartboard, New Game, ring controls and optional room lights. See [Darts Arena Card](#darts-arena-card).

**This project is unofficial and is not affiliated with, endorsed by, or supported by Granboard / GRAN Darts.** The Bluetooth protocol is community reverse-engineered.

## Contents

- [Features](#features)
- [Installation](#installation)
- [Darts Arena Card](#darts-arena-card)
- [Using The Phone App Instead](#using-the-phone-app-instead)
- [Entities](#entities)
- [Player Profiles](#player-profiles)
- [Events](#events)
- [Services](#services)
- [Board Lights](#board-lights)
- [LED Ring Light](#led-ring-light)
- [WLED Sections](#wled-sections)
- [Sounds](#sounds)
- [Protocol](#protocol)
- [Credits](#credits)
- [Development](#development)
- [Complete Setup Guide](docs/INSTALL.md)

## Installation

> 📖 **New to this? Read the [Complete Setup Guide](docs/INSTALL.md).** It covers Bluetooth proxies, HACS, every Configure option, sounds, games, the LED Ring light, WLED automations, dashboards, troubleshooting and uninstalling, step by step.

### Quick Start

1. **Bluetooth:** Home Assistant needs a connectable Bluetooth adapter, or better, an [ESPHome Bluetooth proxy](docs/INSTALL.md#2-set-up-bluetooth-adapter-or-esphome-proxy) (`active: true`) close to the board or inside the dart cabinet. Home Assistant 2025.1 or newer.
2. **HACS:** **HACS > ⋮ > Custom repositories**, add `https://github.com/afcragg78/ha-granboard` as type **Integration**, download **Granboard**, then **restart Home Assistant**. (Manual install: copy `custom_components/granboard` to `/config/custom_components/` and restart.)
3. **Close the Granboard phone app** on every device. The board takes one connection at a time. Turn the board on; its light flashes red while it waits.
4. **Add it:** accept the **Discovered: GRANBOARD** card in **Settings > Devices & Services**, or **+ Add Integration > Granboard** and pick or type its Bluetooth address (like `AA:BB:CC:11:22:33`).
5. **Configure** (optional): **Granboard > Configure** for General options, Sounds and Sound Volumes. Under General, **Preferred Bluetooth Adapter** (default Automatic) can pin the board to a specific USB dongle or Bluetooth proxy so it does not connect through a farther radio.
6. **Play:** add friends with `granboard.add_player`, set tonight's lineup, then call `granboard.new_game` (for example `game: x01`, `start: 501`, `players: [Andy, Sam]` — names or profile ids) from a dashboard button and start throwing.

To update: HACS > Granboard > **Update**, then restart Home Assistant.

## Darts Arena Card

The **Darts Arena** card is a single native Lovelace card (`custom:darts-arena-card`) for playing and watching a game. It does not use button-card, card-mod, or other custom Lovelace cards.

![Darts Arena during a game](images/darts-arena/playing.jpg)

### **Install These First**

Do these before you add the card. Items marked *optional* are only for that feature; skip them if you do not use it.

1. **Home Assistant 2025.1 or newer.**
2. **This Granboard integration**, installed from HACS (recommended) or copied manually, with your **Granboard 3 / 3s** added and connected.
3. **Home Assistant Bluetooth** — a USB adapter or an ESPHome Bluetooth proxy (`active: true`). The card will not see hits without the integration's Bluetooth connection.
4. **The card module and a Lovelace resource** — copy `dashboards/darts-arena-card.js` to `/config/www/granboard/darts-arena-card.js`, then add a resource:

   ```yaml
   url: /local/granboard/darts-arena-card.js?v=2c40de96
   type: module
   ```

   After you replace the file, change `?v=` (first eight characters of the file's sha256) or clients may keep the old module.

**Optional, only if you use that feature:**

- **WLED** (the Home Assistant WLED integration) — only for the card's **Room** tab lights. The example dashboard sets `wled: null` and hides those controls.
- **Alexa Media Player** — only if you play board sounds on an Amazon Echo. The card itself does not talk to Alexa.
- **InfluxDB / Grafana** — only for the optional stats dashboards in [docs/INFLUX-GRAFANA.md](docs/INFLUX-GRAFANA.md). The card does not use them.
- **`input_text` / `input_boolean` helpers** — only as a fallback roster if you are not using Granboard player profiles.

**Not required for this card:** button-card, card-mod, browser_mod, config-template-card, or any other custom Lovelace card.

**HACS** is recommended for installing and updating this integration. It is not required if you install manually. HACS does not copy the card JS for you; you still place it in `/config/www/granboard/`.

Full steps, card options, and an example **Panel** dashboard are in [dashboards/README.md](dashboards/README.md) and [dashboards/darts-arena-card.yaml](dashboards/darts-arena-card.yaml). Set `prefix` to the middle of your entity IDs (for example `granboard_5547`). New Game calls `granboard.new_game`.

The glow behind the dartboard **recreates** the LED ring's current effect, palette, colours, speed and intensity from Home Assistant **settings**, and follows player and hit colours during a game. It is **not** a live per-LED readback. Changes made only in the official Granboard app may not appear until Home Assistant has the new settings.

![Rainbow Sweep glow](images/darts-arena/glow-rainbow-sweep.jpg)

## Using The Phone App Instead

**Granboard Connection** is a kill switch. Turn it off (or press **Release Board**) and Home Assistant disconnects at once and makes no connection attempts until you turn it back on, so the official app can connect. The setting is saved and survives Home Assistant restarts.

## Entities

| Entity | What it shows |
|---|---|
| Switch **Granboard Connection** | Kill switch. Off releases the board and stays released. |
| Button **Release Board** | Turns the switch off. |
| Binary sensor **Connected** | The Bluetooth link is up. |
| Sensor **Last Hit** | Segment (`T20`, `D16`, `S5`, `SB`, `DB`, `MISS`), with number, multiplier, score, ring, and raw frame as attributes. |
| Sensor **Last Raw Frame** | The last frame exactly as received (diagnostic). |
| Sensor **Signal Strength** | RSSI from the last advertisement (diagnostic). The board stops advertising while connected, so this updates only while it is not. |
| Light **LED Ring** | The board's LED ring as a light between games (see LED Ring Light below). |
| Select **Ring Palette**, Numbers **Ring Speed** / **Ring Intensity**, Text **Ring Color 2** | LED Ring effect settings (configuration). |
| Select **Sound Theme** | Sound pack folder under `/config/www/granboard/sounds/<theme>/`, or Off to use only the Configure file boxes. The choice is restored after a restart. |
| Sensor **Game** | `idle`, `playing`, or `finished`. The attributes are the whole game (below). They are excluded from the recorder. |
| Sensor **Players** | How many saved profiles you have. Attributes list each profile (id, name, colour, initials, avatar, career stats) and tonight's lineup. Excluded from the recorder. |


## Player Profiles

Save friends with `granboard.add_player` (name, colour, optional initials and avatar path such as `/local/granboard/players/andrew.jpg`). `granboard.update_player` edits a profile; `granboard.remove_player` archives it so past games keep the same player id. Profiles live in `.storage/granboard.players`.

`granboard.set_lineup` sets tonight's throwing order from profile ids or names. **Guest** is a one-night slot and is never saved as a profile. `granboard.new_game` accepts profile ids or names (a plain list of names still works). If you omit `players`, the saved lineup is used.

Career stats per profile are stored in `.storage/granboard.career` and shown on the Players sensor: 3-dart average, first-9 average, checkout %, doubles hit rate, 180s, ton+, Cricket MPR, win rate and games by mode, and a per-segment heat map. On first run, a profile is seeded from `input_text.darts_players` when that helper exists; Guest is left as a lineup slot only.

Ready-to-apply InfluxDB and Grafana files (not installed by this release) are in [docs/INFLUX-GRAFANA.md](docs/INFLUX-GRAFANA.md).

## Events

- `granboard_hit`: `segment`, `number`, `multiplier`, `score`, `ring` (`treble`, `double`, `single_inner`, `single_outer`, `bull`, `bullseye`, `miss`, or `unknown`), `raw`, `address`, `entry_id`. During a game also `player`, `player_index`, `player_id` and `color`. An unknown frame fires with `segment: unknown` and is logged as a warning, so it can be added to the map.
- `granboard_button`: the board button (`raw: BTN@`). During a game it also ends the turn (can be turned off in the integration's options).
- `granboard_award`: `type` is one of `bullseye` (any bull; check `segment` for `SB` / `DB`), `ton` (100–139), `ton_40` (140–150), `high_ton` (151–179), `ton_80` (180), `hat_trick` (three bulls), `three_in_a_bed` (three darts in the same bed), `white_horse` (three different trebles on Cricket numbers), `bust`, `winner`, `checkout`. Also `player`, `player_index`, `player_id`, `color`, and `score` / `segment` where they apply. Ton awards count in x01 and Count-Up only.

- `granboard_turn`: `player`, `player_index`, `player_id`, `color`, `round` when the turn changes, plus the visit that just ended (`last_visit`, and flat `visit_score`, `visit_bust`, `visit_player`, `visit_player_id`).
- `granboard_game_over`: when a game is won or a round limit ends it: `game`, `game_id`, `start`, `double_out`, `winner`, `winner_id`, and `players` (name, id, colour, score, stats). Not re-fired if Home Assistant restarts with a finished game still loaded.
- `granboard_sound`: `sound` (the trigger, e.g. `ton_80`), `url` and `theme` (the Sound Theme, e.g. `funny` or `Off`) whenever a sound plays.
- `granboard_hit` and `granboard_award` carry `player`, `player_id` and `color` (the thrower's `#rrggbb`) during a game.

Use these to drive WLED or anything else from an automation. See [WLED And Room Lights Automations](docs/INSTALL.md#13-wled-and-room-lights-automations) for ready-to-paste examples.

## Services

| Service | Fields |
|---|---|
| `granboard.new_game` | `game`: `x01`, `cricket`, `count_up`, `around_the_clock` (or `301` / `501` / `701`); `start`: 301 / 501 / 701; `double_out`; `rounds` (Count-Up defaults to 8; 0 = no limit); `players`: profile ids or names in throwing order (a plain list of names still works; Guest is a one-night slot; if omitted, the saved lineup is used); `colors`: one per player (names like `red` or hex `#ff8800`). |
| `granboard.undo` | Takes back the last dart or turn change. Can be repeated. |
| `granboard.next_player` | Ends the turn, even with darts left. |
| `granboard.end_game` | **Clear Game**: clears the current or finished game back to a blank board. Undo brings it back. |
| `granboard.throw` | `segment` such as `T20`, `D16`, `SB`, `DB`, `MISS`. Scores a dart without the board, for testing a dashboard. |
| `granboard.add_player` | Save a profile: `name`, optional `color`, `initials`, `avatar`. Guest cannot be saved. |
| `granboard.update_player` | `player_id` plus any of `name`, `color`, `initials`, `avatar`. |
| `granboard.remove_player` | `player_id`. Archives the profile; career stats and past games keep the id. |
| `granboard.set_lineup` | `players`: profile ids or names in throwing order, plus optional `colors` for one-night players. |
| `granboard.led` | One-off board light effect: `segment`, `blink`, `wave`, `ring`, `numbers`, `clear`, `sweep`, `wipe`, `award`, `rainbow` (the board's own rainbow sweep, loops every 2 seconds until `clear` or another effect), or the advanced test effect `raw` (see the [guide](docs/INSTALL.md#your-own-board-light-effects-granboardled)). |

All take an optional `device_id` when you have more than one board.

### Rules

- A turn is three darts. After the third dart, a bust, or a win, the next dart starts the next player (option **Next Dart After A Full Turn Starts The Next Player**, on by default); with it off, further darts are ignored until the next player (board button or `next_player`).
- **x01**: a bust (below zero, or with Double Out finishing on a non-double or leaving 1) puts the score back to the start of the turn. The bullseye counts as a double. A checkout suggestion is shown for 170 and under when one exists with the darts left.
- **Cricket**: 15–20 and bull. A treble is three marks, the bullseye two. Marks past three score while any opponent has the number open. You win with everything closed and at least as many points as everyone else.
- **Count-Up**: highest total after the round limit.
- **Around The Clock**: 1 to 20, then the bull. Any bed of the target number counts.

### Game Sensor Attributes

`game`, `game_id`, `start`, `double_out`, `rounds`, `round`, `current_player`, `current_player_name`, `darts` (this turn), `darts_left`, `turn_score`, `turn_complete`, `bust`, `winner`, `checkout`, `players` (each with `name`, `profile_id`, `score`, Cricket `marks`, Around The Clock `target`, and `stats`: `darts`, `turns`, `ppd`, `ppr`, `best_turn`, Cricket `mpr`), `history` (last 20 turns, including `player_id`), `last_awards`, `can_undo`.

## Board Lights

With **Light The Board On Hits** on (Configure), the integration drives the board's LED ring over Bluetooth like the Granboard app does. Every dart blinks its segment in the thrower's colour, awards play their own effects, and a circular wipe in the next player's colour runs when the turn changes. Use `granboard.led` for your own effects, for example:

```yaml
action: granboard.led
data:
  effect: segment
  segment: T20
  color: "#ff0000"
```

The LED command format comes from the community reference [keenanlk/granboard-ble-codes](https://github.com/keenanlk/granboard-ble-codes), tested there on a GranBoard 3s.

## LED Ring Light

**LED Ring** (`light.<board>_led_ring`, e.g. `light.granboard_5547_led_ring`) turns the board's LED ring into a WLED-style light when no game is playing. Pick a colour, a brightness and an effect.

| Effect | What it does |
|---|---|
| Solid | Whole ring in one colour (one command, then nothing more is sent). |
| Blink / Heartbeat / Lightning | Whole-ring flashes: steady, double beat, random strikes (Intensity = how often). |
| Breathe | Whole ring steps dimmer and brighter (Intensity = how deep). |
| Wave | The board's wave in Color 1 and Color 2, or palette pairs. |
| Color Cycle | Whole ring glides along the palette (rainbow by default). |
| Palette Steps | Whole ring steps through the palette's colours, a few seconds each (Intensity = how many colours). |
| Chase / Rainbow Chase / Bounce | One number at a time goes round (or back and forth) in palette colours. |
| Rainbow Sweep | The board's own built-in rainbow, moving up and down across the ring. One pass takes about 2 seconds; Home Assistant re-sends it so it keeps looping until you change the effect or turn the ring off. Color, brightness, palette, speed and intensity don't apply. |
| Circular Rainbow | The board's own wave animation keeps running round the whole ring while its two colours travel through the rainbow (or the palette). Intensity = how far apart the two colours are. |
| Circular Wipe | Numbers light one by one round the ring, then it clears. |
| Twinkle | Random numbers blink in palette colours (Intensity = how many). |
| Fire Flicker | Whole ring flickers through the Fire palette (Intensity = how much it dims). |
| Police | Whole ring flashes red, then blue. |

Settings next to the light:

- **Ring Palette** (select): Default, Color 1, Colors 1&2, Color Gradient, Rainbow, Rainbow Bands, Party, Cloud, Lava, Ocean, Forest, Heat, Sunset, Rivendell, Breeze, Red & Blue, Yellowout, Analogous, Splash, Pastel, Sunset 2, Beach, Vintage, Departure, Landscape, Sherbet, Hult, Drywet, Jul, Grintage, Rewhi, Tertiary, Fire, Icefire, Ice, Cyane, Light Pink, Autumn, Magenta, Magred, Yelmag, Yelblu, Orange & Teal, Tiamat, April Night, Orangery, C9, Sakura, Aurora, Atlantica, Temperature, Retro Clown, Candy, Toxy Reaf, Fairy Reaf, Semi Blue, Pink Candy, Red Reaf, Aqua Flash, Yelblu Hot, Red Flash, Red Shift, Red Tide, Candy2. Default lets each effect use its own colours; any other palette colours Color Cycle, Palette Steps, Wave, Chase, Rainbow Chase, Circular Rainbow, Bounce, Circular Wipe, Twinkle and Fire Flicker.
- **Ring Speed** (0-255, 128 = normal): faster or slower effects, but never more than 4 commands a second.
- **Ring Intensity** (0-255): depth or density of the effect (see table).
- **Ring Color 2** (text, `#RRGGBB`): second colour for Wave and the Colors 1&2 / Color Gradient palettes. Empty uses the opposite of the light's colour.

How it behaves:

- The board cannot hold different numbers in different colours with a documented command (number blinks turn themselves off, and the number-state command has only one confirmed colour), so a palette is shown over time on the whole ring, or as moving / twinkling numbers, not as a still rainbow around the ring.
- Effects are slow on purpose (250 ms or more between commands) so the board keeps reading darts, and a whole-ring colour that has not changed is not sent again.
- When a game starts the light pauses (`paused_for_game: true`) and the game lights take over. When the game ends or is cleared, the light comes back.
- A dart outside a game flashes as usual, then the light comes back.
- Nothing is sent while the board is released or offline; the light is re-applied when it reconnects.

## WLED Sections

Put several lights around the board (WLED strips, bulbs, any light) and add them in **Configure > WLED Sections > Add A Light** with their **Position** (Top (20), Top Right (18 / 4), Right (6), Bottom Right (15 / 2), Bottom (3), Bottom Left (7 / 16), Left (11), Top Left (9 / 12), or a Custom Angle where 0° is the 20 and angles go clockwise, 18° per number) and an optional **Spread**.

- A dart lights the nearest light(s) in the player's color, with neighbours glowing softer. The bulls pulse every light.
- Ton / Ton 40 / High Ton sweep once round the lights in board order, Ton 80 and Hat Trick twice, a bust sweeps red, and a checkout or winner sweeps a rainbow twice. A turn change sweeps in the next player's color. Each light comes on as the previous one fades back.
- Afterwards every light goes back exactly as it was. WLED lights are driven and restored through WLED's JSON API (state, effect, palette and segments; presets aren't reloaded), and other lights from their saved state. A new dart interrupts a running sweep.
- **Only Use Lights That Are Already On** (default On) means lights that are off are never touched. **Hit Flash Length** (default 700 ms) and **Enable WLED Sections** (default On) are under Settings.

Full setup, a positions diagram and examples are in the [guide](docs/INSTALL.md#13-wled-sections-lights-around-the-board).

## Sounds

**Sound Themes (recommended for several clips):** create `/config/www/granboard/sounds/<theme>/<trigger>/` (File editor, Samba or Studio Code Server) and drop in `.mp3`, `.wav` or `.ogg` files, for example `/config/www/granboard/sounds/funny/ton_80/wow1.mp3`. Trigger folder names are `hit`, `single`, `double`, `triple`, `triple_20`, `outer_bull`, `inner_bull`, `miss`, `cricket_miss`, `ton`, `ton_40`, `high_ton`, `ton_80`, `hat_trick`, `three_in_a_bed`, `white_horse`, `bust`, `checkout`, `winner`, `next_player` and `game_start`. Pick the pack on the **Sound Theme** select (Off, plus every theme folder). A `default` theme is used when the current pack has no clip for that trigger. Restart Home Assistant once after creating the `www` folder for the first time; after that, new folders and files are picked up on the next dart or when you open the dropdown.

**Single files (still supported):** put a file in `/config/www/granboard/sounds/` and enter it in **Configure > Sounds** as `/local/granboard/sounds/ton80.mp3`, or use a `media-source://media_source/local/...` path from Media. These boxes are the fallback when a theme folder is empty. Leave a box empty for no sound at that layer.

1. Open **Settings > Devices & Services > Granboard > Configure > Sounds**.
2. Pick the **Speaker** (any media player). If you leave it empty, sounds still fire the `granboard_sound` event.
3. Optional: **Sound Volumes** sets a volume per sound (0-60 %). Empty leaves the speaker's volume alone. The integration never sets a volume above 60 %.

One sound plays per dart. Award sounds (winner, checkout, bust, ton 80, hat trick, white horse, three in a bed, high ton, ton 40, ton) win over the hit sound; Triple 20 falls back to Triple, then Any Hit. For theme folders the same chain is used at each layer (current theme, then `default`, then the Configure file).
In **Cricket**, hit sounds play only when the dart counts (15-20 or bull that the player still needs, or that can still score because another player has not closed it). A non-counting dart, a closed number, or a miss plays `cricket_miss` (random clip from that folder), then the ordinary `miss` clips if `cricket_miss` is empty.
Every sound also fires `granboard_sound` (`sound`, `url`, `theme`), so a dashboard or browser_mod automation can play it on a tablet instead of a speaker.

**Amazon Echo / Alexa Media Player:** those speakers cannot stream a regular MP3. Playback on an Echo **requires** the [Alexa Media Player](https://github.com/alandtse/alexa_media_player) integration (install from HACS, then set it up in Home Assistant) **and** a public Home Assistant HTTPS URL (Home Assistant Cloud / Nabu Casa is fine). With those in place, when the configured speaker is an Alexa Media Player device, Granboard pre-converts every clip at startup (and when you change Sound Theme) to a 48 kbps, 24 kHz mono MP3, caches it under `/config/www/granboard/sounds/.alexa_cache/`, and plays it as Alexa SSML over that public HTTPS address without waiting on ffmpeg at dart time. Configure > Sounds has **Alexa-Compatible Audio** to force this conversion for other speakers. The original file is used if conversion fails. Amazon's servers still have to fetch the file, so an Echo typically stays around 1-2 seconds; that floor is on Amazon's side and cannot be removed. A local speaker (for example a Home Assistant Voice PE) is quicker: Granboard plays the clip from `http://YOUR-HA:8123/local/...` on the LAN and, if the speaker is wrapped by Music Assistant, uses the underlying media player so the clip does not sit in a queue.

## Protocol

Service `442f1570-8a00-9a28-cbe1-e1d4212d53eb`. Hits arrive on a notify characteristic (normally `442f1571-…`) as ASCII such as `3.4@` (treble 20). The integration picks the notify and write characteristics on that service when it connects and logs every characteristic at debug level. Frames for about 2 seconds after connecting are ignored because the board can replay the last hit. LED commands go to the write characteristic (normally `442f1572-…`).

To log every raw frame:

```yaml
logger:
  logs:
    custom_components.granboard: debug
```

## Credits

- [keenanlk/granboard-ble-codes](https://github.com/keenanlk/granboard-ble-codes): hit codes and LED commands
- [Dennis-Otto/homedarts-for-autodarts](https://github.com/Dennis-Otto/homedarts-for-autodarts), [sobassy/gran-app](https://github.com/sobassy/gran-app), [bastiennoel93/granboard-app](https://github.com/bastiennoel93/granboard-app): frame mapping cross-checks

## Development

```bash
pytest                                     # pure decoding / game tests, no Home Assistant needed
pytest tests_ha -o asyncio_mode=auto       # needs pytest-homeassistant-custom-component
```
