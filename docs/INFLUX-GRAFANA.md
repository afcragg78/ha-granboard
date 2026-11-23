# InfluxDB and Grafana for Granboard career charts

These files are **ready to apply**. They are not installed by the 0.4.0 integration itself. Nothing here restarts Home Assistant or changes `configuration.yaml` until you choose to apply it.

## What you will get

- Time series in InfluxDB for every dart, visit, award and finished game, plus the Players / Game / Last Hit sensors.
- A Grafana **Darts** dashboard: 3-dart average over time, 180s and ton+, checkout %, a segment heat map, head-to-head wins, with a per-profile selector. Colours are neon accents (cyan, violet, lime, magenta) and are not orange-led.

## Files

| File | Purpose |
|---|---|
| [influxdb.yaml](influxdb.yaml) | `influxdb:` block to merge into `configuration.yaml` |
| [grafana-darts-dashboard.json](grafana-darts-dashboard.json) | Dashboard to import in Grafana (already installed, v13.1.0) |

## Backup plan (do this first)

1. Make a copy of `/config/configuration.yaml` **before** adding any InfluxDB block, for example `/config/configuration.yaml.bak-darts-influx-2026-11-23`. If you add a password to `/config/secrets.yaml`, copy that file too.
2. If the configuration check fails after you add the block, restore the backup and do not restart.
3. To undo later: restore the backup (or delete only the `influxdb:` block), check the configuration, and restart. Stop or uninstall the InfluxDB add-on if you no longer want it. The Grafana dashboard can be deleted from Grafana; stored Influx data stays until you wipe the add-on.

## What to install and apply (in this order)

Home Assistant needs a restart after the YAML is added. Coordinate that restart; do not apply this blindly.

1. **Install the Community InfluxDB add-on** (`a0d7b954_influxdb`) from Settings > Add-ons > Add-on store. Start it and wait until it is healthy. In the add-on, create (or confirm) a database named `homeassistant` and a user `homeassistant` with a password.
2. Put that password in `/config/secrets.yaml` as `influxdb_password: "your-password"`.
3. Merge the contents of `docs/influxdb.yaml` into `/config/configuration.yaml` (top-level `influxdb:` key, not inside `recorder:`). The host `a0d7b954-influxdb` is the add-on's hostname on the Home Assistant network.
4. **Check configuration** in Developer Tools. Only then restart Home Assistant.
5. In Grafana (sidebar panel, already installed), add an **InfluxDB** data source if one is not there:
   - URL: `http://a0d7b954-influxdb:8086`
   - Database: `homeassistant`
   - User / password: the same `homeassistant` credentials
   - InfluxDB 1.x / InfluxQL (the community add-on is 1.x)
6. Import `docs/grafana-darts-dashboard.json` (Dashboards > Import). Pick that InfluxDB data source when asked. Play a few games so events exist; empty panels are normal until then.

The YAML includes only Granboard career sensors and events (`granboard_hit`, `granboard_award`, `granboard_turn`, `granboard_game_over`). LED Ring, WLED and other board lights are excluded so they do not flood the database.

The Game and Players sensor **attributes** stay out of the Recorder (by design). Influx still receives those sensor state changes, but the useful charts come from the events (visit scores, awards, hits, game over).

## After it is running

The darts page can later embed the Grafana dashboard (kiosk or a viewer user). Grafana's ingress panel is admin-only, so a raw iframe on the TV may ask you to log in until a viewer or public-dashboard link is set up. Career numbers also stay available on `sensor.<board>_players` without Grafana.
