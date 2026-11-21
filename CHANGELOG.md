# Changelog

## 0.1.0

- First release. Bluetooth discovery by name or service UUID, plus manual setup by address.
- Keeps the board connected with backoff reconnects. The **Granboard Connection** kill switch and **Release Board** button disconnect immediately and hold no connection until switched back on, so the phone app can connect. The switch state survives restarts.
- `granboard_hit`, `granboard_button`, and `granboard_award` events. Unknown frames are reported with their raw text and logged as warnings.
- Game engine with x01 (301 / 501 / 701, Double Out, busts, checkout suggestions), Cricket, Count-Up, and Around The Clock, with undo, per-player PPD / MPR, and awards.
- Entities: Connected, Last Hit, Last Raw Frame, Signal Strength, Game.
