# Changelog

## 0.2.0

- Board lights like the Granboard app (option **Light The Board On Hits**, on by default). Each dart blinks its segment on the board's LED ring in the thrower's colour: once for a single, twice for a double, three times for a triple. Triple 20 adds a wave. Outer bull flashes the ring, and the inner bull plays a red wave and flash.
- Award effects on the ring for bullseye, bust, ton / ton 40 / high ton, ton 80, hat trick, three in a bed, white horse, checkout and winner.
- A circular wipe goes round the ring in the next player's colour when the turn changes, like the app does when the darts are pulled.
- New `granboard.led` action: segment, blink, wave, ring, numbers, clear, sweep, wipe and award effects.
- LED writes are queued at least 60 ms apart. A new dart replaces effects that are still waiting, the queue is capped, and nothing is sent while the board is released or offline. Repeated frames are filtered before any light fires.
- Player colours: `new_game` takes `colors` (hex or names), with a default 8-colour palette. The Game sensor shows `color` per player and `current_player_color`. `granboard_hit` and `granboard_award` events carry `player` and `color`.
- New `checkout` award when an x01 game is won (with the checkout score and whether the last dart was a double).
- New `granboard_turn` event (player, colour, round) when the turn changes.


## 0.1.1

- Fix: one dart or press could count two or three times, because the board repeats the same frame within about 150 ms. An identical frame arriving within 500 ms of the last one is now ignored. Adjust it with **Repeat Hit Window (ms)** in Configure (0 turns it off). The throw service is not filtered.

## 0.1.0

- First release. Bluetooth discovery by name or service UUID, plus manual setup by address.
- Keeps the board connected with backoff reconnects. The **Granboard Connection** kill switch and **Release Board** button disconnect immediately and hold no connection until switched back on, so the phone app can connect. The switch state survives restarts.
- `granboard_hit`, `granboard_button`, and `granboard_award` events. Unknown frames are reported with their raw text and logged as warnings.
- Game engine with x01 (301 / 501 / 701, Double Out, busts, checkout suggestions), Cricket, Count-Up, and Around The Clock, with undo, per-player PPD / MPR, and awards.
- Entities: Connected, Last Hit, Last Raw Frame, Signal Strength, Game.
