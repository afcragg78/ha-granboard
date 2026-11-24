# Changelog

## 0.5.0

- **Darts Arena card**: a native custom Lovelace card (`custom:darts-arena-card`) for live scoring, the dartboard, New Game, undo / next / end game, LED ring controls, optional Room WLED lights, sound theme, and board settings. It replaces earlier button-card dashboard templates. The module lives in `dashboards/darts-arena-card.js`; copy it to `/config/www/granboard/` and add a Lovelace resource `/local/granboard/darts-arena-card.js?v=2c40de96` (type module). Example panel dashboard: `dashboards/darts-arena-card.yaml`. Setup: [dashboards/README.md](dashboards/README.md).
- The glow behind the dartboard recreates the LED ring's current effect, palette, colours, speed and intensity from Home Assistant settings, and follows player and hit colours during a game. It is not a live per-LED readback.
- The card does not require button-card, card-mod, or other custom Lovelace cards. WLED, Alexa Media Player, and InfluxDB/Grafana stay optional (see **Install These First** in the card docs and the README).


## 0.4.0

- **Player profiles**: save friends with a stable id, name, colour, initials and an optional avatar. New services `granboard.add_player`, `granboard.update_player` and `granboard.remove_player` (archives the profile so past games keep their id). A `granboard.set_lineup` service sets tonight's throwing order from profile ids or names; **Guest** is a one-night slot and is never saved. `granboard.new_game` accepts profile ids or names, and still accepts a plain list of names. If you omit `players`, the saved lineup is used.
- New **Players** sensor (`sensor.<board>_players`) with the profile list, lineup and career stats as attributes (excluded from the Recorder, like the Game sensor).
- **Career stats** per profile, stored in `.storage/granboard.career`: 3-dart average, first-9 average, checkout %, doubles hit rate, 180s, ton+, Cricket MPR, win rate and games by mode, and a per-segment heat map. A rolling log of throws (8,000) and games (400) is kept; cumulative totals are not lost when the log is trimmed. Undoing a finish rolls that game back out of the totals.
- Events: `granboard_hit`, `granboard_award` and `granboard_turn` now include `player_id`. New `granboard_game_over` event (mode, winner, winner id, final scores). `granboard_turn` also has the visit that just ended (`visit_score`, `visit_player_id`, ...).
- On first run, a profile is seeded from `input_text.darts_players` when that helper exists (for example **Andrew**). **Guest** is left as a one-night lineup slot and is not saved.


## 0.3.1

- Configure > General has a **Preferred Bluetooth Adapter** option. Automatic (the default) leaves the radio choice to Home Assistant, the same as before. Pick a specific connectable adapter or proxy, such as a USB dongle or an ESPHome Bluetooth proxy near the board, to always connect through that radio. If the chosen adapter cannot see the board, the connection fails with a clear error instead of silently using another scanner (for example a farther proxy in another room). Advertisement-wake reconnects also honor the choice. The Granboard Connection switch and Release Board still disconnect immediately and stop all retries.

## 0.3.0

