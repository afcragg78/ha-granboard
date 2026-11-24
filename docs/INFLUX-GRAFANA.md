# InfluxDB and Grafana for Granboard career charts

These files are **ready to apply**. They are not installed by the integration itself. Nothing here restarts Home Assistant or changes `configuration.yaml` until you choose to apply it.

The official InfluxDB integration in Home Assistant **2026.x does not record custom events** (`granboard_hit`, `granboard_award`, `granboard_turn`, `granboard_game_over`). Charts are built from **numeric sensors** instead: one set of career figures per saved profile, plus last-visit and last-dart scores on the board. Those sensors only change when a turn ends or a game finishes, so they stay cheap to store.

## What you will get

- Time series in InfluxDB for each player's 3-dart average, first-9 average, checkout percent, 180s, ton+, games played, games won, Cricket MPR and highest checkout, plus the board's last visit score and last dart score.
- A Grafana **Darts** dashboard: averages over time, 180s and ton+, checkout %, Cricket MPR, visit score history, and wins, with a per-player selector. Colours are neon accents (cyan, violet, lime, magenta) and are not orange-led.

Guest slots have no saved profile, so they do not get career sensors.

## Files

| File | Purpose |
|---|---|
| [influxdb.yaml](influxdb.yaml) | Filter-only `influxdb:` block to merge into `configuration.yaml` (no connection fields) |
| [grafana-darts-dashboard.json](grafana-darts-dashboard.json) | Dashboard to import in Grafana |

## How measurements are named

The YAML sets `measurement_attr: entity_id`. Each sensor is written to an Influx measurement named after the entity, for example `sensor.game_room_granboard_3s_andrew_3_dart_average`. The numeric state is the `value` field. `player` and `player_id` are tags.

That is more consistent than Home Assistant's default, where the measurement is the unit of measurement (or the entity id when there is no unit). Checkout percent would otherwise land in `%` while averages landed under their entity ids.

If your board is not named **Game Room Granboard 3s**, the prefix changes. In Grafana, set the `board` variable to your device's object id (the bit after `sensor.` and before `_andrew_…` or `_last_visit_score`).

Example entity ids for that board and a saved player named **Andrew**:

| Sensor | Entity id |
|---|---|
| 3-dart average | `sensor.game_room_granboard_3s_andrew_3_dart_average` |
| First 9 average | `sensor.game_room_granboard_3s_andrew_first_9_average` |
| Checkout percent | `sensor.game_room_granboard_3s_andrew_checkout_percent` |
| 180s | `sensor.game_room_granboard_3s_andrew_180s` |
| Ton+ | `sensor.game_room_granboard_3s_andrew_ton_plus` |
| Games played | `sensor.game_room_granboard_3s_andrew_games_played` |
| Games won | `sensor.game_room_granboard_3s_andrew_games_won` |
| Cricket MPR | `sensor.game_room_granboard_3s_andrew_cricket_mpr` |
| Highest checkout | `sensor.game_room_granboard_3s_andrew_highest_checkout` |
| Last visit score | `sensor.game_room_granboard_3s_last_visit_score` |
| Last dart score | `sensor.game_room_granboard_3s_last_dart_score` |

Unique ids for the career sensors are based on the profile id, so renaming Andrew later keeps the same entities. New profiles get a matching set of sensors when they are added.

## Backup plan (do this first)

1. Make a copy of `/config/configuration.yaml` **before** adding any InfluxDB block, for example `/config/configuration.yaml.bak-darts-influx-2026-11-23`. If you add a password to `/config/secrets.yaml`, copy that file too.
2. If the configuration check fails after you add the block, restore the backup and do not restart.
3. To undo later: restore the backup (or delete only the `influxdb:` block), remove the InfluxDB integration in the UI, check the configuration, and restart. Stop or uninstall the InfluxDB add-on if you no longer want it. The Grafana dashboard can be deleted from Grafana; stored Influx data stays until you wipe the add-on.

## What to install and apply (in this order)

Home Assistant needs a restart after the YAML filters are added (and after the UI integration is first set up). Coordinate that restart; do not apply this blindly.

1. **Install and start the Community InfluxDB v1 add-on** (`a0d7b954_influxdb`) from Settings > Add-ons > Add-on store, if it is not already running. Open **InfluxDB v1** in the sidebar (Chronograf). Create a database named `homeassistant` and a user `homeassistant` with all privileges and a strong password. Auth is on in the usual add-on options, so this step is required.
2. Put that password in `/config/secrets.yaml` as `influxdb_password: "your-password"`. Keep it out of configuration.yaml and out of chat.
3. **Add the InfluxDB integration in the UI:** Settings > Devices & services > Add integration > InfluxDB. Use InfluxDB **1.x** (not a 2.x token / bucket). URL `http://a0d7b954-influxdb:8086`, username `homeassistant`, the password from secrets, database `homeassistant`. (SSL in the add-on options is for the Chronograf web UI; the API URL is still `http`.)
4. Merge the contents of `docs/influxdb.yaml` into `/config/configuration.yaml` (top-level `influxdb:` key, not inside `recorder:`). This block is **filters only** — do not add host, port, database, username or password, and do not add `event_types` (that option is for the Recorder, not InfluxDB, and can fail the config check).
5. **Check configuration** in Developer Tools. Only then restart Home Assistant, after you have agreed to the restart.
6. After the restart, confirm Settings > Devices & services shows the InfluxDB integration (not just the add-on).
7. In Grafana (sidebar panel), add an **InfluxDB** data source if one is not there:
   - URL: `http://a0d7b954-influxdb:8086`
   - Database: `homeassistant`
   - User / password: the same `homeassistant` credentials
   - InfluxDB 1.x / InfluxQL (the community add-on is 1.x)
8. Import `docs/grafana-darts-dashboard.json` (Dashboards > Import). Pick that InfluxDB data source when asked. Set the `board` variable if your device prefix is not `game_room_granboard_3s`. Play a few finished games so career sensors move; empty panels are normal until then. Last visit score starts filling as soon as a turn ends.

The YAML includes only Granboard career / game / last-hit / last-visit sensors. LED Ring, WLED and other board lights are excluded so they do not flood the database.

The Game and Players sensor **attributes** stay out of the Recorder (by design). Influx still receives those sensor *state* changes, but the useful charts come from the numeric career and visit sensors.

## After it is running

The darts page can later embed the Grafana dashboard (kiosk or a viewer user). Grafana's ingress panel is admin-only, so a raw iframe on the TV may ask you to log in until a viewer or public-dashboard link is set up. Career numbers also stay available on the per-player sensors and on `sensor.<board>_players` without Grafana.
