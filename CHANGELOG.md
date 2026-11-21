# Changelog

## 0.2.5

- New **WLED Sections** (Configure > WLED Sections): add the lights around your board with their position (Top (20) ... Top Left (9 / 12), or a Custom Angle) and an optional Spread. Each dart lights the nearest light(s) in the player's color, with a softer glow on the neighbours. The bulls pulse every light. Awards and turn changes sweep round the lights in board order with a smooth handoff: Ton / Ton 40 / High Ton once, Ton 80 / Hat Trick twice, Bust in red, Checkout / Winner as a two-lap rainbow, and a turn change in the next player's color.
- Every light goes back exactly as it was. WLED lights are driven and restored through WLED's JSON API with transitions (state, effect, palette and segments, without reloading presets), and other lights through `light.turn_on` from their saved state. A new dart interrupts a running animation, and the lights still return to how they were before it started. No polling.
- Settings: **Enable WLED Sections** (default On), **Hit Flash Length** (default 700 ms) and **Only Use Lights That Are Already On** (default On: lights that are off are never touched).
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