- **Alexa-compatible audio**: Amazon Echo speakers cannot play a normal `media_player.play_media` stream ("Direct music streaming isn't supported"). Echo playback **requires** the [Alexa Media Player](https://github.com/alandtse/alexa_media_player) integration (HACS, then set up in Home Assistant) **and** a public Home Assistant HTTPS URL (Home Assistant Cloud / Nabu Casa is fine). When the configured speaker is an Alexa Media Player, Granboard now converts the chosen clip with Home Assistant's ffmpeg to a 48 kbps, 24 kHz mono MP3 no longer than 240 seconds, caches it under `/config/www/granboard/sounds/.alexa_cache/`, and plays it with `notify.alexa_media` as SSML `<audio src="..."/>` (`type: tts`) using that public HTTPS URL from `get_url(..., prefer_external=True)`. The 60 % volume cap still applies. The cache is skipped by Sound Theme discovery. If conversion or the public URL fails, the original file is played and a warning is logged.
- New Configure > Sounds option **Alexa-Compatible Audio** (off by default) forces the same conversion for a non-Alexa speaker. Alexa Media Player speakers always use it.


## 0.2.9

- **Sound Themes**: drop a folder of clips per trigger and switch packs from the new **Sound Theme** select (`select.<board>_sound_theme`). Put files in `/config/www/granboard/sounds/<theme>/<trigger>/` as `.mp3`, `.wav` or `.ogg`, for example `/config/www/granboard/sounds/funny/ton_80/wow1.mp3`. The dropdown lists **Off** plus every theme folder it finds. It rescans when Home Assistant starts, when the dropdown is opened, and on each play, so a new folder or file is picked up without a restart (except the first time you create `/config/www`). The chosen theme is restored after a restart.
- On each dart the integration picks a random clip from the current theme's trigger folder. If that folder is empty it tries `default/<trigger>/`, then the existing single-file box in Configure > Sounds, then the next key in the usual chain (for example Triple 20 → Triple → Any Hit) at each of those layers. **Off** uses only the Configure file boxes, as before.
- Award priority, "one sound per dart" and the 60 % volume cap are unchanged. The `granboard_sound` event now includes `theme` as well as `sound` and `url`.


## 0.2.8

- Rainbow Sweep (and `granboard.led` with `effect: rainbow`) now loops. The board only plays one up-and-down pass (about 2 seconds), so the integration re-sends the native `0x10` command every 2 seconds while the effect is active. The repeat stops immediately if you change the effect, turn the ring off, send `clear` or another LED command, unload the integration, or the board disconnects, and it comes back on reconnect if it was still on. A tick is skipped if a write is already in progress, so commands never stack.

## 0.2.7

- New LED Ring effect **Rainbow Sweep**: the board's own firmware rainbow, moving up and down across the ring. It's a single command (`0x10`, now confirmed on a real Granboard 3s; the other bytes are ignored), and the board animates it smoothly by itself until something else is shown. It's only sent again when the light resumes after a game or reconnect. Color, brightness, Ring Palette, Ring Speed, Ring Intensity and Ring Color 2 don't apply to it.
- `granboard.led` has a new `rainbow` effect that starts the same native rainbow. It keeps running until `effect: clear`; the LED Ring light pauses meanwhile. The advanced `raw` test effect stays.

## 0.2.6

- Advanced / test: `granboard.led` has a new `raw` effect with a **Raw Frame (Advanced Test)** field, to send one hand-made frame to the board, for example to try the community "rainbow spin" lead (`10 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00`). It only accepts hex frames of exactly 16 bytes (first byte 01, 02, 03, 10, 11, 14 or 17) or 20 bytes (the number command or all zeros). It goes through the normal LED queue with the usual spacing, and only while the board is connected.
- While a raw frame is shown, the LED Ring light pauses (attribute `paused_for_raw_frame: true`) so it doesn't draw over the test. `granboard.led` with `effect: clear` (or any other board light action, or turning the LED Ring on again) ends the test, and the light comes back.

## 0.2.5

- New **WLED Sections** (Configure > WLED Sections): add the lights around your board with their position (Top (20) ... Top Left (9 / 12), or a Custom Angle) and an optional Spread. Each dart lights the nearest light(s) in the player's color, with a softer glow on the neighbours. The bulls pulse every light. Awards and turn changes sweep round the lights in board order with a smooth handoff: Ton / Ton 40 / High Ton once, Ton 80 / Hat Trick twice, Bust in red, Checkout / Winner as a two-lap rainbow, and a turn change in the next player's color.
- Every light goes back exactly as it was. WLED lights are driven and restored through WLED's JSON API with transitions (state, effect, palette and segments, without reloading presets), and other lights through `light.turn_on` from their saved state. A new dart interrupts a running animation, and the lights still return to how they were before it started. No polling.
- Settings: **Enable WLED Sections** (default On), **Hit Flash Length** (default 700 ms) and **Only Use Lights That Are Already On** (default On: lights that are off are never touched).
- New LED Ring effect **Circular Rainbow**: the board's own wave animation runs round the whole ring while its two colours keep travelling through the rainbow (or the chosen Ring Palette). It's built from the proven wave command, about one write a second, because no native rainbow command is documented. Unlike Rainbow Chase (one number lit at a time), the whole ring is moving and colourful.
- The setup screen's example Bluetooth address is now a generic `AA:BB:CC:11:22:33`.

## 0.2.4

- New integration logo and icon (shown in Home Assistant 2026.3+ via the brand folder) and a refreshed README.

- New **LED Ring** light (`light.<board>_led_ring`): use the board's LED ring like a WLED light between games. Colour, brightness (scaled into the colour, the board has no brightness setting) and 15 effects: Solid, Blink, Breathe, Heartbeat, Wave, Color Cycle, Palette Steps, Chase, Rainbow Chase, Bounce, Circular Wipe, Twinkle, Fire Flicker, Police and Lightning.
- New **Ring Palette** select with 64 WLED-style palettes (Default, Color 1, Colors 1&2, Color Gradient, Rainbow, Party, Ocean, Lava, Sunset, Aurora, Tiamat, ...). Palette-aware effects take their colours from it.
- New **Ring Speed** and **Ring Intensity** numbers (0-255, like WLED) and **Ring Color 2** text (`#RRGGBB`, empty = the opposite of the light's colour). Everything is restored after a restart.
- Gentle on the board: only the documented ring commands are used, effects write at most 4 times a second (250 ms or more apart, Ring Speed cannot go faster), unchanged whole-ring colours are not re-sent, and nothing is sent while the board is released or offline. When the board reconnects with the light on, the light comes back.
- While a game is playing the light steps aside (it stays on with `paused_for_game: true`) so the game effects run; when the game ends or is cleared it comes back after the game effects finish. A dart outside a game plays its normal hit flash, then the light comes back.

## 0.2.3

- A dart thrown after a full turn now starts the next player and counts for them instead of being ignored (new Configure option, on by default).
- The first hit after connecting is no longer lost when the board glues its banner (e.g. `GB7;101`) onto it.
- Repeat Hit Window default lowered from 500 ms to 250 ms, so quick hits on the same bed count.

## 0.2.2

- `granboard.end_game` now fully clears the game (including a finished game with a winner) back to a blank idle board. Undo restores it.

## 0.2.1

- Player colours are now pure, fully saturated LED colours (red ff0000, blue 0000ff, green 00ff00, ...) so the board and WLED show sharp colours instead of pastel tones (red looked pink).

## 0.2.0

- Board lights like the Granboard app (option **Light The Board On Hits**, on by default). Each dart blinks its segment on the board's LED ring in the thrower's colour: once for a single, twice for a double, three times for a triple. Triple 20 adds a wave. Outer bull flashes the ring, and the inner bull plays a red wave and flash.
- Award effects on the ring for bullseye, bust, ton / ton 40 / high ton, ton 80, hat trick, three in a bed, white horse, checkout and winner.
- A circular wipe goes round the ring in the next player's colour when the turn changes, like the app does when the darts are pulled.
- New `granboard.led` action: segment, blink, wave, ring, numbers, clear, sweep, wipe and award effects.
- LED writes are queued at least 60 ms apart. A new dart replaces effects that are still waiting, the queue is capped, and nothing is sent while the board is released or offline. Repeated frames are filtered before any light fires.
- Player colours: `new_game` takes `colors` (hex or names), with a default 8-colour palette. The Game sensor shows `color` per player and `current_player_color`. `granboard_hit` and `granboard_award` events carry `player` and `color`.
- New `checkout` award when an x01 game is won (with the checkout score and whether the last dart was a double).
- New `granboard_turn` event (player, colour, round) when the turn changes.
- Sounds: Configure now opens a menu (General, Sounds, Sound Volumes). Pick a speaker and an MP3 for any hit, single, double, triple, Triple 20, outer bull, inner bull, miss, each award, bust, checkout, winner, next player and game start. One sound plays per dart (an award beats the hit sound). Optional volume per sound, never above 60 %; empty leaves the volume alone. Every sound also fires a `granboard_sound` event so a dashboard or browser_mod can play it instead.


## 0.1.1

- Fix: one dart or press could count two or three times, because the board repeats the same frame within about 150 ms. An identical frame arriving within 500 ms of the last one is now ignored. Adjust it with **Repeat Hit Window (ms)** in Configure > General (0 turns it off). The throw service is not filtered.

## 0.1.0

- First release. Bluetooth discovery by name or service UUID, plus manual setup by address.
- Keeps the board connected with backoff reconnects. The **Granboard Connection** kill switch and **Release Board** button disconnect immediately and hold no connection until switched back on, so the phone app can connect. The switch state survives restarts.
- `granboard_hit`, `granboard_button`, and `granboard_award` events. Unknown frames are reported with their raw text and logged as warnings.
- Game engine with x01 (301 / 501 / 701, Double Out, busts, checkout suggestions), Cricket, Count-Up, and Around The Clock, with undo, per-player PPD / MPR, and awards.
- Entities: Connected, Last Hit, Last Raw Frame, Signal Strength, Game.
