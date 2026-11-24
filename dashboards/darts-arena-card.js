/* darts-arena-card — Home Assistant Lovelace custom card (module) */
const DARTS_ARENA_CSS = "\n:host {\n  display: block;\n  height: auto !important;\n  max-height: none !important;\n  overflow: visible;\n  overscroll-behavior: auto;\n  --arena-footer-clear: calc(64px + env(safe-area-inset-bottom, 0px) + 16px);\n  scroll-padding-bottom: var(--arena-footer-clear);\n  background: transparent;\n}\n@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&display=swap');\n\n:host, ha-card, #container, #app, #darts-app, .app {\n  --ink: var(--primary-text-color, #f3f4f7);\n  --muted: var(--secondary-text-color, #b4b8c2);\n  --accent: var(--primary-color, #5dade2);\n  --line: color-mix(in srgb, var(--primary-text-color, #fff) 18%, transparent);\n  --line-strong: color-mix(in srgb, var(--primary-text-color, #fff) 32%, transparent);\n  --fade: color-mix(in srgb, var(--primary-text-color, #fff) 6%, transparent);\n  --danger: #ff6b6b;\n  --ok: #3dd68c;\n  --warn: #ffd166;\n  --font: \"Outfit\", Inter, \"Segoe UI\", system-ui, sans-serif;\n  --ease: 180ms cubic-bezier(.2,.7,.2,1);\n  --arena-footer-clear: calc(64px + env(safe-area-inset-bottom, 0px) + 16px);\n  font-family: var(--font);\n  color: var(--ink);\n  box-sizing: border-box;\n}\n*, *::before, *::after { box-sizing: border-box; }\n#app, .app { width: 100%; }\n:host, ha-card {\n  position: relative;\n  display: block;\n  height: auto !important;\n  max-height: none !important;\n  overflow: visible;\n  overscroll-behavior: auto;\n  scroll-padding-bottom: var(--arena-footer-clear);\n  background: transparent;\n  border: none !important;\n  box-shadow: none !important;\n}\n[hidden], [data-section][hidden] { display: none !important; }\n/* Overlay tap targets must never take layout space or paint as empty cards. */\n[id^=\"ov_\"] {\n  position: absolute !important;\n  background: transparent !important;\n  box-shadow: none !important;\n  border: none !important;\n  overflow: hidden !important;\n  padding: 0 !important;\n  margin: 0 !important;\n  opacity: 0 !important;\n}\n.app {\n  --pc: var(--accent);\n  --ring: var(--accent);\n  --hit: var(--accent);\n  --bri: 0.7;\n  --fx-dur: 8s;\n  --neon: color-mix(in srgb, var(--pc, var(--primary-color, #5dade2)) 70%, #fff 30%);\n  position: relative;\n  isolation: isolate;\n  min-height: 0;\n  height: auto;\n  padding: 0;\n  max-width: none;\n  margin: 0;\n  width: 100%;\n  overflow: visible;\n  background: color-mix(in srgb, var(--card-background-color, #16181e) 72%, #000 28%);\n}\n@media (min-width: 901px) {\n  .app { min-height: 100%; }\n}\n.stage {\n  position: relative;\n  z-index: 1;\n  display: grid;\n  grid-template-columns: 92px minmax(0, 1fr);\n  grid-template-rows: minmax(0, 1fr);\n  grid-template-areas: \"rail main\";\n  min-height: inherit;\n}\n.main { min-width: 0; padding: 18px 36px 40px 28px; overflow: auto; }\n.rail { display: flex; }\n.top { display: none; }\na { color: inherit; }\nbutton, input, select { font: inherit; color: inherit; }\n.sr { position: absolute; width: 1px; height: 1px; overflow: hidden; clip: rect(0,0,0,0); }\n\n/* Top bar */\n.top {\n  grid-template-columns: auto 1fr auto;\n  align-items: end;\n  gap: 24px;\n  padding-bottom: 0;\n  border-bottom: 1px solid var(--line);\n}\n.stage > .top { display: none; }\n.stage > .rail { grid-area: rail; }\n.stage > .main { grid-area: main; }\n.stage {\n  grid-template-areas: \"rail main\";\n}\n.brand { display: flex; align-items: baseline; gap: 12px; min-width: 0; padding-bottom: 16px; }\n.brand svg { width: 22px; height: 22px; flex: 0 0 22px; translate: 0 1px; }\n.brand .name { font-size: 22px; font-weight: 700; letter-spacing: -0.04em; line-height: 1; }\n.brand .tag { font-size: 11px; font-weight: 600; letter-spacing: 0.12em; color: var(--muted); text-transform: none; }\n.nav { display: flex; justify-content: center; gap: 4px 22px; flex-wrap: wrap; }\n.nav button {\n  appearance: none; background: none; border: 0; padding: 8px 0 16px;\n  font-size: 13px; font-weight: 600; letter-spacing: 0.04em;\n  color: var(--muted); cursor: pointer; position: relative;\n  border-radius: 0; transition: color var(--ease);\n}\n.nav button:hover { color: var(--ink); }\n.nav button.on { color: var(--ink); }\n.nav button.on::after {\n  content: \"\"; position: absolute; left: 0; right: 0; bottom: -1px;\n  height: 2px; background: var(--ink);\n}\n.status { display: flex; align-items: center; gap: 8px; font-size: 12px; font-weight: 600; color: var(--muted); padding-bottom: 16px; white-space: nowrap; }\n.status .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--muted); }\n.status .dot.ok { background: var(--ok); box-shadow: 0 0 8px var(--ok); }\n.status .dot.wait { background: var(--warn); animation: pulse 1.6s ease-in-out infinite; }\n@keyframes pulse { 50% { opacity: .35 } }\n\n/* Type */\n.kicker { font-size: 11px; font-weight: 600; letter-spacing: 0.14em; color: var(--muted); }\n.display { font-weight: 800; letter-spacing: -0.05em; line-height: 0.92; font-variant-numeric: tabular-nums; }\n.title { font-size: clamp(28px, 3.2vw, 42px); font-weight: 700; letter-spacing: -0.035em; line-height: 1.05; }\n.lede { color: var(--muted); font-size: 14px; font-weight: 500; }\n.section { margin-top: 48px; }\n.section-h { display: flex; align-items: baseline; justify-content: space-between; gap: 16px; margin-bottom: 16px; padding-bottom: 10px; border-bottom: 1px solid var(--line); }\n.section-h h2 { margin: 0; font-size: 13px; font-weight: 650; letter-spacing: 0.08em; }\n\n/* Buttons \u2014 ghost / outline, never pills */\n.btn {\n  appearance: none; background: transparent;\n  border: 1px solid var(--line-strong);\n  border-radius: 8px;\n  padding: 10px 16px;\n  font-size: 14px; font-weight: 600; letter-spacing: -0.01em;\n  color: var(--ink); cursor: pointer;\n  display: inline-flex; align-items: center; gap: 8px;\n  transition: border-color var(--ease), background var(--ease), color var(--ease), transform var(--ease);\n}\n.btn svg { width: 16px; height: 16px; flex: 0 0 16px; }\n.btn:hover { border-color: color-mix(in srgb, var(--ink) 40%, transparent); background: var(--fade); }\n.btn:active { transform: translateY(1px); }\n.btn.quiet { border-color: transparent; padding-left: 8px; padding-right: 8px; color: var(--muted); }\n.btn:not(.quiet) { text-decoration: none; }\n.fx .btn:not(.quiet), .modes .btn:not(.quiet) { box-shadow: inset 0 -2px 0 var(--ink); border-color: transparent; border-radius: 0; padding-left: 4px; padding-right: 4px; }\n.btn.quiet:hover { color: var(--ink); background: transparent; border-color: transparent; }\n.btn.warn:hover { border-color: var(--danger); color: var(--danger); background: transparent; }\n.actions { display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }\n.modes {\n  display: grid;\n  grid-template-columns: repeat(5, minmax(0, 1fr));\n  gap: 4px 6px;\n  width: 100%;\n  overflow: visible;\n}\n.icon-row, .fx, .preset-row, .theme-row {\n  display: flex;\n  flex-wrap: nowrap;\n  gap: 4px 8px;\n  overflow-x: auto;\n  overflow-y: hidden;\n  -webkit-overflow-scrolling: touch;\n  scrollbar-width: thin;\n  padding: 2px 0 8px;\n}\n.mode-tile, .icon-tile {\n  appearance: none;\n  background: transparent;\n  border: 0;\n  border-radius: 0;\n  box-shadow: none;\n  padding: 8px 4px 6px;\n  display: flex;\n  flex-direction: column;\n  align-items: center;\n  justify-content: flex-start;\n  gap: 6px;\n  color: var(--muted);\n  cursor: pointer;\n  min-width: 0;\n  flex: 0 0 auto;\n  transition: color var(--ease), transform var(--ease), filter var(--ease);\n}\n.modes .mode-tile { width: 100%; min-width: 0; }\n.icon-tile { min-width: 64px; max-width: 88px; }\n.mode-tile svg, .icon-tile svg { width: 28px; height: 28px; display: block; flex: 0 0 28px; }\n.mode-label, .icon-label {\n  font-size: 10px;\n  font-weight: 600;\n  letter-spacing: 0.02em;\n  text-align: center;\n  line-height: 1.2;\n  color: inherit;\n  max-width: 100%;\n}\n.mode-tile:hover, .icon-tile:hover,\n.mode-tile:focus-visible, .icon-tile:focus-visible {\n  color: var(--ink);\n  background: transparent;\n}\n.mode-tile:hover svg, .icon-tile:hover svg,\n.mode-tile:focus-visible svg, .icon-tile:focus-visible svg {\n  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--accent, var(--primary-color)) 55%, transparent));\n}\n.mode-tile:hover .mode-label, .icon-tile:hover .icon-label,\n.mode-tile:focus-visible .mode-label, .icon-tile:focus-visible .icon-label {\n  text-shadow: 0 0 8px color-mix(in srgb, var(--accent, var(--primary-color)) 40%, transparent);\n}\n.mode-tile:active, .icon-tile:active { transform: translateY(1px); background: transparent; }\n.icon-tile.on, .mode-tile.on { color: var(--ink); background: transparent; }\n.icon-tile.on svg, .mode-tile.on svg {\n  filter: drop-shadow(0 0 6px color-mix(in srgb, var(--accent, var(--primary-color)) 50%, transparent));\n}\n.icon-tile.on .icon-label, .mode-tile.on .mode-label {\n  box-shadow: inset 0 -2px 0 var(--ink);\n  text-shadow: 0 0 8px color-mix(in srgb, var(--accent, var(--primary-color)) 35%, transparent);\n}\n\n\n/* Game */\n.game { display: grid; grid-template-columns: minmax(0, 480px) minmax(0, 1fr); gap: 40px 64px; padding-top: 36px; align-items: start; }\n.hero-top { display: flex; justify-content: space-between; align-items: baseline; gap: 16px; margin-bottom: 28px; }\n.score {\n  font-size: clamp(72px, 11vw, 152px); font-weight: 800; letter-spacing: -0.06em; line-height: 0.88;\n  font-variant-numeric: tabular-nums;\n  background-image: linear-gradient(\n    105deg,\n    #ffffff 0%,\n    #ffffff 36%,\n    color-mix(in srgb, var(--pc) 55%, #fff) 50%,\n    #ffffff 64%,\n    #f2f3f7 100%\n  );\n  background-size: 220% 100%;\n  background-position: 40% 0;\n  -webkit-background-clip: text;\n  background-clip: text;\n  color: transparent;\n  filter: drop-shadow(0 0 18px color-mix(in srgb, var(--pc) 40%, transparent));\n  animation: scoreSheen 6s ease-in-out infinite;\n}\n@keyframes scoreSheen {\n  0%, 16% { background-position: 120% 0; }\n  58%, 100% { background-position: -20% 0; }\n}\n.score.idle { font-size: clamp(40px, 6vw, 64px); font-weight: 500; opacity: 0.35; letter-spacing: -0.02em; }\n.who { margin-top: 4px; }\n.who .name {\n  color: var(--pc, var(--ink));\n  text-shadow:\n    0 0 8px color-mix(in srgb, var(--pc) 85%, #fff),\n    0 0 20px var(--pc),\n    0 0 42px color-mix(in srgb, var(--pc) 65%, transparent);\n  animation: nameBreathe 2.8s ease-in-out infinite;\n}\n.meta-row { display: flex; gap: 20px; margin-top: 8px; font-size: 13px; font-weight: 500; color: var(--muted); }\n.tray { margin-top: 36px; }\n.slots { display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-top: 12px; }\n.slot {\n  min-height: 64px; display: flex; flex-direction: column; align-items: center; justify-content: center;\n  border: 1px dashed color-mix(in srgb, var(--ink) 45%, transparent); border-radius: 8px; background: transparent;\n}\n.slot.on { border-style: solid; }\n.slot span { font-size: 22px; font-weight: 700; letter-spacing: -0.03em; }\n.slot small { font-size: 11px; font-weight: 600; color: var(--muted); margin-top: 2px; }\n.slot.r-treble { border-bottom: 2px solid #e5484d; }\n.slot.r-double, .slot.r-bull { border-bottom: 2px solid #3dd68c; }\n.slot.r-bullseye { border-bottom: 2px solid #e5484d; }\n.slot.pop { animation: pop .45s cubic-bezier(.2,1.4,.4,1); }\n@keyframes pop { 0%{transform:scale(.92);opacity:0} 100%{transform:scale(1);opacity:1} }\n.roster { margin-top: 40px; }\n.row {\n  display: grid; grid-template-columns: 3px 1fr auto; gap: 16px; align-items: center;\n  padding: 14px 0; border-bottom: 1px solid var(--line);\n  position: relative;\n  opacity: 1;\n  transition: opacity 0.65s ease, filter 0.65s ease;\n}\n.row:first-child { border-top: 1px solid var(--line); }\n.app.is-play .row:not(.cur) { opacity: 0.42; filter: saturate(0.75); }\n.row .bar { align-self: stretch; background: var(--pc); transition: box-shadow 0.65s ease, background 0.65s ease; }\n.row .nm {\n  font-size: 18px; font-weight: 650; letter-spacing: -0.02em;\n  transition: color 0.65s ease, text-shadow 0.65s ease;\n}\n.row .sub { font-size: 12px; font-weight: 500; color: var(--muted); margin-top: 2px; }\n.row .pts {\n  font-size: 28px; font-weight: 700; letter-spacing: -0.04em; font-variant-numeric: tabular-nums;\n  transition: font-size 0.45s ease, color 0.65s ease, text-shadow 0.65s ease, filter 0.65s ease;\n}\n.row.cur .nm {\n  color: var(--pc);\n  text-shadow:\n    0 0 8px color-mix(in srgb, var(--pc) 85%, #fff),\n    0 0 20px var(--pc),\n    0 0 42px color-mix(in srgb, var(--pc) 65%, transparent);\n  animation: nameBreathe 2.8s ease-in-out infinite;\n}\n.row.cur .pts {\n  font-size: 32px;\n  text-shadow: 0 0 16px color-mix(in srgb, var(--pc) 45%, transparent);\n}\n.row.cur .bar {\n  box-shadow: 0 0 8px var(--pc), 0 0 18px color-mix(in srgb, var(--pc) 80%, transparent);\n}\n.row.cur::after {\n  content: \"\";\n  position: absolute;\n  left: 19px; right: 0; bottom: -1px;\n  height: 2px;\n  background: linear-gradient(90deg, transparent, var(--pc), #fff, var(--pc), transparent);\n  background-size: 200% 100%;\n  box-shadow: 0 0 12px var(--pc);\n  animation: underGlow 3.2s ease-in-out infinite;\n  pointer-events: none;\n}\n@keyframes nameBreathe {\n  0%, 100% { filter: brightness(1); }\n  50% { filter: brightness(1.22); }\n}\n@keyframes underGlow {\n  0%, 100% { background-position: 0% 50%; opacity: 0.72; }\n  50% { background-position: 100% 50%; opacity: 1; }\n}\n.co { margin-top: 24px; font-size: 20px; font-weight: 700; letter-spacing: -0.02em; }\n.co .lbl { display: block; font-size: 11px; letter-spacing: 0.12em; color: var(--muted); font-weight: 600; margin-bottom: 6px; }\n.co b { font-weight: 700; }\n.co i { font-style: normal; color: var(--muted); margin: 0 8px; font-weight: 500; }\n.banner { margin-top: 20px; font-size: 18px; font-weight: 700; letter-spacing: -0.02em; }\n.banner.win { color: #ffd54a; }\n.banner.bust { color: var(--danger); }\n.banner.next { font-size: 14px; font-weight: 600; color: var(--muted); }\n.board-side { position: relative; text-align: center; overflow: hidden; --board-glow: var(--pc, var(--primary-color, #5dade2)); --board-glow-a: 0.55; }\n.board-art {\n  position: relative;\n  display: block;\n  width: min(100%, calc(62vh + 36px));\n  max-width: 100%;\n  margin: 0 auto;\n  padding: 18px;\n  box-sizing: border-box;\n  overflow: hidden;\n  border-radius: 50%;\n  z-index: 0;\n  isolation: isolate;\n  pointer-events: none;\n}\n.board-art svg {\n  position: relative; z-index: 1;\n  display: block;\n  width: 100%;\n  height: auto;\n  aspect-ratio: 1 / 1;\n  overflow: visible;\n  pointer-events: auto;\n  filter: drop-shadow(0 10px 16px color-mix(in srgb, var(--ink) 10%, transparent));\n}\n/* Soft 8-zone rim ring: at most 18px past the board, faded, restrained neon */\n.board-glow-bloom {\n  position: absolute;\n  inset: 0;\n  border-radius: 50%;\n  pointer-events: none;\n  z-index: 0;\n  --z0: var(--board-glow);\n  --z1: var(--board-glow);\n  --z2: var(--board-glow);\n  --z3: var(--board-glow);\n  --z4: var(--board-glow);\n  --z5: var(--board-glow);\n  --z6: var(--board-glow);\n  --z7: var(--board-glow);\n  background: conic-gradient(from -22.5deg,\n    var(--z0), var(--z1), var(--z2), var(--z3),\n    var(--z4), var(--z5), var(--z6), var(--z7), var(--z0));\n  filter: blur(8px) saturate(1.12);\n  opacity: var(--board-glow-a, 0.55);\n  transition: opacity 1.5s ease, filter 0.8s linear;\n  transform-origin: center center;\n  -webkit-mask-image: radial-gradient(circle closest-side, transparent 86%, #000 90%, #000 94%, transparent 100%);\n  mask-image: radial-gradient(circle closest-side, transparent 86%, #000 90%, #000 94%, transparent 100%);\n}\n.board-side.glow-breathe .board-glow-bloom {\n  animation: boardGlowBreathe var(--board-glow-dur, 5.6s) ease-in-out infinite;\n}\n.board-side.glow-blink .board-glow-bloom {\n  animation: boardGlowBlink var(--board-glow-dur, 1.2s) linear infinite;\n}\n.board-side.glow-heartbeat .board-glow-bloom {\n  animation: boardGlowHeartbeat var(--board-glow-dur, 1.7s) linear infinite;\n}\n@keyframes boardGlowBreathe {\n  0%, 100% { opacity: var(--glow-floor, 0.3); }\n  50% { opacity: var(--board-glow-a, 0.95); }\n}\n@keyframes boardGlowBlink {\n  0%, 45% { opacity: var(--board-glow-a, 0.9); }\n  50%, 95% { opacity: 0.06; }\n  100% { opacity: var(--board-glow-a, 0.9); }\n}\n@keyframes boardGlowHeartbeat {\n  0%, 8% { opacity: var(--board-glow-a, 0.95); }\n  14% { opacity: 0.18; }\n  22% { opacity: var(--board-glow-a, 0.95); }\n  30%, 100% { opacity: 0.16; }\n}\n.board-side.glow-rainbow .board-glow-prism {\n  animation-duration: var(--board-glow-dur, 18s);\n}\n/* Rainbow rim: same 18px hug as the bloom, never a disc, never past the art clip */\n.board-glow-rainbow-clip {\n  display: none;\n  position: absolute;\n  inset: 0;\n  border-radius: 50%;\n  overflow: hidden;\n  pointer-events: none;\n  z-index: 0;\n  contain: paint;\n  -webkit-mask-image: radial-gradient(circle closest-side, transparent 86%, #000 90%, #000 94%, transparent 100%);\n  mask-image: radial-gradient(circle closest-side, transparent 86%, #000 90%, #000 94%, transparent 100%);\n}\n.board-glow-prism {\n  position: absolute;\n  inset: 0;\n  border-radius: 50%;\n  background: conic-gradient(#ff2a6d, #ff8a00, #ffe600, #2bff88, #00d5ff, #2f6bff, #8a2bff, #ff2ad0, #ff2a6d);\n  filter: blur(8px) saturate(1.12);\n  opacity: 0.55;\n  will-change: transform;\n  contain: paint;\n  pointer-events: none;\n  animation: boardGlowSpin 18s linear infinite;\n}\n@keyframes boardGlowSpin {\n  from { transform: translateZ(0) rotate(0deg); }\n  to { transform: translateZ(0) rotate(360deg); }\n}\n.board-side.glow-rainbow .board-glow-rainbow-clip { display: block; }\n.board-side.glow-rainbow .board-glow-bloom {\n  will-change: transform;\n  animation: boardGlowOrbit var(--board-glow-dur, 18s) linear infinite;\n}\n@keyframes boardGlowOrbit {\n  from { transform: rotate(0deg); }\n  to { transform: rotate(360deg); }\n}\n.board-side.glow-off .board-glow-bloom { opacity: 0; }\n.board-side.glow-off .board-glow-rainbow-clip { display: none; }\n.rim-aura {\n  fill: none; stroke: var(--pc); stroke-width: 14;\n  opacity: 0.22; filter: blur(6px);\n}\n.rim-glow {\n  fill: none; stroke: var(--pc); stroke-width: 3.2;\n  opacity: 0.9; filter: blur(0.6px);\n}\n.ring-outer { fill: color-mix(in srgb, var(--ink) 8%, #111); }\n.ring-bevel { fill: none; stroke: color-mix(in srgb, var(--ink) 22%, #8a7350); stroke-width: 10; }\n.nums text { fill: #f3f4f7; font-size: 20px; font-weight: 600; text-anchor: middle; font-family: sans-serif; }\n.wires { stroke: color-mix(in srgb, var(--ink) 20%, transparent); stroke-width: .6; fill: none; }\n.hit { fill: var(--pc, var(--accent)); stroke: #fff; stroke-width: 2; filter: drop-shadow(0 0 10px var(--pc, var(--accent))); animation: hitFade 20s ease-out forwards; }\n.hit.flash { animation: flash 1.1s ease-out, hitFade 20s ease-out forwards; }\n.burst { fill: none; stroke: #fff; stroke-width: 3; animation: burst .9s ease-out forwards; opacity: 0; }\n.hitlbl { position: relative; z-index: 2; margin-top: 8px; }\n.hitlbl b { display: block; font-size: clamp(28px, 4vh, 48px); font-weight: 800; letter-spacing: -0.04em; }\n.hitlbl span { display: block; margin-top: 4px; font-size: 13px; font-weight: 500; color: var(--muted); }\n@keyframes flash { 0%,30%,60%{opacity:1;fill:#fff} 15%,45%{opacity:.35;fill:var(--pc)} 100%{opacity:.9} }\n@keyframes hitFade { 0%,92.5%{opacity:.9} 100%{opacity:0} }\n@keyframes burst { 0%{transform:scale(.4);opacity:1} 100%{transform:scale(8);opacity:0} }\n.play-actions { margin-top: 36px; padding-top: 20px; border-top: 1px solid var(--line); }\n.cr { display: grid; gap: 0; margin-top: 8px; text-align: center; }\n.cr .ch { font-size: 11px; font-weight: 650; color: var(--muted); padding: 8px 4px; }\n.cr .ct { font-weight: 700; font-size: 14px; padding: 8px 4px; border-top: 1px solid var(--line); }\n.cr .ct.closed { opacity: .35; text-decoration: line-through; }\n.cr .cm { height: 36px; display: flex; align-items: center; justify-content: center; border-top: 1px solid var(--line); }\n.cr .cm svg { width: 18px; height: 18px; fill: none; stroke: var(--pc, var(--accent)); stroke-width: 2.2; stroke-linecap: round; }\n\n/* Forms & pickers */\n.field { display: grid; gap: 8px; margin: 16px 0; }\n.field label { font-size: 12px; font-weight: 600; letter-spacing: 0.06em; color: var(--muted); }\n.field input[type=text], .field select {\n  background: transparent; border: 0; border-bottom: 1px solid var(--line);\n  border-radius: 0; padding: 10px 0; outline: none; font-size: 16px; font-weight: 500;\n}\n.field input[type=text]:focus, .field select:focus { border-bottom-color: var(--ink); }\n.toggle { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 16px 0; border-bottom: 1px solid var(--line); cursor: pointer; }\n.toggle span { font-size: 15px; font-weight: 600; }\n.toggle i {\n  width: 36px; height: 20px; border: 1px solid var(--line); border-radius: 8px; position: relative; display: inline-block;\n}\n.toggle i::after { content: \"\"; position: absolute; top: 2px; left: 2px; width: 14px; height: 14px; background: var(--muted); border-radius: 3px; transition: transform var(--ease), background var(--ease); }\n.toggle.on i { border-color: var(--ink); }\n.toggle.on i::after { transform: translateX(16px); background: var(--ink); }\n\n.swatches, .palettes, .fx { display: flex; flex-wrap: wrap; gap: 8px; }\n.swatch {\n  width: 32px; height: 32px; border: 1px solid color-mix(in srgb, var(--ink) 18%, transparent);\n  border-radius: 8px; cursor: pointer; padding: 0; background: center/cover no-repeat;\n  transition: transform var(--ease), outline-color var(--ease);\n}\n.swatch:hover { transform: translateY(-1px); }\n.swatch.on { outline: 2px solid var(--ink); outline-offset: 3px; }\n.pal {\n  width: 148px; height: 64px; border: 0; border-radius: 6px; cursor: pointer;\n  padding: 0 10px 8px; display: flex; align-items: flex-end;\n  font-size: 11px; font-weight: 650; color: #fff; text-shadow: 0 1px 3px rgba(0,0,0,.7);\n  text-align: left; overflow: hidden; position: relative;\n}\n.pal.on { outline: 2px solid var(--ink); outline-offset: 3px; }\n.fx button { }\n.range { display: grid; gap: 8px; margin: 20px 0; }\n.range label { display: flex; justify-content: space-between; font-size: 12px; font-weight: 600; letter-spacing: 0.06em; color: var(--muted); }\n.range input[type=range] {\n  appearance: none; height: 16px; background: transparent; border-radius: 0; outline: none; width: 100%;\n  margin: 0; padding: 0;\n}\n.range input[type=range]::-webkit-slider-runnable-track {\n  height: 2px; background: color-mix(in srgb, var(--ink) 40%, transparent); border-radius: 0;\n}\n.range input[type=range]::-webkit-slider-thumb {\n  appearance: none; width: 14px; height: 14px; border-radius: 2px; background: var(--ink); border: 0; cursor: pointer;\n  margin-top: -6px;\n}\n.range input[type=range]::-moz-range-track {\n  height: 2px; background: color-mix(in srgb, var(--ink) 40%, transparent); border: 0;\n}\n.range input[type=range]::-moz-range-thumb {\n  width: 14px; height: 14px; border-radius: 2px; background: var(--ink); border: 0; cursor: pointer;\n}\n.def { display: grid; grid-template-columns: 180px 1fr; gap: 8px 24px; padding: 12px 0; border-bottom: 1px solid var(--line); font-size: 14px; }\n.def dt { font-weight: 600; color: var(--muted); }\n.def dd { margin: 0; font-weight: 600; }\n.note { margin-top: 16px; font-size: 13px; font-weight: 500; color: var(--muted); max-width: 52ch; line-height: 1.5; }\n\n/* Modal */\n.modal-bg { position: fixed; inset: 0; background: color-mix(in srgb, #000 40%, transparent); display: flex; align-items: center; justify-content: center; z-index: 20; }\n.modal { background: color-mix(in srgb, var(--card-background-color, #1c1c1e) 88%, #fff 12%); padding: 28px 32px; max-width: 420px; width: calc(100% - 32px); border: 1px solid var(--line); border-radius: 8px; }\n.modal p { margin: 0 0 20px; font-size: 16px; font-weight: 600; letter-spacing: -0.02em; }\n\n\n/* Active lighting \u2014 Dynaframe-style edge blooms and color washes */\n.lights, .halo-wrap, .key-halo { display: none !important; }\n.edge {\n  position: absolute;\n  inset: 0;\n  pointer-events: none;\n}\n.edge i {\n  position: absolute;\n  display: block;\n  pointer-events: none;\n  will-change: box-shadow;\n  transition: box-shadow 0.2s linear;\n}\n.edge .t0 { left: 0; top: 0; width: 34%; height: 2px; box-shadow: var(--z0); }\n.edge .t1 { left: 33%; top: 0; width: 34%; height: 2px; box-shadow: var(--z1); }\n.edge .t2 { left: 66%; top: 0; width: 34%; height: 2px; box-shadow: var(--z2); }\n.edge .r0 { right: 0; top: 0; width: 2px; height: 34%; box-shadow: var(--z2); }\n.edge .r1 { right: 0; top: 33%; width: 2px; height: 34%; box-shadow: var(--z3); }\n.edge .r2 { right: 0; top: 66%; width: 2px; height: 34%; box-shadow: var(--z4); }\n.edge .b2 { left: 66%; bottom: 0; width: 34%; height: 2px; box-shadow: var(--z4); }\n.edge .b1 { left: 33%; bottom: 0; width: 34%; height: 2px; box-shadow: var(--z5); }\n.edge .b0 { left: 0; bottom: 0; width: 34%; height: 2px; box-shadow: var(--z6); }\n.edge .l2 { left: 0; top: 66%; width: 2px; height: 34%; box-shadow: var(--z6); }\n.edge .l1 { left: 0; top: 33%; width: 2px; height: 34%; box-shadow: var(--z7); }\n.edge .l0 { left: 0; top: 0; width: 2px; height: 34%; box-shadow: var(--z0); }\n\n\n/* Left rail (TV / tablet) */\n.rail {\n  flex-direction: column;\n  align-items: center;\n  gap: 16px;\n  padding: 20px 8px 24px;\n  border-right: 1px solid var(--line);\n  background: color-mix(in srgb, var(--card-background-color, #16181e) 55%, transparent);\n  min-height: 0;\n  overflow: hidden;\n}\n.rail-av {\n  width: 44px; height: 44px; border-radius: 50%;\n  display: grid; place-items: center;\n  border: 1px solid color-mix(in srgb, var(--primary-color, var(--accent)) 45%, transparent);\n  box-shadow: 0 0 12px color-mix(in srgb, var(--primary-color, var(--accent)) 28%, transparent);\n  color: var(--ink);\n}\n.rail-av svg { width: 22px; height: 22px; }\n.rail-nav {\n  display: flex; flex-direction: column; gap: 2px; width: 100%; flex: 1;\n}\n.rail-nav button {\n  appearance: none; background: none; border: 0; border-radius: 0;\n  display: flex; flex-direction: column; align-items: center; gap: 4px;\n  padding: 10px 4px; color: var(--muted); cursor: pointer;\n  font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase;\n  position: relative; transition: color var(--ease);\n}\n.rail-nav button svg { width: 18px; height: 18px; }\n.rail-nav button:hover { color: var(--ink); }\n.rail-nav button.on { color: var(--ink); }\n.rail-nav button.on::before {\n  content: \"\"; position: absolute; left: 0; top: 8px; bottom: 8px; width: 2px;\n  background: var(--neon, var(--ink));\n  box-shadow: 0 0 8px color-mix(in srgb, var(--primary-color, var(--accent)) 55%, transparent);\n}\n.rail .status { writing-mode: horizontal-tb; flex-direction: column; text-align: center; white-space: normal; padding: 0; font-size: 9px; letter-spacing: 0.04em; line-height: 1.3; }\n\n/* Omni game (TV / tablet) */\n.game-omni {\n  display: grid;\n  grid-template-columns: minmax(0, 1.05fr) minmax(0, 0.95fr);\n  gap: 20px 36px;\n  align-items: start;\n}\n.omni-left { min-width: 0; display: flex; flex-direction: column; gap: 16px; }\n.omni-board { min-width: 0; }\n.game-key { display: none; }\n\n.match {\n  display: grid;\n  grid-template-columns: auto 1fr auto;\n  gap: 16px;\n  align-items: center;\n  padding: 10px 4px 14px;\n  border-bottom: 1px solid color-mix(in srgb, var(--primary-color, var(--accent)) 22%, transparent);\n  box-shadow: 0 1px 12px color-mix(in srgb, var(--primary-color, var(--accent)) 8%, transparent);\n}\n.match-mid { text-align: center; min-width: 0; }\n.match-title { font-size: clamp(22px, 2.4vw, 32px); font-weight: 800; letter-spacing: -0.05em; line-height: 1; }\n.match-sub { margin-top: 4px; font-size: 11px; font-weight: 600; letter-spacing: 0.12em; color: var(--muted); text-transform: uppercase; }\n.chips { display: flex; justify-content: center; flex-wrap: wrap; gap: 8px; margin-top: 8px; }\n.chips span {\n  font-size: 10px; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase;\n  padding: 4px 8px; border: 1px solid var(--line-strong); border-radius: 4px; color: var(--muted);\n}\n.legs { display: flex; gap: 0; border-bottom: 1px solid var(--line); }\n.legs button {\n  appearance: none; background: none; border: 0; border-radius: 0; cursor: pointer;\n  padding: 8px 14px; font-size: 11px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase;\n  color: var(--muted);\n}\n.legs button.on {\n  color: var(--ink);\n  box-shadow: inset 0 -2px 0 var(--neon, var(--ink)), 0 4px 12px color-mix(in srgb, var(--primary-color, var(--accent)) 18%, transparent);\n}\n\n.avatar {\n  width: 44px; height: 44px; border-radius: 50%;\n  display: grid; place-items: center;\n  font-size: 16px; font-weight: 800; letter-spacing: -0.03em;\n  color: var(--ink);\n  border: 2px solid var(--pc, var(--primary-color, var(--accent)));\n  background: color-mix(in srgb, var(--pc, var(--primary-color)) 16%, transparent);\n  transition: box-shadow 0.65s ease, border-color 0.65s ease;\n}\n.avatar.on {\n  box-shadow: 0 0 0 1px color-mix(in srgb, var(--pc) 40%, transparent), 0 0 14px color-mix(in srgb, var(--pc) 45%, transparent);\n}\n\n.score-row { display: grid; grid-template-columns: 1fr auto 1fr; gap: 16px; align-items: stretch; }\n.score-row.multi { grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); }\n\n.pl {\n  position: relative;\n  isolation: isolate;\n  padding: 16px 16px 18px;\n  border: 1px solid var(--line);\n  border-radius: 10px;\n  background: color-mix(in srgb, var(--card-background-color, #1c1c1e) 78%, transparent);\n  opacity: 1;\n  transition: opacity 0.65s ease, filter 0.65s ease, border-color 0.65s ease;\n}\n.app.is-play .pl:not(.cur) { opacity: 0.5; filter: saturate(0.8); }\n.pl-head { display: flex; align-items: center; gap: 10px; }\n.pl-name { font-size: 15px; font-weight: 700; letter-spacing: -0.02em; }\n.pl-score {\n  margin-top: 8px;\n  font-size: clamp(56px, 7vw, 96px);\n  font-weight: 800; letter-spacing: -0.07em; line-height: 0.9;\n  font-variant-numeric: tabular-nums;\n}\n.pl-score.idle { display: none; }\n.pl.cur .pl-score {\n  text-shadow:\n    0 0 8px color-mix(in srgb, var(--pc) 50%, transparent),\n    0 0 22px color-mix(in srgb, var(--pc) 28%, transparent);\n}\n.pl.cur .pl-name {\n  color: var(--pc);\n  text-shadow: 0 0 12px color-mix(in srgb, var(--pc) 40%, transparent);\n}\n.pl-stats { margin: 12px 0 0; display: grid; gap: 6px; }\n.pl-stats div { display: flex; justify-content: space-between; gap: 10px; border-top: 1px solid var(--line); padding-top: 6px; }\n.pl-stats dt { font-size: 10px; font-weight: 700; letter-spacing: 0.12em; text-transform: uppercase; color: var(--muted); }\n.pl-stats dd { margin: 0; font-size: 15px; font-weight: 700; font-variant-numeric: tabular-nums; }\n\n.your-turn {\n  margin-top: 10px;\n  padding: 7px 10px;\n  font-size: 12px; font-weight: 800; letter-spacing: 0.06em; text-transform: none; text-align: center;\n  color: var(--ink);\n  border: 1px solid color-mix(in srgb, var(--pc) 55%, transparent);\n  border-radius: 6px;\n  background: color-mix(in srgb, var(--pc) 16%, transparent);\n  text-shadow: 0 0 10px color-mix(in srgb, var(--pc) 40%, transparent);\n  box-shadow: 0 0 14px color-mix(in srgb, var(--pc) 22%, transparent);\n}\n\n/* Static, edge-contained soft neon glow. No rotation, no conic square, no continuous animation. */\n.pl, .key-hero-wrap { overflow: hidden; }\n.pl > .pl-head, .pl > .your-turn, .pl > .pl-score, .pl > .pl-stats,\n.key-hero-wrap > .key-hero { position: relative; z-index: 1; }\n.halo-wrap {\n  position: absolute;\n  inset: 0;\n  width: 100%;\n  height: 100%;\n  overflow: hidden;\n  border-radius: inherit;\n  pointer-events: none !important;\n  contain: strict;\n  z-index: 0;\n  transform: translateZ(0);\n}\n.pl .halo-wrap { border-radius: 10px; }\n.key-halo { border-radius: 18px; }\n.pl:not(.cur) .halo-wrap,\n.key-hero-wrap:not(.cur) .key-halo { display: none; }\n.halo-glow,\n.halo-ring {\n  position: absolute;\n  pointer-events: none !important;\n  animation: none;\n  will-change: auto;\n}\n.halo-glow {\n  inset: 0;\n  border-radius: inherit;\n  background:\n    radial-gradient(ellipse 90% 70% at 50% 0%, color-mix(in srgb, var(--pc, var(--primary-color, #5dade2)) 38%, transparent), transparent 70%),\n    radial-gradient(ellipse 70% 60% at 0% 80%, color-mix(in srgb, var(--pc, var(--primary-color, #5dade2)) 18%, transparent), transparent 68%),\n    radial-gradient(ellipse 70% 60% at 100% 80%, color-mix(in srgb, var(--pc, var(--primary-color, #5dade2)) 16%, transparent), transparent 68%);\n  opacity: 0.7;\n}\n.halo-ring {\n  inset: 0;\n  border-radius: inherit;\n  background: none;\n  box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--pc, var(--primary-color, #5dade2)) 40%, transparent);\n  opacity: 0.9;\n}\n.pl.cur { border-color: color-mix(in srgb, var(--pc) 35%, transparent); }\n\n.badge {\n  display: flex; flex-direction: column; align-items: center; justify-content: center;\n  min-width: 88px; padding: 10px 12px; text-align: center;\n  border: 1px solid color-mix(in srgb, var(--primary-color, var(--accent)) 28%, transparent);\n  border-radius: 10px;\n  box-shadow: 0 0 16px color-mix(in srgb, var(--primary-color, var(--accent)) 12%, transparent);\n}\n.badge-k, .badge-g { font-size: 9px; font-weight: 700; letter-spacing: 0.14em; text-transform: uppercase; color: var(--muted); }\n.badge strong { font-size: 36px; font-weight: 800; letter-spacing: -0.06em; line-height: 1; margin: 4px 0; }\n\n.dart-tray .kicker { margin-bottom: 8px; }\n.dart-cards { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; }\n.dart-card {\n  border: 1px solid var(--line);\n  border-radius: 8px;\n  overflow: hidden;\n  background: color-mix(in srgb, var(--card-background-color, #1c1c1e) 70%, transparent);\n  min-height: 86px;\n  display: flex; flex-direction: column;\n}\n.dart-card svg { display: block; width: 100%; height: 70px; background: #14161c; }\n.dart-card .dc-meta { display: flex; justify-content: space-between; align-items: baseline; padding: 6px 8px 8px; }\n.dart-card .dc-meta b { font-size: 16px; font-weight: 800; letter-spacing: -0.03em; }\n.dart-card .dc-meta span { font-size: 12px; font-weight: 700; color: var(--muted); }\n.dart-card.empty { align-items: center; justify-content: center; border-style: dashed; color: var(--muted); font-size: 11px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }\n.crop-dot { fill: #fff; stroke: var(--pc, #fff); stroke-width: 2; filter: drop-shadow(0 0 5px var(--pc, #fff)); }\n.heat-layer { mix-blend-mode: screen; pointer-events: none; }\n.heat { opacity: 0.22; filter: blur(9px); }\n.scatter { filter: drop-shadow(0 0 2px #fff); }\n\n/* Phone \u2014 DartsKEY-inspired */\n.key-head { display: flex; align-items: baseline; justify-content: space-between; gap: 12px; }\n.key-mode { font-size: 20px; font-weight: 800; letter-spacing: -0.05em; }\n.key-meta { font-size: 11px; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: var(--muted); }\n.key-hero-wrap { position: relative; isolation: isolate; }\n.key-halo { position: absolute; inset: 0; }\n.key-hero {\n  position: relative;\n  display: flex;\n  flex-direction: column;\n  gap: 4px;\n  min-height: 176px;\n  padding: 12px 112px 10px 14px;\n  border-radius: 10px;\n  overflow: hidden;\n  background: color-mix(in srgb, var(--card-background-color, #1c1c1e) 82%, var(--pc) 8%);\n  clip-path: polygon(0 14px, 18px 0, 100% 0, 100% 100%, 0 100%);\n  border: 1px solid color-mix(in srgb, var(--pc) 30%, transparent);\n}\n.key-left { display: flex; gap: 10px; align-items: center; z-index: 1; max-width: 100%; }\n.key-name { font-size: 15px; font-weight: 800; letter-spacing: -0.02em; text-shadow: 0 0 10px color-mix(in srgb, var(--pc) 35%, transparent); }\n.key-mini { display: flex; flex-direction: column; gap: 2px; margin-top: 4px; font-size: 10px; font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--muted); }\n.key-mini b { color: var(--ink); font-weight: 800; letter-spacing: 0; text-transform: none; }\n.key-score { position: relative; z-index: 1; text-align: center; margin-top: auto; pointer-events: none; }\n.key-score .prev {\n  display: block; font-size: 16px; font-weight: 700; color: var(--muted);\n  text-decoration: line-through; text-decoration-thickness: 2px; opacity: 0.75;\n}\n.key-score .now {\n  font-size: 72px; font-weight: 800; letter-spacing: -0.08em; line-height: 0.82;\n  font-variant-numeric: tabular-nums;\n  text-shadow:\n    0 0 8px color-mix(in srgb, var(--pc) 50%, transparent),\n    0 0 22px color-mix(in srgb, var(--pc) 28%, transparent);\n}\n.key-opp {\n  position: absolute; top: 0; right: 0; z-index: 2;\n  min-width: 88px; padding: 8px 12px 10px 28px;\n  clip-path: polygon(22% 0, 100% 0, 100% 100%, 0 100%);\n  background: color-mix(in srgb, var(--card-background-color, #111) 70%, #000 30%);\n  border-left: 1px solid color-mix(in srgb, var(--primary-text-color, #fff) 12%, transparent);\n  text-align: right;\n}\n.key-opp span { display: block; font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); }\n.key-opp b { display: block; font-size: 22px; font-weight: 800; letter-spacing: -0.04em; font-variant-numeric: tabular-nums; }\n.key-visit { display: grid; grid-template-columns: 64px 1fr; gap: 8px; align-items: stretch; }\n.turn-total {\n  display: flex; flex-direction: column; align-items: center; justify-content: center;\n  border: 1px solid var(--line); border-radius: 8px;\n  box-shadow: 0 0 12px color-mix(in srgb, var(--pc) 14%, transparent);\n}\n.turn-total small { font-size: 9px; font-weight: 700; letter-spacing: 0.04em; color: var(--muted); text-align: center; padding: 0 2px; line-height: 1.2; }\n.turn-total b { font-size: 26px; font-weight: 800; letter-spacing: -0.04em; font-variant-numeric: tabular-nums; }\n.key-darts { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }\n.key-dart {\n  min-height: 64px; border: 1px solid var(--line); border-radius: 8px;\n  display: flex; flex-direction: column; align-items: center; justify-content: center;\n  background: color-mix(in srgb, var(--card-background-color, #1c1c1e) 70%, transparent);\n}\n.key-dart b { font-size: 22px; font-weight: 800; letter-spacing: -0.04em; }\n.key-dart small { font-size: 11px; font-weight: 600; color: var(--muted); }\n.key-dart.on {\n  border-color: color-mix(in srgb, var(--pc) 50%, transparent);\n  box-shadow: 0 0 14px color-mix(in srgb, var(--pc) 22%, transparent);\n}\n.key-dart.on b { text-shadow: 0 0 10px color-mix(in srgb, var(--pc) 45%, transparent); }\n.key-dart.empty { border-style: dashed; color: var(--muted); font-size: 10px; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }\n.key-bar {\n  display: flex; align-items: center; gap: 6px;\n  padding: 8px 4px 4px;\n  border-top: 1px solid color-mix(in srgb, var(--primary-color, var(--accent)) 22%, transparent);\n  box-shadow: 0 -1px 12px color-mix(in srgb, var(--primary-color, var(--accent)) 8%, transparent);\n}\n.key-turn {\n  flex: 1; text-align: center;\n  font-size: 13px; font-weight: 800; letter-spacing: 0.04em; text-transform: none;\n  text-shadow: 0 0 10px color-mix(in srgb, var(--pc) 40%, transparent);\n}\n.hitlbl b {\n  text-shadow: 0 0 12px color-mix(in srgb, var(--pc, var(--primary-color)) 35%, transparent);\n}\n\n/* Neon hairlines on key dividers */\n.section-h { border-bottom-color: color-mix(in srgb, var(--primary-color, var(--accent)) 22%, var(--line)); }\n\n@media (max-width: 1400px) {\n  .main { padding: 16px 24px 28px 20px; }\n  .game-omni { gap: 16px 24px; }\n  .pl-score { font-size: clamp(48px, 6vw, 80px); }\n}\n@media (max-width: 900px) {\n  .app {\n    min-height: 0;\n    height: auto;\n    overflow: visible;\n  }\n  .stage {\n    grid-template-columns: 1fr;\n    grid-template-rows: auto auto;\n    grid-template-areas: \"top\" \"main\";\n    min-height: 0;\n    height: auto;\n    overflow: visible;\n  }\n  .rail { display: none; }\n  .stage > .top, .top {\n    display: grid;\n    grid-area: top;\n    grid-template-columns: 1fr auto;\n    grid-template-areas: \"brand status\" \"nav nav\";\n    gap: 4px 12px;\n    padding: 12px 16px 0;\n  }\n  .brand { grid-area: brand; padding-bottom: 4px; }\n  .nav { grid-area: nav; justify-content: space-between; width: 100%; gap: 0; }\n  .nav button { font-size: 11px; padding: 10px 2px 14px; letter-spacing: 0.02em; min-width: 0; flex: 1 1 0; }\n  .status { grid-area: status; padding-bottom: 4px; }\n  .main {\n    padding: 12px 16px 16px;\n    overflow: visible;\n    height: auto;\n    max-height: none;\n    min-height: 0;\n    scroll-padding-bottom: var(--arena-footer-clear);\n  }\n  .game-omni { display: none; }\n  .game-key { display: flex; flex-direction: column; gap: 12px; height: auto; overflow: visible; padding-bottom: var(--arena-footer-clear); }\n  .key-bar {\n    position: fixed;\n    left: 0;\n    right: 0;\n    bottom: 0;\n    z-index: 20;\n    background: color-mix(in srgb, var(--card-background-color, #16181e) 94%, #000 6%);\n    padding: 8px 12px max(12px, env(safe-area-inset-bottom, 0px));\n    margin: 0;\n    border-top: 1px solid color-mix(in srgb, var(--primary-color, var(--accent)) 22%, transparent);\n  }\n  .key-board { max-height: none; overflow: hidden; }\n  .key-board .board-art { width: min(100%, calc(min(38vh, 300px) + 36px)); }\n  .key-board .board-art svg { width: 100%; height: auto; max-height: none; }\n  .key-bar, .play-actions { overflow: visible; }\n  .score { font-size: clamp(64px, 18vw, 96px); }\n  .pal { width: calc(50% - 4px); }\n  .wash-player, .wash-ring { opacity: 0.16; }\n}\n@media (max-height: 850px) and (min-width: 901px) {\n  .main { padding-top: 12px; padding-bottom: 16px; }\n  .pl-score { font-size: clamp(48px, 8vh, 84px); }\n}\n@media (prefers-reduced-motion: reduce) {\n  .lights, .lights *, .wash, .edge, .rim-aura, .rim-glow, .who .name, .row.cur .nm, .row.cur::after, .score, .board-side svg,\n  .pl.cur, .halo-glow, .halo-ring, .key-halo, .key-hero-wrap.cur .key-halo,\n  .dart-pin-wrap.drop-in .dart-drop, .dart-card.just-landed, .key-dart.just-landed {\n    animation: none !important;\n    transition: none !important;\n  }\n  .lights.is-hit .wash-hit { opacity: 0.16; transform: translate(-50%, -50%) scale(1); }\n  .wash-player, .wash-ring, .wash-accent { transform: none; }\n  .pl.cur .halo-glow, .key-hero-wrap.cur .halo-glow {\n    background: radial-gradient(circle, color-mix(in srgb, var(--pc) 40%, transparent), transparent 70%);\n    filter: blur(16px);\n    opacity: 0.4;\n  }\n}\n\n.key-hero-wrap.idle .key-score { display: none; }\n.key-hero-wrap.idle .key-hero { min-height: 0; padding-bottom: 16px; }\n.row-main {\n  appearance: none; background: none; border: 0; color: inherit; font: inherit;\n  display: grid; grid-template-columns: 3px 1fr auto; gap: 16px; align-items: center;\n  width: 100%; text-align: left; cursor: pointer; padding: 0;\n}\n.roster .row { display: flex; align-items: center; gap: 8px; }\n.swatch-chip { width: 28px; height: 28px; border-radius: 4px; flex: 0 0 28px; }\n.badge strong:empty { display: none; }\n\nbutton.dart-card, button.key-dart {\n  appearance: none; color: inherit; font: inherit; padding: 0; cursor: pointer;\n  text-align: inherit; width: 100%;\n}\n.dart-card svg, .key-dart svg { pointer-events: none; }\n.dart-card.empty svg, .key-dart.empty svg { opacity: 0.55; }\n.dart-card .wait, .key-dart .wait {\n  letter-spacing: 0.04em; font-size: 11px; font-weight: 700; color: var(--muted);\n  width: 100%; text-align: center; text-transform: none;\n}\n.dart-card.just-landed, .key-dart.just-landed {\n  animation: cropPulse 0.9s ease-out 1;\n}\n.dart-card.focus, .key-dart.focus, .key-dart.latest, .dart-card.latest {\n  border-color: color-mix(in srgb, var(--pc) 70%, transparent);\n  box-shadow: 0 0 16px color-mix(in srgb, var(--pc) 26%, transparent);\n}\n@keyframes cropPulse {\n  0% { box-shadow: 0 0 0 0 color-mix(in srgb, var(--pc) 48%, transparent); }\n  45% { box-shadow: 0 0 18px 3px color-mix(in srgb, var(--pc) 40%, transparent); }\n  100% { box-shadow: 0 0 0 0 transparent; }\n}\n.key-darts .dart-card { min-height: 86px; }\n.key-darts .dart-card svg { height: 76px; width: 100%; display: block; background: #14161c; }\n.key-darts .dc-meta { width: 100%; padding: 4px 6px 6px; }\n.board-side.idle .rim-aura, .board-side.idle .rim-glow {\n  stroke: var(--board-glow, var(--accent-color, var(--primary-color)));\n}\n.dart-aura {\n  fill: var(--dc, var(--pc, var(--accent-color)));\n  opacity: 0.34;\n  filter: blur(2.3px);\n}\n.dart-flight {\n  fill: color-mix(in srgb, var(--dc, var(--pc, var(--accent-color))) 78%, #fff);\n  stroke: color-mix(in srgb, var(--dc, var(--pc)) 35%, #fff);\n  stroke-width: 0.25;\n  filter: drop-shadow(0 0 2.1px color-mix(in srgb, var(--dc, var(--pc)) 70%, transparent));\n}\n.dart-flight.back {\n  fill: color-mix(in srgb, var(--dc, var(--pc)) 50%, #1a1a1e);\n  opacity: 0.92;\n  filter: none;\n}\n.dart-barrel {\n  fill: color-mix(in srgb, var(--dc, var(--pc)) 28%, #d8dce3);\n  stroke: color-mix(in srgb, var(--ink, #111) 20%, #fff);\n  stroke-width: 0.2;\n}\n.dart-grip { fill: color-mix(in srgb, var(--dc, var(--pc)) 20%, #9aa0ab); }\n.dart-shaft { fill: #f3f5f8; }\n.dart-tip {\n  fill: #f7f8fb;\n  filter: drop-shadow(0 0 1.5px color-mix(in srgb, var(--dc, var(--pc)) 80%, transparent));\n}\n.dart-pin-wrap.drop-in .dart-drop {\n  animation: dartDrop 0.48s cubic-bezier(.2,.75,.25,1) both;\n  transform-box: fill-box;\n  transform-origin: center top;\n}\n@keyframes dartDrop {\n  0% { transform: translateY(-26px) scale(1.16); opacity: 0; }\n  72% { transform: translateY(1.4px) scale(1); opacity: 1; }\n  100% { transform: translateY(0) scale(1); opacity: 1; }\n}\n.dart-pin-wrap.is-focus .dart-aura { opacity: 0.55; }\n.dart-pin-wrap.is-focus .dart-pin {\n  filter: drop-shadow(0 0 4px color-mix(in srgb, var(--dc, var(--pc)) 75%, transparent));\n}\n\n.lights, .lights *, .wash, .edge, .edge i, .halo, .key-halo, .halo-wrap, .halo-glow, .halo-ring,\n.row.cur::after, .rim-aura, .rim-glow,\n.dart-pin-wrap, .dart-drop, .dart-pin, .heat-layer, .scatter-layer {\n  pointer-events: none !important;\n}\nbutton, input, select, textarea, a, .dart-card, .key-dart, .row-main, .toggle, .swatch, .pal, .nav button, .rail-nav button {\n  pointer-events: auto;\n  touch-action: manipulation;\n}\n.modal-bg { pointer-events: auto; }\n\n.offline-badge {\n  display: inline-block;\n  margin-left: 8px;\n  padding: 2px 8px;\n  font-size: 10px;\n  font-weight: 700;\n  letter-spacing: 0.06em;\n  color: var(--muted, #b4b8c2);\n  border: 1px solid color-mix(in srgb, var(--primary-text-color, #fff) 22%, transparent);\n  border-radius: 999px;\n  background: color-mix(in srgb, var(--card-background-color, #16181e) 60%, transparent);\n  vertical-align: middle;\n}\n.status .dot.off { background: var(--muted, #b4b8c2); }\n\n.lights, .lights *, .wash, .edge, .rim-aura, .rim-glow, .key-halo, .halo-wrap, .halo-glow, .halo-ring, .who .halo {\n  pointer-events: none !important;\n}\n.nav, .rail-nav, .nav button, .rail-nav button, .play-actions, .modes, .section, .section-h {\n  position: relative;\n  z-index: 2;\n}\n\n@media (max-width: 900px) {\n  .key-bar {\n    position: fixed !important;\n    left: 0;\n    right: 0;\n    bottom: 0;\n    z-index: 20 !important;\n  }\n}\n\n/* data-act pointer fix: designed controls must receive taps. Do not cover them. */\nbutton, .swatch, .pal, .toggle, input[type=\"range\"], input[type=\"text\"], [data-act], [data-act-change], [data-act-blur], [data-act-key] {\n  pointer-events: auto !important;\n  touch-action: manipulation;\n  cursor: pointer;\n}\ninput[type=\"range\"], input[type=\"text\"] { cursor: auto; }\ninput[type=\"range\"] { cursor: pointer; }\n\n\n@media (max-width: 900px) {\n  .stage > .top, .top {\n    position: sticky;\n    top: 0;\n    z-index: 15;\n    background: color-mix(in srgb, var(--card-background-color, #16181e) 94%, #000 6%);\n  }\n  .key-visit, .key-darts, .dart-card, .key-dart, .dart-tray, .key-hero-wrap {\n    position: relative;\n    z-index: 3;\n  }\n  .key-board { position: relative; z-index: 0; overflow: hidden; }\n}\n\n/* Room WLED units */\n.wled-unit { margin-top: 8px; }\n.wled-h {\n  display: flex; align-items: center; justify-content: space-between; gap: 12px;\n  padding: 8px 0 10px; border-bottom: 1px solid var(--line);\n}\n.wled-name {\n  appearance: none; background: transparent; border: 0; color: inherit;\n  font: inherit; display: inline-flex; align-items: center; gap: 8px;\n  cursor: pointer; padding: 0; margin: 0;\n  font-size: 13px; font-weight: 650; letter-spacing: 0.08em;\n}\n.wled-name svg { width: 16px; height: 16px; flex: 0 0 16px; transition: transform var(--ease); }\n.wled-unit:not(.open) .wled-name svg { transform: rotate(-90deg); }\n.wled-unit:not(.open) .wled-body { display: none; }\n.wled-body { padding-top: 12px; }\n\n.halo-wrap, .key-halo, .halo-glow, .halo-ring { display: none !important; }\n\n.glow-swatch {\n  display: block; width: 22px; height: 22px; border-radius: 50%;\n  box-shadow: 0 0 8px color-mix(in srgb, currentColor 35%, transparent);\n  flex: 0 0 22px;\n}\n.glow-row .icon-tile { min-width: 56px; }\n";
const DARTS_PALETTES = [{"name": "Default", "gradient": "linear-gradient(90deg, #ff0000 0%, #ffbf00 12%, #80ff00 25%, #00ff40 38%, #00ffff 50%, #0046ff 62%, #7a00ff 75%, #ff00c5 88%, #ff0006 100%)"}, {"name": "Color 1", "gradient": "linear-gradient(90deg, #ffffff 0%, #ffffff 12%, #ffffff 25%, #ffffff 38%, #ffffff 50%, #ffffff 62%, #ffffff 75%, #ffffff 88%, #ffffff 100%)"}, {"name": "Colors 1&2", "gradient": "linear-gradient(90deg, #ffffff 0%, #ffffff 12%, #ffffff 25%, #ffffff 38%, #0000ff 50%, #0000ff 62%, #0000ff 75%, #0000ff 88%, #0000ff 100%)"}, {"name": "Color Gradient", "gradient": "linear-gradient(90deg, #ffffff 0%, #bfbfff 12%, #8080ff 25%, #4040ff 38%, #0000ff 50%, #3e3eff 62%, #7e7eff 75%, #bdbdff 88%, #fdfdff 100%)"}, {"name": "Rainbow", "gradient": "linear-gradient(90deg, #ff0000 0%, #ffbf00 12%, #80ff00 25%, #00ff40 38%, #00ffff 50%, #0046ff 62%, #7a00ff 75%, #ff00c5 88%, #ff0006 100%)"}, {"name": "Rainbow Bands", "gradient": "linear-gradient(90deg, #ff0000 0%, #ffbf00 12%, #80ff00 25%, #00ff40 38%, #00ffff 50%, #00ffff 62%, #0040ff 75%, #8000ff 88%, #ff00bf 100%)"}, {"name": "Party", "gradient": "linear-gradient(90deg, #5500ab 0%, #84007c 7%, #b5004b 13%, #e5001b 20%, #e81700 27%, #b84700 33%, #ab7700 40%, #abab00 47%, #ab5500 53%, #dd2200 60%, #f2000e 67%, #c2003e 73%, #8f0071 80%, #5f00a1 87%, #2d00d2 93%, #0007f9 100%)"}, {"name": "Cloud", "gradient": "linear-gradient(90deg, #0000ff 0%, #00008b 7%, #00008b 13%, #00008b 20%, #00008b 27%, #00008b 33%, #00008b 40%, #00008b 47%, #0000ff 53%, #00008b 60%, #87ceeb 67%, #87ceeb 73%, #add8e6 80%, #ffffff 87%, #add8e6 93%, #87ceeb 100%)"}, {"name": "Lava", "gradient": "linear-gradient(90deg, #000000 0%, #800000 7%, #000000 13%, #800000 20%, #8b0000 27%, #800000 33%, #8b0000 40%, #8b0000 47%, #8b0000 53%, #ff0000 60%, #ffa500 67%, #ffffff 73%, #ffa500 80%, #ff0000 87%, #8b0000 93%, #000000 100%)"}, {"name": "Ocean", "gradient": "linear-gradient(90deg, #191970 0%, #00008b 7%, #191970 13%, #000080 20%, #00008b 27%, #0000cd 33%, #2e8b57 40%, #008080 47%, #5f9ea0 53%, #0000ff 60%, #008b8b 67%, #6495ed 73%, #7fffd4 80%, #2e8b57 87%, #00ffff 93%, #87cefa 100%)"}, {"name": "Forest", "gradient": "linear-gradient(90deg, #006400 0%, #006400 7%, #556b2f 13%, #006400 20%, #008000 27%, #228b22 33%, #6b8e23 40%, #008000 47%, #2e8b57 53%, #66cdaa 60%, #32cd32 67%, #9acd32 73%, #90ee90 80%, #7cfc00 87%, #66cdaa 93%, #228b22 100%)"}, {"name": "Heat", "gradient": "linear-gradient(90deg, #000000 0%, #ff0000 33%, #ffff00 67%, #ffffff 100%)"}, {"name": "Sunset", "gradient": "linear-gradient(90deg, #780000 0%, #b31600 9%, #ff6800 20%, #a71612 33%, #640067 53%, #100082 78%, #0000a0 100%)"}, {"name": "Rivendell", "gradient": "linear-gradient(90deg, #010e05 0%, #10240e 40%, #38441e 65%, #969c63 95%, #969c63 100%)"}, {"name": "Breeze", "gradient": "linear-gradient(90deg, #010607 0%, #01636f 35%, #90d1ff 60%, #004952 100%)"}, {"name": "Red & Blue", "gradient": "linear-gradient(90deg, #ff0000 0%, #ff0000 25%, #0000ff 38%, #0000ff 63%, #ff0000 75%, #ff0000 100%)"}, {"name": "Yellowout", "gradient": "linear-gradient(90deg, #bc8701 0%, #2e0701 100%)"}, {"name": "Analogous", "gradient": "linear-gradient(90deg, #0300ff 0%, #1700ff 25%, #4300ff 50%, #8e002d 75%, #ff0000 100%)"}, {"name": "Splash", "gradient": "linear-gradient(90deg, #7e0bff 0%, #c50116 50%, #d29dac 69%, #9d0370 87%, #9d0370 100%)"}, {"name": "Pastel", "gradient": "linear-gradient(90deg, #0a3e7b 0%, #388267 14%, #99e155 34%, #c7d944 39%, #ffcf36 42%, #f79839 45%, #ef6b3d 47%, #f79839 50%, #ffcf36 71%, #ffe955 100%)"}, {"name": "Sunset 2", "gradient": "linear-gradient(90deg, #6e310b 0%, #37220a 11%, #161609 27%, #ef7c08 27%, #dc9c1b 38%, #cbc13d 49%, #213538 70%, #000134 100%)"}, {"name": "Beach", "gradient": "linear-gradient(90deg, #fffcd6 0%, #fffcd6 9%, #bebf73 10%, #898d34 11%, #70ffcd 11%, #33f6d6 20%, #11ebe2 28%, #02c1c7 36%, #009cae 47%, #016573 52%, #013b47 53%, #0783aa 54%, #015a97 82%, #003885 100%)"}, {"name": "Vintage", "gradient": "linear-gradient(90deg, #040101 0%, #100001 20%, #616803 30%, #ff8313 40%, #430904 50%, #100001 60%, #040101 90%, #040101 100%)"}, {"name": "Departure", "gradient": "linear-gradient(90deg, #080300 0%, #170700 16%, #4b2606 25%, #a96326 33%, #d5a977 42%, #ffffff 45%, #87ff8a 54%, #16ff18 58%, #00ff00 67%, #008800 75%, #003700 83%, #003700 100%)"}, {"name": "Landscape", "gradient": "linear-gradient(90deg, #000000 0%, #021901 15%, #0f7305 30%, #4fd501 50%, #7ed32f 50%, #bcd1f7 51%, #90b6cd 60%, #3b75fa 80%, #0125c0 100%)"}, {"name": "Sherbet", "gradient": "linear-gradient(90deg, #ff2104 0%, #ff4419 17%, #ff0719 34%, #ff5267 50%, #fffff2 67%, #2aff16 82%, #57ff41 100%)"}, {"name": "Hult", "gradient": "linear-gradient(90deg, #f7b0f7 0%, #ff88ff 19%, #dc1de2 35%, #0752b2 63%, #017c6d 85%, #017c6d 100%)"}, {"name": "Drywet", "gradient": "linear-gradient(90deg, #776121 0%, #ebc758 16%, #a9ee7c 33%, #25eee8 50%, #0778ec 67%, #1b01af 83%, #043365 100%)"}, {"name": "Jul", "gradient": "linear-gradient(90deg, #e2060c 0%, #1a604e 37%, #82bd5e 52%, #b10309 100%)"}, {"name": "Grintage", "gradient": "linear-gradient(90deg, #020101 0%, #120100 21%, #451d01 41%, #a7870a 60%, #2e3804 100%)"}, {"name": "Rewhi", "gradient": "linear-gradient(90deg, #715b93 0%, #9d584e 28%, #d05521 35%, #ff1d0b 42%, #891f27 55%, #3b2159 100%)"}, {"name": "Tertiary", "gradient": "linear-gradient(90deg, #0001ff 0%, #03442d 25%, #17ff00 50%, #644401 75%, #ff0104 100%)"}, {"name": "Fire", "gradient": "linear-gradient(90deg, #000000 0%, #4d0000 18%, #b10000 38%, #c42609 42%, #d74c13 47%, #eb731d 57%, #ff9929 68%, #ffb229 74%, #ffcc29 79%, #ffe629 85%, #ffff29 92%, #ffff8f 96%, #ffffff 100%)"}, {"name": "Icefire", "gradient": "linear-gradient(90deg, #000000 0%, #00092d 23%, #0026ff 47%, #0364ff 58%, #17c7ff 71%, #64ebff 85%, #ffffff 100%)"}, {"name": "Ice", "gradient": "linear-gradient(90deg, #001040 0%, #0050c8 39%, #00a0ff 67%, #c8f0ff 100%)"}, {"name": "Cyane", "gradient": "linear-gradient(90deg, #0a5505 0%, #1d6d12 10%, #3b8a2a 24%, #536334 36%, #6e4240 42%, #7b3141 43%, #8b2342 44%, #c07562 45%, #ffff89 49%, #64b49b 66%, #1679ae 100%)"}, {"name": "Light Pink", "gradient": "linear-gradient(90deg, #130227 0%, #1a042d 10%, #210634 20%, #443e7d 30%, #76bbf0 40%, #a3d7f7 43%, #d9f4ff 45%, #9f95dd 48%, #714ebc 58%, #80399b 72%, #92287b 100%)"}, {"name": "Autumn", "gradient": "linear-gradient(90deg, #1a0101 0%, #430401 20%, #760e01 33%, #899834 41%, #714101 44%, #85953b 48%, #899834 49%, #714101 53%, #8b9a2e 56%, #710d01 64%, #370301 80%, #110101 98%, #110101 100%)"}, {"name": "Magenta", "gradient": "linear-gradient(90deg, #000000 0%, #00002d 16%, #0000ff 33%, #2a00ff 50%, #ff00ff 67%, #ff37ff 83%, #ffffff 100%)"}, {"name": "Magred", "gradient": "linear-gradient(90deg, #000000 0%, #2a002d 25%, #ff00ff 50%, #ff002d 75%, #ff0000 100%)"}, {"name": "Yelmag", "gradient": "linear-gradient(90deg, #000000 0%, #2a0000 16%, #ff0000 33%, #ff002d 50%, #ff00ff 67%, #ff372d 83%, #ffff00 100%)"}, {"name": "Yelblu", "gradient": "linear-gradient(90deg, #0000ff 0%, #0037ff 25%, #00ffff 50%, #2aff2d 75%, #ffff00 100%)"}, {"name": "Orange & Teal", "gradient": "linear-gradient(90deg, #00965c 0%, #00965c 22%, #ff4800 78%, #ff4800 100%)"}, {"name": "Tiamat", "gradient": "linear-gradient(90deg, #01020e 0%, #020523 13%, #0d875c 39%, #2bffc1 47%, #f707f9 55%, #c111d0 63%, #27ff9a 71%, #04d5ec 78%, #27fc87 86%, #c1d5fd 94%, #fff9ff 100%)"}, {"name": "April Night", "gradient": "linear-gradient(90deg, #01052d 0%, #01052d 4%, #05a9af 10%, #01052d 16%, #01052d 24%, #2daf1f 30%, #01052d 36%, #01052d 44%, #f99605 50%, #01052d 56%, #01052d 64%, #ff5c00 70%, #01052d 76%, #01052d 84%, #df2d48 90%, #01052d 96%, #01052d 100%)"}, {"name": "Orangery", "gradient": "linear-gradient(90deg, #ffad17 0%, #ff5200 14%, #ff2000 27%, #ff5200 41%, #9e0d0b 55%, #ff5200 69%, #ff2000 82%, #ff5200 100%)"}, {"name": "C9", "gradient": "linear-gradient(90deg, #b80400 0%, #b80400 24%, #902c02 25%, #902c02 49%, #046002 51%, #046002 75%, #070758 76%, #070758 100%)"}, {"name": "Sakura", "gradient": "linear-gradient(90deg, #c4130a 0%, #ff452d 25%, #df2d48 51%, #ff5267 76%, #df0d11 100%)"}, {"name": "Aurora", "gradient": "linear-gradient(90deg, #01052d 0%, #00c817 25%, #00ff00 50%, #00f32d 67%, #008707 78%, #01052d 100%)"}, {"name": "Atlantica", "gradient": "linear-gradient(90deg, #001c70 0%, #2060ff 20%, #00f32d 39%, #0c5f52 59%, #19be5f 78%, #28aa50 100%)"}, {"name": "Temperature", "gradient": "linear-gradient(90deg, #011b69 0%, #01287f 5%, #0146a8 11%, #015cc5 16%, #0177dd 22%, #038297 27%, #179c95 33%, #43b670 39%, #79c934 44%, #8ecb0b 50%, #e0df01 55%, #fcbb02 61%, #f79301 67%, #ed5701 72%, #e52b01 78%, #ab0202 89%, #500303 94%, #500303 100%)"}, {"name": "Retro Clown", "gradient": "linear-gradient(90deg, #e36503 0%, #c21213 46%, #5c08c0 100%)"}, {"name": "Candy", "gradient": "linear-gradient(90deg, #e5e301 0%, #e36503 6%, #280150 56%, #11014f 78%, #00002d 100%)"}, {"name": "Toxy Reaf", "gradient": "linear-gradient(90deg, #01dd35 0%, #4903b2 100%)"}, {"name": "Fairy Reaf", "gradient": "linear-gradient(90deg, #b80180 0%, #01c1b6 63%, #99e3be 86%, #ffffff 100%)"}, {"name": "Semi Blue", "gradient": "linear-gradient(90deg, #000000 0%, #010103 5%, #080116 21%, #040659 31%, #0219d8 47%, #070a63 57%, #0f021f 73%, #020105 91%, #000000 100%)"}, {"name": "Pink Candy", "gradient": "linear-gradient(90deg, #ffffff 0%, #070cff 18%, #e3017f 44%, #e3017f 55%, #ffffff 61%, #e3017f 77%, #2d0163 100%)"}, {"name": "Red Reaf", "gradient": "linear-gradient(90deg, #030d2b 0%, #4e8df0 41%, #ff0000 74%, #1c0101 100%)"}, {"name": "Aqua Flash", "gradient": "linear-gradient(90deg, #000000 0%, #39e3e9 26%, #ffff08 38%, #ffffff 49%, #ffff08 60%, #39e3e9 74%, #000000 100%)"}, {"name": "Yelblu Hot", "gradient": "linear-gradient(90deg, #040209 0%, #10002f 23%, #180010 48%, #900901 62%, #b32d01 72%, #dc7202 86%, #eaed01 100%)"}, {"name": "Red Flash", "gradient": "linear-gradient(90deg, #000000 0%, #e30101 39%, #f9c75f 51%, #e30101 61%, #000000 100%)"}, {"name": "Red Shift", "gradient": "linear-gradient(90deg, #1f011b 0%, #220110 18%, #890509 39%, #d5800a 52%, #c71601 69%, #c70906 79%, #010001 100%)"}, {"name": "Red Tide", "gradient": "linear-gradient(90deg, #f70500 0%, #ff4301 11%, #ea580b 17%, #eab033 23%, #e51c01 33%, #710c01 45%, #ffe12c 55%, #710c01 66%, #f4d158 77%, #ff1c01 85%, #350101 100%)"}, {"name": "Candy2", "gradient": "linear-gradient(90deg, #272122 0%, #04060f 10%, #311d16 19%, #e0ad01 29%, #b12305 35%, #04060f 51%, #ff7206 64%, #e0ad01 73%, #272122 83%, #010101 100%)"}];
const PAL = ['#ff3b30', '#0a84ff', '#30d158', '#ffd60a', '#bf5af2', '#ff9f0a', '#64d2ff', '#ff375f'];
const NAMED = { red: '#ff3b30', blue: '#0a84ff', green: '#30d158', yellow: '#ffd60a', purple: '#bf5af2', orange: '#ff9f0a', cyan: '#64d2ff', pink: '#ff375f', white: '#ffffff', teal: '#40c8e0', lime: '#a3e635', gold: '#ffc300' };
const COLOR1 = [
  ['Red', '#ff0000', [255, 0, 0]], ['Orange', '#ff6000', [255, 96, 0]], ['Yellow', '#ffff00', [255, 255, 0]],
  ['Green', '#00ff00', [0, 255, 0]], ['Cyan', '#00ffff', [0, 255, 255]], ['Blue', '#0000ff', [0, 0, 255]],
  ['Purple', '#8000ff', [128, 0, 255]], ['Magenta', '#ff00ff', [255, 0, 255]], ['Pink', '#ff0080', [255, 0, 128]],
  ['White', '#ffffff', [255, 255, 255]]
];
const RING_FX = ['Solid', 'Blink', 'Breathe', 'Heartbeat', 'Wave', 'Color Cycle', 'Palette Steps', 'Chase', 'Rainbow Chase', 'Circular Rainbow', 'Rainbow Sweep', 'Bounce', 'Circular Wipe', 'Twinkle', 'Fire Flicker', 'Police', 'Lightning'];
const TREE_FX = ['Solid', 'Blink', 'Breathe', 'Wipe', 'Sweep', 'Rainbow', 'Colorloop', 'Fire Flicker', 'Fireworks', 'Twinkle', 'Sparkle', 'Chase', 'Scan', 'Meteor', 'Colortwinkles', 'Pride 2015'];
const MODES = [
  ['301', { game: 'x01', start: '301' }, 'Start A New 301 Game?'],
  ['501', { game: 'x01', start: '501' }, 'Start A New 501 Game?'],
  ['Cricket', { game: 'cricket' }, 'Start A New Cricket Game?'],
  ['Count-Up', { game: 'count_up' }, 'Start A New Count-Up Game?'],
  ['Around The Clock', { game: 'around_the_clock' }, 'Start A New Around The Clock Game?']
];
const TABS = [
  ['game', 'Game'], ['players', 'Players'], ['ring', 'Ring'],
  ['room', 'Room'], ['sounds', 'Sounds'], ['settings', 'Settings']
];
/* DARTS_CONFIG — live defaults. Public templates override window.DARTS_CONFIG
 * (prefix, optional wled, newGameScript). wled: null hides Tree Lights.
 * newGameScript empty => granboard.new_game with the current roster. */
let DARTS_CONFIG = Object.assign({
  prefix: 'game_room_granboard_3s',
  newGameScript: 'darts_preview_new_game',
  helpers: {
    players: 'input_text.darts_players',
    colors: 'input_text.darts_colors',
    double: 'input_boolean.darts_double_out'
  },
  wled: {
    light: 'light.wled_4',
    palette: 'select.wled_color_palette_3',
    preset: 'select.wled_preset_3',
    intensity: 'number.wled_intensity_3',
    speed: 'number.wled_speed_3'
  }
}, (typeof window !== 'undefined' && window.DARTS_CONFIG) || {});
function firstWledCfg(cfg) {
  const w = cfg && cfg.wled;
  if (!w) return {};
  if (Array.isArray(w)) {
    const x = w[0];
    return typeof x === 'string' ? { light: x } : (x || {});
  }
  return w;
}
function wledOpenMap() {
  try { return JSON.parse(localStorage.getItem('dartsArenaWledOpen') || '{}') || {}; } catch (e) { return {}; }
}
function discoverWledParts(light, given) {
  const out = {
    palette: (given && given.palette) || '',
    preset: (given && given.preset) || '',
    intensity: (given && given.intensity) || '',
    speed: (given && given.speed) || ''
  };
  if (out.palette && out.preset && out.intensity && out.speed) return out;
  const hass = hassObj();
  const states = (hass && hass.states) || {};
  const entities = (hass && hass.entities) || {};
  const deviceId = (entities[light] || {}).device_id;
  const take = (eid) => {
    if (!eid || eid === light) return;
    const low = String(eid).toLowerCase();
    if (low.startsWith('select.') && /color_palette|palette/.test(low) && !/ring_palette/.test(low) && !out.palette) out.palette = eid;
    else if (low.startsWith('select.') && /preset/.test(low) && !out.preset) out.preset = eid;
    else if (low.startsWith('number.') && /intensity/.test(low) && !/ring_intensity/.test(low) && !out.intensity) out.intensity = eid;
    else if (low.startsWith('number.') && /speed/.test(low) && !/ring_speed/.test(low) && !out.speed) out.speed = eid;
  };
  if (deviceId) {
    Object.keys(entities).forEach(eid => { if (entities[eid] && entities[eid].device_id === deviceId) take(eid); });
    Object.keys(states).forEach(eid => {
      const stt = states[eid];
      if (stt && stt.attributes && stt.attributes.device_id === deviceId) take(eid);
    });
  }
  const stem = String(light).replace(/^light\./, '');
  const prefix = stem.replace(/_?\d+$/, '');
  Object.keys(states).forEach(eid => {
    if (prefix && eid.indexOf(prefix) !== -1) take(eid);
  });
  return out;
}
function wledUnits() {
  const raw = (typeof DARTS_CONFIG !== 'undefined' && DARTS_CONFIG.wled);
  if (raw == null) return [];
  const arr = Array.isArray(raw) ? raw : [raw];
  const hass = hassObj();
  return arr.map((item, i) => {
    const src = typeof item === 'string' ? { light: item } : (item || {});
    const light = src.light || src.entity || '';
    if (!light) return null;
    const parts = discoverWledParts(light, src);
    const stt = st(light);
    const friendly = (stt.attributes || {}).friendly_name || '';
    const name = src.name || friendly || (light === 'light.wled_4' ? 'Tree Lights' : light.replace(/^light\./, '').replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()));
    return { light, name, palette: parts.palette, preset: parts.preset, intensity: parts.intensity, speed: parts.speed, i };
  }).filter(Boolean);
}
function paletteBank() {
  if (typeof DARTS_PALETTES !== 'undefined' && DARTS_PALETTES && DARTS_PALETTES.length) return DARTS_PALETTES;
  if (typeof TREE_PALETTES !== 'undefined' && TREE_PALETTES && TREE_PALETTES.length) return TREE_PALETTES;
  return [];
}
function cfgEntities(cfg) {
  const p = cfg.prefix;
  const w = firstWledCfg(cfg);
  const h = cfg.helpers || {};
  return {
    game: 'sensor.' + p + '_game',
    last: 'sensor.' + p + '_last_hit',
    conn: 'binary_sensor.' + p + '_connected',
    sw: 'switch.' + p + '_granboard_connection',
    signal: 'sensor.' + p + '_signal_strength',
    release: 'button.' + p + '_release_board',
    players: h.players || 'input_text.darts_players',
    colors: h.colors || 'input_text.darts_colors',
    double: h.double || 'input_boolean.darts_double_out',
    theme: 'select.' + p + '_sound_theme',
    ring: 'light.' + p + '_led_ring',
    palette: 'select.' + p + '_ring_palette',
    color2: 'text.' + p + '_ring_color_2',
    speed: 'number.' + p + '_ring_speed',
    intensity: 'number.' + p + '_ring_intensity',
    tree: w.light || '',
    treePal: w.palette || '',
    treePreset: w.preset || '',
    treeSpeed: w.speed || '',
    treeInt: w.intensity || '',
    roster: 'sensor.' + p + '_players'
  };
}
let E = cfgEntities(DARTS_CONFIG);
function isVisualOnly() { return false; }


function st(id) {
  try {
    if (!id) return { state: '', attributes: {} };
    const hass = hassObj();
    const map = (hass && hass.states) ? hass.states : {};
    const e = map[id];
    if (!e || typeof e !== 'object') return { state: '', attributes: {} };
    return e;
  } catch (err) { return { state: '', attributes: {} }; }
}
function attr(id) {
  try {
    const a = st(id).attributes;
    return (a && typeof a === 'object') ? a : {};
  } catch (err) { return {}; }
}
function isUnavailable(id) {
  const s = String((st(id) || {}).state || '').toLowerCase();
  return !s || s === 'unavailable' || s === 'unknown';
}
function isBoardOffline() {
  return isUnavailable(E.game);
}
function esc(s) { return String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])); }
function helperCols() {
  return String(st(E.colors).state || '').split(',').map(x => x.trim().toLowerCase()).map(x => NAMED[x] || (/^#?[0-9a-f]{6}$/.test(x) ? (x[0] === '#' ? x : '#' + x) : ''));
}
function helperNames() {
  const roster = rosterEntries();
  if (roster.length) return roster.map(p => p.name);
  return String(st(E.players).state || '').split(',').map(x => x.trim()).filter(Boolean);
}
/* PLAYER PROFILES HOOK
 * When the integration exposes sensor.{device}_players (and later
 * granboard.add_player / update_player / remove_player / set_lineup),
 * the Players tab and roster read from that sensor. Until then this
 * returns [] and the dashboard falls back to input_text helpers.
 */
function rosterEntries() {
  const r = st(E.roster);
  if (!r || !r.state || r.state === 'unknown' || r.state === 'unavailable') return [];
  const attrs = r.attributes || {};
  // 0.4.0+ players sensor: lineup is tonight's throwing order; profiles are saved friends.
  const list = attrs.lineup || attrs.players || attrs.roster || attrs.profiles;
  if (!Array.isArray(list) || !list.length) return [];
  return list.map((p, i) => {
    if (p == null) return null;
    if (typeof p === 'string') return { name: p, color: '', id: p };
    const name = p.name || p.player || '';
    if (!name) return null;
    return { name, color: p.color || '', id: p.id || p.player_id || name, index: i };
  }).filter(Boolean);
}
function hasProfileServices() {
  return rosterEntries().length > 0 || (st(E.roster).state && st(E.roster).state !== 'unknown' && st(E.roster).state !== 'unavailable');
}
function gs() {
  try {
    const a = attr(E.game);
    return (a && typeof a === 'object') ? a : {};
  } catch (err) { return {}; }
}
function pcol(i) {
  const p = (gs().players || [])[i];
  return (p && p.color) || helperCols()[i] || PAL[(i || 0) % 8];
}
function tabName() {
  try {
    const card = typeof window !== 'undefined' && window.__dartsCard;
    if (card && card._section && TABS.some(t => t[0] === card._section)) return card._section;
    if (typeof window !== 'undefined' && window.__dartsSection && TABS.some(t => t[0] === window.__dartsSection)) return window.__dartsSection;
    const hash = (typeof location !== 'undefined' && (location.hash || '').replace('#', '')) || '';
    let stored = '';
    try { stored = (typeof localStorage !== 'undefined' && localStorage.getItem('dartsArenaTab')) || ''; } catch (e) { stored = ''; }
    const h = hash || stored || 'game';
    return TABS.some(t => t[0] === h) ? h : 'game';
  } catch (e) { return 'game'; }
}
function hassObj() {
  try {
    if (typeof window !== 'undefined' && window.__dartsHass) return window.__dartsHass;
    const card = typeof window !== 'undefined' && window.__dartsCard;
    if (card && (card.hass || card._hass)) {
      window.__dartsHass = card.hass || card._hass;
      return window.__dartsHass;
    }
    const ha = document.querySelector('home-assistant');
    if (ha && ha.hass) {
      window.__dartsHass = ha.hass;
      return ha.hass;
    }
  } catch (e) {}
  return null;
}
function appRoot() {
  try {
    const card = typeof window !== 'undefined' && window.__dartsCard;
    if (card && card.shadowRoot) {
      const el = card.shadowRoot.getElementById('darts-app') || card.shadowRoot.querySelector('#darts-app') || card.shadowRoot.getElementById('app');
      if (el) return el;
    }
    if (card && card.querySelector) {
      const el = card.querySelector('#darts-app') || card.querySelector('#app');
      if (el) return el;
    }
  } catch (e) {}
  try {
    if (typeof document !== 'undefined') {
      const el = document.getElementById('darts-app');
      if (el) return el;
    }
  } catch (e) {}
  return null;
}
function da(name) {
  const args = Array.prototype.slice.call(arguments, 1);
  const json = JSON.stringify(args).replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  return 'data-act="' + name + '" data-args="' + json + '"';
}
function daChange(name) {
  const args = Array.prototype.slice.call(arguments, 1);
  const json = JSON.stringify(args).replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  return 'data-act-change="' + name + '" data-args-change="' + json + '" onchange="return window.__dartsApi&&window.__dartsApi.run(this,event,\'change\')"';
}
function daBlur(name) {
  const args = Array.prototype.slice.call(arguments, 1);
  const json = JSON.stringify(args).replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  return 'data-act-blur="' + name + '" data-args-blur="' + json + '" onblur="return window.__dartsApi&&window.__dartsApi.run(this,event,\'blur\')"';
}
function daKey(name) {
  const args = Array.prototype.slice.call(arguments, 1);
  const json = JSON.stringify(args).replace(/&/g, '&amp;').replace(/"/g, '&quot;');
  return 'data-act-key="' + name + '" data-args-key="' + json + '" onkeydown="return window.__dartsApi&&window.__dartsApi.run(this,event,\'key\')"';
}
function slug(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, '_').replace(/^_|_$/g, '');
}
function ov(id) { return 'data-overlay="' + id + '"'; }
function overlayHost(card) {
  try {
    const root = card && card.shadowRoot;
    if (!root) return null;
    return root.querySelector('ha-card') || root;
  } catch (e) { return null; }
}
function syncOverlays(card) {
  try {
    const root = card && card.shadowRoot;
    if (!root) return;
    const host = overlayHost(card);
    if (!host) return;
    const hostR = host.getBoundingClientRect();
    const used = {};
    const nodes = root.querySelectorAll('[data-overlay]');
    nodes.forEach(target => {
      const id = 'ov_' + target.getAttribute('data-overlay');
      const field = root.getElementById(id);
      if (!field) return;
      used[id] = true;
      const hidden = !!(target.closest && target.closest('[hidden]'));
      const vis = !hidden && target.getClientRects && target.getClientRects().length > 0 && (target.offsetWidth > 0 || target.offsetHeight > 0);
      if (!vis) {
        field.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;opacity:0;pointer-events:none;overflow:hidden;z-index:0;';
        return;
      }
      const r = target.getBoundingClientRect();
      const left = r.left - hostR.left + (host.scrollLeft || 0);
      const top = r.top - hostR.top + (host.scrollTop || 0);
      field.style.cssText = 'position:absolute;left:' + left + 'px;top:' + top + 'px;width:' + r.width + 'px;height:' + r.height + 'px;opacity:0;pointer-events:auto;z-index:50;overflow:hidden;cursor:pointer;';
    });
    root.querySelectorAll('[id^="ov_"]').forEach(field => {
      if (!used[field.id]) {
        field.style.cssText = 'position:absolute;left:0;top:0;width:0;height:0;opacity:0;pointer-events:none;overflow:hidden;z-index:0;';
      }
    });
  } catch (e) { try { console.error(e); } catch (x) {} }
}
function scheduleBind(card) {
  if (typeof window === 'undefined') return;
  if (card) {
    window.__dartsCard = card;
    try { if (card.hass || card._hass) window.__dartsHass = card.hass || card._hass; } catch (e) {}
  }
  const run = () => {
    try {
      installApi(card || window.__dartsCard);
      bindCard(card || window.__dartsCard);
    } catch (e) {}
  };
  run();
  setTimeout(run, 0);
  setTimeout(run, 60);
  setTimeout(run, 250);
}

function bindOverlayTabs(card) {
  try {
    const root = card && card.shadowRoot;
    if (!root) return;
    root.querySelectorAll('[id^="ov_tab_"]').forEach(field => {
      if (field.__tabBound) return;
      field.__tabBound = true;
      field.addEventListener('click', ev => {
        const raw = String(field.id || '').replace(/^ov_tab_/, '');
        const name = raw.replace(/_top$/, '').replace(/_rail$/, '');
        ev.preventDefault();
        ev.stopPropagation();
        if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
        if (window.__dartsApi && name) window.__dartsApi.tab(name);
      });
    });
  } catch (e) {}
}

function parseActArgs(el, attr) {
  const raw = el && el.getAttribute && el.getAttribute(attr);
  if (!raw) return [];
  try {
    const v = JSON.parse(raw);
    return Array.isArray(v) ? v : [v];
  } catch (e) { return []; }
}
function findActEl(ev, names) {
  const path = (ev && ev.composedPath) ? ev.composedPath() : [];
  const list = path.length ? path : (ev && ev.target ? [ev.target] : []);
  for (let i = 0; i < list.length; i++) {
    const n = list[i];
    if (!n || !n.getAttribute) continue;
    if (n.hasAttribute && n.hasAttribute('data-stop') && !names.some(a => n.hasAttribute(a))) return null;
    if (names.some(a => n.hasAttribute && n.hasAttribute(a))) return n;
  }
  return null;
}
function onDartsAct(ev, kind) {
  try {
    if (ev && ev.__dartsHandled) return;
    const names = kind === 'change' || kind === 'input' ? ['data-act-change']
      : kind === 'blur' ? ['data-act-blur']
      : kind === 'key' ? ['data-act-key']
      : ['data-act'];
    const el = findActEl(ev, names);
    if (!el || !window.__dartsApi) return;
    if (kind === 'key' && ev && ev.key !== 'Enter') return;
    ev.__dartsHandled = true;
    if (kind !== 'input') {
      try { ev.preventDefault(); } catch (e) {}
    }
    try { ev.stopPropagation(); } catch (e) {}
    try { if (ev.stopImmediatePropagation) ev.stopImmediatePropagation(); } catch (e) {}
    window.__dartsApi.run(el, ev, kind === 'input' ? 'change' : kind);
  } catch (e) {}
}
function attachDartsHost(host) {
  if (!host || host.__dartsBound) return;
  host.__dartsBound = true;
  host.addEventListener('click', ev => onDartsAct(ev, ''), true);
  host.addEventListener('change', ev => onDartsAct(ev, 'change'), true);
  host.addEventListener('input', ev => {
    const el = ev && ev.target;
    if (el && el.matches && el.matches('input[type="range"][data-act-change], input[type="range"][data-act-change] *')) {
      onDartsAct(ev, 'input');
    } else if (el && el.getAttribute && el.getAttribute('data-act-change') && el.type === 'range') {
      onDartsAct(ev, 'input');
    }
  }, true);
  host.addEventListener('focusout', ev => onDartsAct(ev, 'blur'), true);
  host.addEventListener('keydown', ev => onDartsAct(ev, 'key'), true);
}
function bindCard(card) {
  if (typeof window === 'undefined') return;
  if (card) {
    window.__dartsCard = card;
    try { if (card.hass || card._hass) window.__dartsHass = card.hass || card._hass; } catch (e) {}
  }
  try { if (card && card.shadowRoot) attachDartsHost(card.shadowRoot); } catch (e) {}
}
function installApi(card) {
  if (typeof window === 'undefined') return;
  bindCard(card || window.__dartsCard);
  window.__dartsApi = {
    run(el, ev, kind) {
      kind = kind || '';
      const attr = kind === 'change' ? 'data-act-change' : kind === 'blur' ? 'data-act-blur' : kind === 'key' ? 'data-act-key' : 'data-act';
      const argsAttr = kind === 'change' ? 'data-args-change' : kind === 'blur' ? 'data-args-blur' : kind === 'key' ? 'data-args-key' : 'data-args';
      const act = el && el.getAttribute && el.getAttribute(attr);
      if (!act) return false;
      if (kind === 'key' && ev && ev.key !== 'Enter') return false;
      const args = parseActArgs(el, argsAttr).map(a => a === '$value' ? el.value : a);
      if (act === 'addPlayer') {
        window.__dartsApi.addPlayer(args[0] != null ? args[0] : el.value);
        if (el && 'value' in el) el.value = '';
        return false;
      }
      const fn = window.__dartsApi[act];
      if (typeof fn === 'function') fn.apply(window.__dartsApi, args);
      return false;
    },
    lightBri(entity, value) {
      return window.__dartsApi.lightOn(entity, { brightness: Math.round(Number(value) * 2.55) });
    },
    tab(name) {
      window.__dartsSection = name;
      try { if (window.__dartsCard) window.__dartsCard._section = name; } catch (e) {}
      try { localStorage.setItem('dartsArenaTab', name); } catch (e) {}
      try {
        history.pushState({ dartsTab: name }, '', '#' + name);
        try { window.dispatchEvent(new Event('location-changed')); } catch (e2) {}
      } catch (e) {
        try { history.replaceState(null, '', '#' + name); } catch (e3) { try { location.hash = name; } catch (e4) {} }
      }
      const root = appRoot();
      if (root) {
        root.querySelectorAll('[data-section]').forEach(el => { el.hidden = el.getAttribute('data-section') !== name; });
        root.querySelectorAll('[data-tab]').forEach(el => el.classList.toggle('on', el.getAttribute('data-tab') === name));
      }
      try { setTimeout(() => syncOverlays(window.__dartsCard), 0); } catch (e) {}
      try { if (window.__dartsCard && window.__dartsCard._lockGlowHeight) window.__dartsCard._lockGlowHeight(false); } catch (e) {}
      return false;
    },
    leg(v) {
      window.__dartsLeg = String(v);
      const root = appRoot();
      if (root) {
        root.querySelectorAll('[data-leg]').forEach(el => el.classList.toggle('on', el.getAttribute('data-leg') === String(v)));
        const board = root.querySelector('.board-side');
        if (board) board.outerHTML = renderBoard();
      }
      return false;
    },
    call(domain, service, data) {
      const card = (typeof window !== 'undefined' && window.__dartsCard) || null;
      const hass = (card && (card._hass || card.hass)) || hassObj();
      const payload = data || {};
      try {
        if (hass && typeof hass.callService === 'function') hass.callService(domain, service, payload);
        else if (hass && hass.services && typeof hass.services.call === 'function') hass.services.call(domain, service, payload);
      } catch (e) {}
      return false;
    },
    confirm(msg, domain, service, data) {
      window.__dartsPending = { msg, domain, service, data };
      const root = appRoot();
      if (root) {
        const old = root.querySelector('.modal-bg');
        if (old) old.remove();
        root.insertAdjacentHTML('beforeend', modalHtml());
      }
      return false;
    },
    yes() {
      const p = window.__dartsPending;
      window.__dartsPending = null;
      const root = appRoot();
      if (root) { const m = root.querySelector('.modal-bg'); if (m) m.remove(); }
      if (p) window.__dartsApi.call(p.domain, p.service, p.data);
      return false;
    },
    no() {
      window.__dartsPending = null;
      const root = appRoot();
      if (root) { const m = root.querySelector('.modal-bg'); if (m) m.remove(); }
      return false;
    },
    more(entityId) {
      const ev = new CustomEvent('hass-more-info', { bubbles: true, composed: true, detail: { entityId } });
      const card = window.__dartsCard;
      try { if (card) card.dispatchEvent(ev); } catch (e) {}
      try {
        const ha = document.querySelector('home-assistant');
        if (ha && ha !== card) ha.dispatchEvent(ev);
      } catch (e) {}
      return false;
    },
    setText(entity, value) { return window.__dartsApi.call('text', 'set_value', { entity_id: entity, value }); },
    setInput(entity, value) { return window.__dartsApi.call('input_text', 'set_value', { entity_id: entity, value }); },
    setNumber(entity, value) { return window.__dartsApi.call('number', 'set_value', { entity_id: entity, value: Number(value) }); },
    setSelect(entity, option) { return window.__dartsApi.call('select', 'select_option', { entity_id: entity, option }); },
    lightOn(entity, data) { return window.__dartsApi.call('light', 'turn_on', Object.assign({ entity_id: entity }, data || {})); },
    toggle(domain, entity) { return window.__dartsApi.call(domain, 'toggle', { entity_id: entity }); },
    press(entity) { return window.__dartsApi.call('button', 'press', { entity_id: entity }); },
    cycleColor(index) {
      const NAMES = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'cyan', 'pink'];
      const names = helperNames();
      const n = Math.max(4, names.length);
      const cur = String(st(E.colors).state || '').split(',').map(x => x.trim().toLowerCase());
      while (cur.length < n) cur.push(NAMES[cur.length % 8]);
      if (index < n) {
        const k = NAMES.indexOf(cur[index]);
        cur[index] = NAMES[(k < 0 ? 0 : k + 1) % 8];
      }
      const next = cur.slice(0, n).join(', ');
      // PLAYER PROFILES HOOK: prefer granboard.update_player when a roster id exists
      const entry = rosterEntries()[index];
      if (entry && (entry.id || entry.name)) {
        window.__dartsApi.call('granboard', 'update_player', { player_id: entry.id || entry.name, name: entry.name, color: cur[index] });
      }
      return window.__dartsApi.setInput(E.colors, next);
    },
    savePlayers(val) { return window.__dartsApi.setInput(E.players, val); },
    saveColors(val) { return window.__dartsApi.setInput(E.colors, val); },
    // PLAYER PROFILES HOOK — no-ops until the integration registers these services
    addPlayer(name) { return window.__dartsApi.call('granboard', 'add_player', { name: name }); },
    removePlayer(id, name) { return window.__dartsApi.call('granboard', 'remove_player', { player_id: id || name, name: name }); },
    setLineup(names) { return window.__dartsApi.call('granboard', 'set_lineup', { players: names }); },
    focusDart(i) {
      const cur = window.__dartsFocusDart;
      window.__dartsFocusDart = (cur === i ? null : i);
      const root = appRoot();
      if (root) {
        root.querySelectorAll('[data-dart]').forEach(el => {
          el.classList.toggle('focus', window.__dartsFocusDart != null && el.getAttribute('data-dart') === String(window.__dartsFocusDart));
        });
        root.querySelectorAll('.board-side').forEach(board => {
          const wrap = document.createElement('div');
          wrap.innerHTML = renderBoard();
          if (wrap.firstElementChild) board.replaceWith(wrap.firstElementChild);
        });
      }
      return false;
    },
    toggleWledPanel(id) {
      const root = appRoot();
      if (!root) return false;
      const unit = root.querySelector('.wled-unit[data-wled="' + String(id).replace(/"/g, '') + '"]');
      if (!unit) return false;
      const open = !unit.classList.contains('open');
      unit.classList.toggle('open', open);
      unit.setAttribute('aria-expanded', open ? 'true' : 'false');
      try {
        const map = wledOpenMap();
        map[id] = open;
        localStorage.setItem('dartsArenaWledOpen', JSON.stringify(map));
      } catch (e) {}
      return false;
    },
    setGlow(mode) {
      try { localStorage.setItem('dartsArenaGlow', mode); } catch (e) {}
      try {
        if (window.__dartsCard && window.__dartsCard._syncBoardGlow) window.__dartsCard._syncBoardGlow();
        else applyBoardGlow(appRoot());
      } catch (e) { applyBoardGlow(appRoot()); }
      return false;
    },
    startGame(data, msg) {
      const cfg = DARTS_CONFIG;
      if (cfg.newGameScript) {
        return window.__dartsApi.confirm(msg, 'script', String(cfg.newGameScript).replace(/^script\./, ''), data);
      }
      const names = helperNames();
      const roster = rosterEntries();
      const cols = names.map((n, i) => (roster[i] && roster[i].color) || helperCols()[i] || '');
      const payload = Object.assign({
        players: names.length ? names : ['Player 1'],
        double_out: st(E.double).state === 'on'
      }, data || {});
      if (cols.some(Boolean)) payload.colors = cols;
      return window.__dartsApi.confirm(msg, 'granboard', 'new_game', payload);
    }
  };
  if (!window.__dartsHashBound) {
    window.__dartsHashBound = true;
    window.addEventListener('hashchange', () => {
      window.__dartsSection = (location.hash || '').replace('#', '') || 'game';
      window.__dartsApi.tab(window.__dartsSection);
    });
  }
}

function ico(d) {
  return `<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="${d}"></path></svg>`;
}
const ICON = {
  undo: 'M12.5,8C9.85,8 7.45,9 5.6,10.6L2,7V16H11L7.38,12.38C8.77,11.22 10.54,10.5 12.5,10.5C16.04,10.5 19.05,12.81 20.1,16L22.47,15.22C21.08,11.03 17.15,8 12.5,8Z',
  next: 'M15,14C12.33,14 7,15.33 7,18V20H23V18C23,15.33 17.67,14 15,14M15,12A4,4 0 0,0 19,8A4,4 0 0,0 15,4A4,4 0 0,0 11,8A4,4 0 0,0 15,12M5.59,10L8,12.41L6.59,13.82L2.76,10L6.59,6.18L8,7.59L5.59,10Z',
  flag: 'M14.4,6H20V16H13L12.6,14H7V21H5V4H14L14.4,6Z',
  mark: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12zm0 2a4 4 0 1 1 0 8 4 4 0 0 1 0-8zm0 2a2 2 0 1 0 0 4 2 2 0 0 0 0-4z',
  game: 'M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm0 2a8 8 0 1 1 0 16 8 8 0 0 1 0-16zm0 3a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 3a2 2 0 1 1 0 4 2 2 0 0 1 0-4z',
  players: 'M16 17V19H2V17S2 13 9 13 16 17 16 17M12.5 7.5A3.5 3.5 0 1 0 9 11A3.5 3.5 0 0 0 12.5 7.5M15.94 13A5.32 5.32 0 0 1 18 17V19H22V17S22 13.37 15.94 13M15 4A3.39 3.39 0 0 0 13.07 4.59 5 5 0 0 1 13.07 10.41 3.39 3.39 0 0 0 15 11A3.5 3.5 0 0 0 15 4Z',
  ring: 'M12,2A10,10 0 0,0 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2M12,4A8,8 0 0,1 20,12A8,8 0 0,1 12,20A8,8 0 0,1 4,12A8,8 0 0,1 12,4M12,6A6,6 0 0,0 6,12A6,6 0 0,0 12,18A6,6 0 0,0 18,12A6,6 0 0,0 12,6Z',
  room: 'M12,2A7,7 0 0,0 5,9C5,11.38 6.19,13.47 8,14.74V17A1,1 0 0,0 9,18H15A1,1 0 0,0 16,17V14.74C17.81,13.47 19,11.38 19,9A7,7 0 0,0 12,2M9,21A1,1 0 0,0 10,22H14A1,1 0 0,0 15,21V20H9V21Z',
  sounds: 'M14,3.23V5.29C16.89,6.15 19,8.83 19,12C19,15.17 16.89,17.84 14,18.7V20.77C18,19.86 21,16.28 21,12C21,7.72 18,4.14 14,3.23M16.5,12C16.5,10.23 15.5,8.71 14,7.97V16C15.5,15.29 16.5,13.76 16.5,12M3,9V15H7L12,20V4L7,9H3Z',
  settings: 'M12,15.5A3.5,3.5 0 0,1 8.5,12A3.5,3.5 0 0,1 12,8.5A3.5,3.5 0 0,1 15.5,12A3.5,3.5 0 0,1 12,15.5M19.43,12.97C19.47,12.65 19.5,12.33 19.5,12C19.5,11.67 19.47,11.34 19.43,11L21.54,9.37C21.73,9.22 21.78,8.95 21.66,8.73L19.66,5.27C19.54,5.05 19.27,4.96 19.05,5.05L16.56,6.05C16.04,5.66 15.5,5.32 14.87,5.07L14.5,2.42C14.46,2.18 14.25,2 14,2H10C9.75,2 9.54,2.18 9.5,2.42L9.13,5.07C8.5,5.32 7.96,5.66 7.44,6.05L4.95,5.05C4.73,4.96 4.46,5.05 4.34,5.27L2.34,8.73C2.21,8.95 2.27,9.22 2.46,9.37L4.57,11C4.53,11.34 4.5,11.67 4.5,12C4.5,12.33 4.53,12.65 4.57,12.97L2.46,14.63C2.27,14.78 2.21,15.05 2.34,15.27L4.34,18.73C4.46,18.95 4.73,19.03 4.95,18.95L7.44,17.94C7.96,18.34 8.5,18.68 9.13,18.93L9.5,21.58C9.54,21.82 9.75,22 10,22H14C14.25,22 14.46,21.82 14.5,21.58L14.87,18.93C15.5,18.67 16.04,18.34 16.56,17.94L19.05,18.95C19.27,19.03 19.54,18.95 19.66,18.73L21.66,15.27C21.78,15.05 21.73,14.78 21.54,14.63L19.43,12.97Z'
};


function svgGlyph(inner) {
  return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">' + inner + '</svg>';
}
function modeGlyph(name) {
  if (name === '301' || name === '501') {
    return '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="2.75" y="5" width="18.5" height="14" rx="2.25" fill="none" stroke="currentColor" stroke-width="1.5"/><text x="12" y="15.2" text-anchor="middle" font-size="7.4" font-weight="700" font-family="Outfit,Inter,system-ui,sans-serif" fill="currentColor">' + name + '</text></svg>';
  }
  if (name === 'Cricket') {
    return svgGlyph('<circle cx="12" cy="12" r="8.5"/><circle cx="12" cy="12" r="5.2"/><circle cx="12" cy="12" r="1.8" fill="currentColor" stroke="none"/>');
  }
  if (name === 'Count-Up') {
    return svgGlyph('<path d="M5 18V13M10 18V9M15 18V11M19 18V6" stroke-width="2"/>');
  }
  if (name === 'Around The Clock') {
    return svgGlyph('<circle cx="12" cy="12" r="8.5"/><path d="M12 12V7.5M12 12L16 14"/><path d="M12 3.8V5.4M20.2 12H18.6M12 20.2V18.6M3.8 12H5.4"/>');
  }
  return svgGlyph('<circle cx="12" cy="12" r="8.5"/>');
}
function fxGlyph(name) {
  const n = String(name || '').toLowerCase();
  const map = {
    'solid': '<circle cx="12" cy="12" r="6" fill="currentColor" stroke="none"/>',
    'blink': '<circle cx="12" cy="12" r="4"/><path d="M12 3.5V6M12 18V20.5M3.5 12H6M18 12H20.5M6.2 6.2L8 8M16 16L17.8 17.8M17.8 6.2L16 8M8 16L6.2 17.8"/>',
    'breathe': '<circle cx="12" cy="12" r="3.5"/><circle cx="12" cy="12" r="7.5" opacity="0.7"/>',
    'heartbeat': '<path d="M3 12H7L9.2 7.5L12.5 16.5L14.8 12H21"/>',
    'wave': '<path d="M3 12C5.5 8 8.5 8 11 12S16.5 16 21 12"/>',
    'color cycle': '<circle cx="12" cy="12" r="6.5"/><path d="M12 5.5A6.5 6.5 0 0 1 18.5 12"/><path d="M16.7 6.2L18.6 5.4 18.2 7.6"/>',
    'palette steps': '<rect x="4" y="13" width="5" height="5"/><rect x="9.5" y="9" width="5" height="5"/><rect x="15" y="5" width="5" height="5"/>',
    'chase': '<path d="M5 8L10 12L5 16M11 8L16 12L11 16M17 8L20 12L17 16"/>',
    'rainbow chase': '<path d="M5 8L10 12L5 16M11 8L16 12L11 16"/><path d="M16 7A7 7 0 0 1 20 12"/>',
    'circular rainbow': '<path d="M6 16A7 7 0 1 1 18 16"/><path d="M8 16A5 5 0 1 1 16 16"/><path d="M10 16A3 3 0 1 1 14 16"/>',
    'rainbow sweep': '<path d="M5 16A7 7 0 0 1 19 16"/><path d="M8 16A4 4 0 0 1 16 16"/><path d="M19 16H21"/>',
    'bounce': '<path d="M8 16C8 12 16 12 16 8"/><circle cx="16" cy="7" r="2" fill="currentColor" stroke="none"/><path d="M6 19H18"/>',
    'circular wipe': '<circle cx="12" cy="12" r="7.5"/><path d="M12 4.5A7.5 7.5 0 0 1 19.5 12L12 12Z" fill="currentColor" stroke="none" opacity="0.85"/>',
    'twinkle': '<path d="M12 3.5L13.4 9.2L19 10.5L13.4 11.8L12 17.5L10.6 11.8L5 10.5L10.6 9.2Z" fill="currentColor" stroke="none"/>',
    'fire flicker': '<path d="M12 20C8.8 20 7 17.6 7 14.8C7 11.2 12 6 12 6S17 11.2 17 14.8C17 17.6 15.2 20 12 20Z"/><path d="M12 18C10.6 18 10 16.8 10 15.6C10 13.8 12 11.5 12 11.5"/>',
    'police': '<circle cx="8" cy="12" r="3.2"/><circle cx="16" cy="12" r="3.2"/><path d="M11.2 12H12.8"/>',
    'lightning': '<path d="M13 3L6.5 13H12L11 21L17.5 11H12L13 3Z" fill="currentColor" stroke="none"/>',
    'wipe': '<rect x="4" y="6" width="16" height="12"/><path d="M12 6V18" /><path d="M12 6H20V18H12" fill="currentColor" opacity="0.35" stroke="none"/>',
    'sweep': '<path d="M5 16A7 7 0 0 1 19 16"/><path d="M12 16V9"/>',
    'rainbow': '<path d="M5 16A7 7 0 0 1 19 16"/><path d="M8 16A4 4 0 0 1 16 16"/>',
    'colorloop': '<path d="M7 7A6 6 0 1 1 6 12"/><path d="M5 5.5V8.2H7.7"/>',
    'fireworks': '<path d="M12 11V4M12 11L7.5 6.5M12 11L16.5 6.5M12 13V20M10 14L6 18M14 14L18 18M8 12H4M16 12H20"/>',
    'sparkle': '<path d="M8 4L9 7L12 8L9 9L8 12L7 9L4 8L7 7Z" fill="currentColor" stroke="none"/><path d="M16 10L17.2 13.2L20.5 14.5L17.2 15.8L16 19L14.8 15.8L11.5 14.5L14.8 13.2Z" fill="currentColor" stroke="none"/>',
    'scan': '<rect x="4" y="6" width="16" height="12"/><path d="M4 12H20" stroke-width="2"/>',
    'meteor': '<circle cx="15.5" cy="8.5" r="2.4" fill="currentColor" stroke="none"/><path d="M13.4 10.6L5 19"/>',
    'colortwinkles': '<path d="M8 5L9 8L12 9L9 10L8 13L7 10L4 9L7 8Z" fill="currentColor" stroke="none"/><path d="M16 11L17 14L20 15L17 16L16 19L15 16L12 15L15 14Z" fill="currentColor" stroke="none"/>',
    'pride 2015': '<path d="M5 6H19M5 10H19M5 14H19M5 18H19" stroke-width="1.8"/>'
  };
  const inner = map[n] || (n.includes('rainbow') ? map.rainbow : n.includes('fire') ? map['fire flicker'] : n.includes('twink') || n.includes('spark') ? map.sparkle : n.includes('wave') || n.includes('flow') || n.includes('aquatic') ? map.wave : '<circle cx="12" cy="12" r="3.2" fill="currentColor" stroke="none"/><circle cx="12" cy="12" r="8"/>');
  return svgGlyph(inner);
}
function themeGlyph(name) {
  const n = String(name || '').toLowerCase();
  if (n === 'off') return svgGlyph('<path d="M5 10V14H9L14 18V6L9 10H5Z"/><path d="M16.5 9.5L19.5 14.5"/>');
  if (n === 'classic') return svgGlyph('<path d="M5 10V14H9L14 18V6L9 10H5Z"/><path d="M17 9A4 4 0 0 1 17 15"/>');
  if (n === 'pub') return svgGlyph('<path d="M6 5H14L13 11A4 4 0 0 1 6 11V5Z"/><path d="M14 7H17A2 2 0 0 1 17 11H13"/><path d="M10 13V19M7 19H13"/>');
  return svgGlyph('<path d="M5 10V14H9L14 18V6L9 10H5Z"/><path d="M17 8A5 5 0 0 1 17 16"/>');
}
function presetGlyph(name) {
  const n = String(name || '').toLowerCase();
  if (n.includes('rainbow')) return fxGlyph('Rainbow');
  if (n.includes('aquatic') || n.includes('flow') || n.includes('water') || n.includes('ocean')) return fxGlyph('Wave');
  if (n.includes('forest') || n.includes('leaf')) return svgGlyph('<path d="M12 20V11"/><path d="M12 18C8 18 6 14 6 10C10 10 12 12 12 12C12 12 14 10 18 10C18 14 16 18 12 18Z"/><path d="M12 11C12 8 13.5 5 17 4C16 8 14 10 12 11Z"/>');
  if (n.includes('party') || n.includes('fire')) return fxGlyph('Fireworks');
  return svgGlyph('<path d="M8 4H16L18 8H6L8 4Z"/><path d="M7 8H17V19L12 16.5L7 19V8Z"/>');
}
function iconTile(kind, label, selected, attrs) {
  const glyph = kind === 'mode' ? modeGlyph(label) : kind === 'theme' ? themeGlyph(label) : kind === 'preset' ? presetGlyph(label) : fxGlyph(label);
  const cls = (kind === 'mode' ? 'mode-tile' : 'icon-tile') + (selected ? ' on' : '');
  return '<button type="button" class="' + cls + '" title="' + esc(label) + '" ' + attrs + '>' + glyph + '<span class="' + (kind === 'mode' ? 'mode-label' : 'icon-label') + '">' + esc(label) + '</span></button>';
}

function chrome() {
  const tab = tabName();
  const on = st(E.conn).state === 'on';
  const en = st(E.sw).state === 'on';
  const sg = st(E.signal).state;
  const offline = isBoardOffline();
  const txt = offline ? 'Board Offline' : (on ? 'Board Connected' : (en ? 'Looking For Board' : 'Released For App'));
  const short = offline ? 'Offline' : (on ? 'Connected' : (en ? 'Looking' : 'Released'));
  const sig = (on && sg && sg !== 'unknown' && sg !== 'unavailable' && !offline) ? ` · ${esc(sg)} dBm` : '';
  const cls = offline ? 'off' : (on ? 'ok' : (en ? 'wait' : ''));
  const badge = offline ? '<span class="offline-badge">Board Offline</span>' : '';
  const topNav = TABS.map(([id, label]) => `<button type="button" data-tab="${id}" class="${tab === id ? 'on' : ''}" ${da('tab', id)} ${ov('tab_' + id + '_top')}>${label}</button>`).join('');
  const railNav = TABS.map(([id, label]) => `<button type="button" data-tab="${id}" class="${tab === id ? 'on' : ''}" ${da('tab', id)} ${ov('tab_' + id + '_rail')}>${ico(ICON[id] || ICON.mark)}<span>${label}</span></button>`).join('');
  return `<aside class="rail" aria-label="Sections">
    <div class="rail-av">${ico(ICON.mark)}</div>
    <nav class="rail-nav">${railNav}</nav>
    <div class="status"><i class="dot ${cls}"></i><span>${short}</span></div>
    ${badge}
  </aside>
  <header class="top">
    <div class="brand">${ico(ICON.mark)}<span class="name">Darts</span><span class="tag">Arena</span></div>
    <nav class="nav" aria-label="Sections">${topNav}</nav>
    <div class="status"><i class="dot ${cls}"></i><span>${txt}${sig}</span>${badge}</div>
  </header>`;
}

function gameName(a) {
  const GN = { x01: (a.start || '') + (a.double_out ? ' Double Out' : ''), cricket: 'Cricket', count_up: 'Count-Up', around_the_clock: 'Around The Clock' };
  return GN[a.game] || a.game || 'Ready To Throw';
}


const BOARD_ORD = [20, 1, 18, 4, 13, 6, 10, 15, 2, 17, 3, 19, 7, 16, 8, 11, 14, 9, 12, 5];
const BOARD_R = { single_inner: [16, 99], treble: [99, 107], single_outer: [107, 162], double: [162, 170] };
const BOARD_MID = { single_inner: 57.5, treble: 103, single_outer: 134.5, double: 166, bull: 11.2, bullseye: 0 };

function parseSegment(seg) {
  if (!seg || seg === 'OUT' || String(seg).toLowerCase() === 'miss') return null;
  const s = String(seg).trim().toUpperCase();
  if (s === 'DB' || s === 'BULLSEYE' || s === 'IB') return { segment: s, ring: 'bullseye', number: 25 };
  if (s === 'SB' || s === 'BULL' || s === 'OB') return { segment: s, ring: 'bull', number: 25 };
  const m = s.match(/^(T|D|S)?(\d+)$/);
  if (!m) return null;
  const n = Number(m[2]);
  const ring = m[1] === 'T' ? 'treble' : m[1] === 'D' ? 'double' : (n ? 'single_outer' : 'single_outer');
  return { segment: s, ring, number: n };
}
function dartAngle(idx) {
  return -26 + ((idx || 0) % 6) * 14;
}
function dartPos(d, idx) {
  const p = (d && d.number != null && d.ring) ? d : parseSegment((d && (d.segment || d)) || '');
  if (!p) {
    const a = (-90 + (idx || 0) * 28) * Math.PI / 180;
    return { x: Math.cos(a) * 188, y: Math.sin(a) * 188, p: { ring: 'miss', number: 0, segment: 'OUT' } };
  }
  const k = ((idx || 0) * 17 + (p.number || 0) * 13) % 360;
  if (p.ring === 'bullseye') {
    const a = k * Math.PI / 180;
    return { x: Math.cos(a) * 1.6, y: Math.sin(a) * 1.6, p };
  }
  if (p.ring === 'bull') {
    const a = (k % 360) * Math.PI / 180;
    return { x: Math.cos(a) * 11, y: Math.sin(a) * 11, p };
  }
  const i = BOARD_ORD.indexOf(p.number);
  if (i < 0) return null;
  const mid = (-99 + i * 18 + 9) * Math.PI / 180;
  const r = (BOARD_MID[p.ring] || 134.5) + ((idx || 0) % 5 - 2) * 2.2;
  const wobble = ((idx || 0) % 3 - 1) * 0.035;
  return { x: r * Math.cos(mid + wobble), y: r * Math.sin(mid + wobble), p };
}
function selectedLeg() {
  return (typeof window !== 'undefined' && window.__dartsLeg) ? String(window.__dartsLeg) : 'all';
}
function collectHits() {
  const a = gs();
  const leg = selectedLeg();
  const people = a.players || [];
  const colorOf = name => {
    const hit = people.find(p => p.name === name);
    return (hit && hit.color) || pcol(Math.max(0, people.findIndex(p => p.name === name)));
  };
  const out = [];
  (a.history || []).forEach(h => {
    if (leg !== 'all' && String(h.round) !== leg) return;
    (h.darts || []).forEach(seg => {
      const p = parseSegment(seg);
      if (p) out.push(Object.assign({ color: colorOf(h.player), player: h.player }, p));
    });
  });
  const includeTurn = leg === 'all' || String(a.round) === leg;
  if (includeTurn) {
    const col = a.current_player_color || pcol(a.current_player || 0);
    (a.darts || []).forEach(d => out.push(Object.assign({ color: col, player: a.current_player_name }, d)));
  }
  return out;
}
function availableRounds() {
  const a = gs();
  const rs = new Set();
  (a.history || []).forEach(h => { if (h.round) rs.add(Number(h.round)); });
  if (a.round) rs.add(Number(a.round));
  return [...rs].filter(n => Number.isFinite(n)).sort((x, y) => x - y);
}
function lastScoreFor(name) {
  const hist = (gs().history || []).filter(h => h.player === name);
  if (!hist.length) return null;
  return hist[hist.length - 1].score;
}
function reduceMotion() {
  try { return typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches; } catch (e) { return false; }
}
function dartSig(d) {
  if (!d) return '';
  return [d.segment, d.ring, d.number, d.score].join('|');
}
function dartGraphic(x, y, color, opts) {
  opts = opts || {};
  const ang = opts.angle != null ? opts.angle : dartAngle(opts.idx);
  const scale = opts.scale || 1;
  const fresh = opts.fresh ? ' drop-in' : '';
  const focus = opts.focus ? ' is-focus' : '';
  const c = color || 'var(--pc, var(--accent-color, var(--primary-color)))';
  return `<g class="dart-pin-wrap${fresh}${focus}" transform="translate(${Number(x).toFixed(2)},${Number(y).toFixed(2)})"><g class="dart-drop"><g class="dart-pin" transform="rotate(${ang}) scale(${scale})" style="--dc:${c}">
    <ellipse class="dart-aura" cx="0" cy="-11" rx="6.5" ry="13"/>
    <path class="dart-flight back" d="M0 -14.6 L0 -23.8 L3.2 -18.6 Z"/>
    <path class="dart-flight left" d="M0 -14.6 L-7.2 -21.8 L-0.2 -18.2 Z"/>
    <path class="dart-flight right" d="M0 -14.6 L7.2 -21.8 L0.2 -18.2 Z"/>
    <path class="dart-barrel" d="M-1.25 -6.2 C-1.45 -8.2 -1.5 -10.2 -1.45 -12.6 C-1.4 -14.2 -0.7 -15.1 0 -15.1 C0.7 -15.1 1.4 -14.2 1.45 -12.6 C1.5 -10.2 1.45 -8.2 1.25 -6.2 Z"/>
    <rect class="dart-grip" x="-1.15" y="-10.4" width="2.3" height="3.2" rx="0.4"/>
    <path class="dart-shaft" d="M0 0.2 L0.55 -6.2 L-0.55 -6.2 Z"/>
    <path class="dart-tip" d="M0 2.1 L1.15 -1.1 L0 -0.35 L-1.15 -1.1 Z"/>
  </g></g></g>`;
}
function cropBox(d, i) {
  if (!d) return { x: -125, y: -125, w: 250, h: 250 };
  const pos = dartPos(d, i) || { x: 0, y: 0 };
  const ang = dartAngle(i) * Math.PI / 180;
  const lift = 12;
  const cx = pos.x + lift * Math.sin(ang);
  const cy = pos.y - lift * Math.cos(ang);
  const ring = (pos.p && pos.p.ring) || d.ring || '';
  const s = ring === 'bullseye' ? 26 : ring === 'bull' ? 34 : ring === 'treble' ? 42 : ring === 'double' ? 42 : ring === 'miss' ? 56 : 48;
  return { x: cx - s, y: cy - s, w: s * 2, h: s * 2 };
}
function cropVb(box) {
  return box.x.toFixed(1) + ' ' + box.y.toFixed(1) + ' ' + box.w.toFixed(1) + ' ' + box.h.toFixed(1);
}
function focusedDartIndex() {
  if (typeof window === 'undefined') return null;
  const i = window.__dartsFocusDart;
  if (i == null || i === '') return null;
  if (!(gs().darts || [])[i]) { window.__dartsFocusDart = null; return null; }
  return i;
}
function isNewVisitDart(sig) {
  if (typeof window === 'undefined') return !!sig;
  const mem = window.__dartsFreshSig = window.__dartsFreshSig || { v: '' };
  const changed = mem.v !== sig;
  mem.v = sig;
  return !!(changed && sig);
}

function boardArt(hits, freshHit, opt) {

  const P = (r, a) => { const x = (r * Math.cos(a * Math.PI / 180)).toFixed(2), y = (r * Math.sin(a * Math.PI / 180)).toFixed(2); return x + ' ' + y; };
  const sec = (r1, r2, a1, a2) => `M${P(r2, a1)}A${r2} ${r2} 0 0 1 ${P(r2, a2)}L${P(r1, a2)}A${r1} ${r1} 0 0 0 ${P(r1, a1)}Z`;
  let paths = '', nums = '', hitPath = '';
  BOARD_ORD.forEach((n, i) => {
    const a1 = -99 + i * 18, a2 = a1 + 18, dark = i % 2 === 0;
    for (const ring in BOARD_R) {
      const [r1, r2] = BOARD_R[ring];
      const col = (ring === 'treble' || ring === 'double') ? (dark ? '#c8323a' : '#2f8f57') : (dark ? '#1d1f24' : '#e9dfc6');
      const d = sec(r1, r2, a1, a2);
      paths += `<path d="${d}" fill="${col}"/>`;
      if (freshHit && freshHit.number === n && freshHit.ring === ring) hitPath = d;
    }
    nums += `<text fill="#f3f4f7" x="${(186 * Math.cos((a1 + 9) * Math.PI / 180)).toFixed(1)}" y="${(186 * Math.sin((a1 + 9) * Math.PI / 180) + 6).toFixed(1)}">${n}</text>`;
  });
  paths += `<circle r="16" fill="#2f8f57"/><circle r="6.5" fill="#c8323a"/>`;
  if (freshHit && freshHit.ring === 'bull') hitPath = 'M16 0A16 16 0 1 0 -16 0A16 16 0 1 0 16 0M6.5 0A6.5 6.5 0 1 1 -6.5 0A6.5 6.5 0 1 1 6.5 0Z';
  if (freshHit && freshHit.ring === 'bullseye') hitPath = 'M6.5 0A6.5 6.5 0 1 1 -6.5 0A6.5 6.5 0 1 1 6.5 0Z';
  let heat = '', dots = '';
  opt = opt || {};
  const focusHit = opt.focusHit;
  (hits || []).forEach((d, i) => {
    const pos = dartPos(d, i);
    if (!pos) return;
    const c = d.color || 'var(--accent-color, var(--primary-color))';
    const isFocus = !!d._focus;
    const isFresh = !!(opt.freshAnim && d._fresh);
    heat += `<circle class="heat" cx="${pos.x.toFixed(1)}" cy="${pos.y.toFixed(1)}" r="22" fill="${c}"/>`;
    dots += dartGraphic(pos.x, pos.y, c, { idx: (d._idx != null ? d._idx : i), fresh: isFresh, focus: isFocus, scale: isFocus ? 1.22 : 1 });
  });
  const hl = hitPath ? `<path class="hit flash" d="${hitPath}" fill-rule="evenodd"/>` : '';
  return `<circle class="rim-aura" r="206"/><circle class="rim-glow" r="204"/><circle class="ring-outer" r="204"/><circle class="ring-bevel" r="198"/><g class="nums">${nums}</g>${paths}<g class="wires"><circle r="170"/><circle r="162"/><circle r="107"/><circle r="99"/></g><g class="heat-layer">${heat}</g><g class="scatter-layer">${dots}</g>${hl}`;
}
function renderBoard() {
  const GS = gs();
  const mem = (typeof window !== 'undefined') ? window : {};
  const playing = st(E.game).state;
  const darts = GS.darts || [];
  const lastDart = darts[darts.length - 1];
  let h = Object.assign({}, attr(E.last));
  let t = h.time || '';
  if (playing === 'playing' && GS.turn_complete && lastDart) {
    const same = h.segment === lastDart.segment && (!lastDart.ring || h.ring === lastDart.ring);
    if (same && t) mem._gbLockT = t;
    t = mem._gbLockT || (same ? t : '');
    h = Object.assign({}, h, lastDart);
  } else if (!GS.turn_complete) {
    mem._gbLockT = undefined;
  }
  const HOLD = 20000;
  const fresh = !!t && !Number.isNaN(Date.parse(t)) && (Date.now() - Date.parse(t) < HOLD);
  if (mem) {
    if (mem._gbClearTimer) { clearTimeout(mem._gbClearTimer); mem._gbClearTimer = null; }
    if (fresh) {
      const remain = HOLD - (Date.now() - Date.parse(t));
      mem._gbClearTimer = setTimeout(() => { mem._gbClearTimer = null; }, Math.max(50, remain + 50));
    }
  }
  const visit = GS.darts || [];
  const hits = collectHits().map((d, i) => Object.assign({}, d, { _idx: d._idx != null ? d._idx : i }));
  if (visit.length) {
    const last = visit[visit.length - 1];
    for (let i = hits.length - 1; i >= 0; i--) {
      if (dartSig(hits[i]) === dartSig(last) || (hits[i].segment === last.segment && hits[i].number === last.number && hits[i].ring === last.ring)) {
        hits[i] = Object.assign({}, hits[i], { _fresh: true, _idx: visit.length - 1 });
        break;
      }
    }
  }
  const focusI = focusedDartIndex();
  const focusHit = (focusI != null && visit[focusI]) ? visit[focusI] : null;
  if (focusHit) {
    const col = GS.current_player_color || pcol(GS.current_player || 0);
    let tagged = false;
    for (let i = hits.length - 1; i >= 0; i--) {
      if (hits[i].segment === focusHit.segment && hits[i].ring === focusHit.ring && hits[i].number === focusHit.number) {
        hits[i] = Object.assign({}, hits[i], { _focus: true, _idx: focusI });
        tagged = true;
        break;
      }
    }
    if (!tagged) hits.push(Object.assign({}, focusHit, { color: col, _focus: true, _idx: focusI }));
  }
  const freshHit = (fresh && (h.number || h.ring)) ? h : (visit[visit.length - 1] || null);
  const lastSig = visit.length ? dartSig(visit[visit.length - 1]) + '|' + visit.length : '';
  const freshAnim = !reduceMotion() && isNewVisitDart(lastSig);
  const playingNow = playing === 'playing';
  const pc = playingNow ? (GS.current_player_color || pcol(GS.current_player || 0)) : '';
  const label = h.segment ? (h.segment === 'OUT' ? 'Miss' : h.segment) : 'Waiting For A Hit';
  const RN = { single_inner: 'Single', single_outer: 'Single', treble: 'Triple', double: 'Double', bull: 'Outer Bull', bullseye: 'Bullseye', miss: 'Miss' };
  const sub = h.segment ? ((RN[h.ring] || '') + (h.score !== undefined && h.ring !== 'miss' ? ' · ' + h.score : '')) : 'Last Hit Shows Here';
  const glow = boardGlowState();
  const glowCls = glow.kind ? ' glow-' + glow.kind : '';
  const glowZs = (glow.zones || []).map((c, i) => c ? `--z${i}:${c};` : '').join('');
  const glowSt = (glow.color ? `--board-glow:${glow.color};` : '') + `--board-glow-a:${glow.alpha};--board-glow-dur:${glow.dur || 8}s;` + glowZs;
  return `<div class="board-side${playingNow ? '' : ' idle'}${glowCls}" style="--pc:${pc || 'var(--accent-color, var(--primary-color))'};${glowSt}"><div class="board-art"><div class="board-glow-bloom" aria-hidden="true"></div><div class="board-glow-rainbow-clip" aria-hidden="true"><i class="board-glow-prism"></i></div><svg viewBox="-205 -205 410 410" overflow="visible">${boardArt(hits, freshHit, { freshAnim, focusHit, focusIdx: focusI })}</svg></div><div class="hitlbl"><b>${esc(label)}</b><span>${esc(sub)}</span></div></div>`;
}
function renderDartCard(d, i, kind) {
  const latest = !!(d && ((gs().darts || []).length - 1 === i));
  const focus = focusedDartIndex() === i;
  const reduce = reduceMotion();
  const next = cropBox(d, i);
  const mem = (typeof window !== 'undefined') ? (window.__dartsCropVB = window.__dartsCropVB || {}) : {};
  const key = (kind || 'tv') + ':' + i;
  const sig = dartSig(d);
  const changed = mem[key + '_sig'] !== sig;
  const prev = mem[key];
  let from = next;
  if (changed && !reduce) {
    from = prev || (d ? { x: -125, y: -125, w: 250, h: 250 } : next);
  }
  mem[key] = next;
  mem[key + '_sig'] = sig;
  const animate = changed && !reduce && (from.x !== next.x || from.y !== next.y || from.w !== next.w);
  const pulse = latest && changed && !!d && !reduce;
  const pos = d ? dartPos(d, i) : null;
  const pc = gs().current_player_color || pcol(gs().current_player || 0);
  const anim = animate ? `<animate attributeName="viewBox" dur="0.55s" fill="freeze" begin="0s" from="${cropVb(from)}" to="${cropVb(next)}"/>` : '';
  const pin = pos ? dartGraphic(pos.x, pos.y, pc, { idx: i, fresh: pulse, focus: focus, scale: 2.55 }) : '';
  const val = d && d.score !== undefined && d.score !== null ? d.score : '';
  const seg = d ? (d.segment === 'OUT' ? 'Miss' : (d.segment || '')) : 'Waiting';
  const cls = [(kind === 'phone' ? 'key-dart dart-card' : 'dart-card'), d ? '' : 'empty', focus ? 'focus' : '', pulse ? 'just-landed' : '', (latest && d) ? 'latest' : ''].filter(Boolean).join(' ');
  const click = d ? `${da('focusDart', i)}` : '';
  return `<button type="button" class="${cls}" data-dart="${i}" ${click} style="--pc:${pc}" aria-label="${d ? ('Dart ' + (i + 1) + ' ' + seg) : ('Dart ' + (i + 1) + ' Waiting')}">
    <svg viewBox="${cropVb(animate ? from : next)}" overflow="hidden">${boardArt([], null)}${pin}${anim}</svg>
    <div class="dc-meta">${d ? `<b>${esc(val)}</b><span>${esc(seg)}</span>` : `<span class="wait">Waiting</span>`}</div>
  </button>`;
}

function sectionGame() {
  const a = gs(), state = st(E.game).state;
  const offline = isBoardOffline();
  const playing = !offline && (state === 'playing' || state === 'finished');
  const people = (a.players && a.players.length) ? a.players : (helperNames().length ? helperNames() : ['Player 1', 'Player 2']).map((name, i) => ({ name, score: null, color: pcol(i), stats: {} }));
  const curIdx = (state === 'playing' || state === 'finished') ? (a.current_player || 0) : -1;
  const pc = a.current_player_color || pcol(curIdx >= 0 ? curIdx : 0);
  const darts = a.darts || [];
  const shortName = playing ? (a.game === 'x01' || a.game === '301' || a.game === '501' ? String(a.start || gameName(a)) : gameName(a)) : 'Darts';
  const inChip = 'Straight In';
  const outChip = a.double_out ? 'Double Out' : 'Straight Out';
  const pL = people[0] || { name: 'Player 1', color: pcol(0) };
  const pR = people[1];
  const av = (p, cur) => `<div class="avatar ${cur ? 'on' : ''}" style="--pc:${p.color || pcol(0)}">${esc((p.name || '?').trim().charAt(0).toUpperCase())}</div>`;
  const title = playing ? esc(shortName) : 'Ready To Throw';
  const sub = playing ? (a.round ? `Round ${a.round}${a.rounds ? ' / ' + a.rounds : ''}` : 'Match') : 'Pick A Game To Start';
  const banner = `<div class="match">
    ${av(pL, curIdx === 0)}
    <div class="match-mid">
      <div class="match-title">${title}</div>
      <div class="match-sub">${esc(sub)}</div>
      <div class="chips"><span>${inChip}</span><span>${outChip}</span></div>
    </div>
    ${pR ? av(pR, curIdx === 1) : '<div></div>'}
  </div>`;
  const rounds = availableRounds();
  const leg = selectedLeg();
  const legs = (playing && rounds.length) ? `<div class="legs" role="tablist" aria-label="Rounds">
    <button type="button" data-leg="all" class="${leg === 'all' ? 'on' : ''}" ${da('leg', 'all')}>All</button>
    ${rounds.map(r => `<button type="button" data-leg="${r}" class="${leg === String(r) ? 'on' : ''}" ${da('leg', r)}>${r}</button>`).join('')}
  </div>` : '';
  const col = (p, i) => {
    const cur = i === curIdx && state === 'playing';
    const s = p.stats || {};
    let score = p.score;
    if (!playing || score == null || score === '') score = '';
    if (playing && a.game === 'around_the_clock') score = (p.target === 0 ? 'Done' : (p.target ?? ''));
    const avgLbl = a.game === 'cricket' ? 'Mpr' : '3-Dart Avg';
    const avg = playing ? (a.game === 'cricket' ? (s.mpr ?? 0).toFixed(2) : (s.ppr != null ? Number(s.ppr).toFixed(1) : ((s.ppd ?? 0) * 3).toFixed(1))) : '—';
    const last = playing ? lastScoreFor(p.name) : null;
    const thrown = playing ? (s.darts ?? 0) : '—';
    const lastLbl = (last == null || last === '') ? '—' : last;
    return `<article class="pl ${cur ? 'cur' : ''}" style="--pc:${p.color || pcol(i)}">
      <div class="halo-wrap" aria-hidden="true"><span class="halo-glow"></span><span class="halo-ring"></span></div>
      <div class="pl-head">${av(p, cur)}<div class="pl-name">${esc(p.name)}${a.winner === p.name ? ' · Winner' : ''}</div></div>
      ${cur ? '<div class="your-turn">It\'s Your Turn</div>' : ''}
      <div class="pl-score ${(!playing || p.score == null) ? 'idle' : ''}">${esc(score)}</div>
      <dl class="pl-stats">
        <div><dt>${avgLbl}</dt><dd>${esc(avg)}</dd></div>
        <div><dt>Last Score</dt><dd>${esc(lastLbl)}</dd></div>
        <div><dt>Darts Thrown</dt><dd>${esc(thrown)}</dd></div>
      </dl>
    </article>`;
  };
  const two = people.length <= 2;
  const badge = `<div class="badge"><span class="badge-k">${playing ? 'Round' : 'Game'}</span><strong>${playing ? (a.round || 1) : ''}</strong><span class="badge-g">${esc(playing ? shortName : 'Ready')}</span></div>`;
  const scores = two
    ? `<div class="score-row">${col(people[0], 0)}${badge}${people[1] ? col(people[1], 1) : '<div></div>'}</div>`
    : `<div class="score-row multi">${people.map((p, i) => col(p, i)).join('')}</div>`;
  let slots = '';
  for (let i = 0; i < 3; i++) slots += renderDartCard(darts[i], i);
  const tray = `<div class="dart-tray"><div class="kicker">This Turn</div><div class="dart-cards">${slots}</div></div>`;
  let cr = '';
  if (a.game === 'cricket' && (a.players || []).length) {
    const T = ['20', '19', '18', '17', '16', '15', '25'];
    const mk = (m) => m >= 3 ? '<svg viewBox="0 0 20 20"><circle cx="10" cy="10" r="8"/><path d="M5 5L15 15M15 5L5 15"/></svg>' : m === 2 ? '<svg viewBox="0 0 20 20"><path d="M5 5L15 15M15 5L5 15"/></svg>' : m === 1 ? '<svg viewBox="0 0 20 20"><path d="M15 5L5 15"/></svg>' : '';
    const closed = (t) => people.every(p => (p.marks || {})[t] >= 3);
    cr = `<div class="section"><div class="section-h"><h2>Cricket Marks</h2></div><div class="cr" style="grid-template-columns:repeat(${people.length + 1},1fr)"><div class="ch"></div>${people.map(p => `<div class="ch">${esc(p.name)}</div>`).join('')}` +
      T.map(t => `<div class="ct ${closed(t) ? 'closed' : ''}">${t === '25' ? 'Bull' : t}</div>` + people.map((p, i) => `<div class="cm" style="--pc:${p.color || pcol(i)}">${mk((p.marks || {})[t] || 0)}</div>`).join('')).join('') + `</div></div>`;
  }
  const co = (a.checkout || []).length ? `<div class="co"><span class="lbl">Checkout</span>${a.checkout.map(s => `<b>${esc(s)}</b>`).join('<i>›</i>')}</div>` : '';
  let bannerMsg = '';
  if (state === 'finished' || a.winner) bannerMsg = `<div class="banner win">${esc(a.winner)} Wins</div>`;
  else if (a.bust) bannerMsg = `<div class="banner bust">Bust</div>`;
  else if (a.turn_complete) bannerMsg = `<div class="banner next">Pull Your Darts, Then Next Player</div>`;
  const modeId = n => ({ '301': '301', '501': '501', Cricket: 'cricket', 'Count-Up': 'count_up', 'Around The Clock': 'around_the_clock' }[n] || slug(n));
  const modesHtml = sfx => playing ? '' : `<div class="play-actions"><div class="kicker" style="margin-bottom:12px">New Game</div><div class="modes">${MODES.map(([n, d, c]) => iconTile('mode', n, false, da('startGame', d, c) + ' ' + ov('ng_' + modeId(n) + '_' + sfx))).join('')}</div></div>`;
  const modesTv = modesHtml('tv');
  const modesPhone = modesHtml('phone');
  const controls = `<div class="play-actions actions">
    <button type="button" class="btn quiet" ${da('call', 'granboard', 'undo', {})} ${ov('undo_tv')}>${ico(ICON.undo)} Undo</button>
    <button type="button" class="btn quiet" ${da('call', 'granboard', 'next_player', {})} ${ov('next_tv')}>${ico(ICON.next)} Next Player</button>
    <button type="button" class="btn quiet warn" ${da('confirm', 'End The Current Game?', 'granboard', 'end_game', {})} ${ov('end_tv')}>${ico(ICON.flag)} End Game</button>
  </div>`;
  const curP = (curIdx >= 0 ? people[curIdx] : people[0]) || { name: 'Player', stats: {} };
  const curI = curIdx >= 0 ? curIdx : 0;
  const oppP = people.length === 2 ? people[curI === 0 ? 1 : 0] : (people.filter((_, i) => i !== curI)[0] || null);
  let preVisit = null;
  if (playing && curP.score != null && curP.score !== '' && darts.length && a.turn_score) {
    const sc = Number(curP.score), ts = Number(a.turn_score);
    if (Number.isFinite(sc) && Number.isFinite(ts)) preVisit = a.game === 'count_up' ? sc - ts : sc + ts;
  }
  const curStats = curP.stats || {};
  const curPpr = playing ? (curStats.ppr != null ? Number(curStats.ppr).toFixed(1) : ((curStats.ppd ?? 0) * 3).toFixed(1)) : '—';
  const curLast = playing ? lastScoreFor(curP.name) : null;
  const curScore = (!playing || curP.score == null || curP.score === '') ? '' : (a.game === 'around_the_clock' ? (curP.target === 0 ? 'Done' : (curP.target ?? '')) : curP.score);
  const keyTiles = [0, 1, 2].map(i => renderDartCard(darts[i], i, 'phone')).join('');
  const key = `<section class="game-key" style="--pc:${pc}">
    <div class="key-head"><span class="key-mode">${title}</span><span class="key-meta">${esc(sub)}</span></div>
    <div class="key-hero-wrap ${state === 'playing' ? 'cur' : 'idle'}">
      <div class="key-halo halo-wrap" aria-hidden="true"><span class="halo-glow"></span><span class="halo-ring"></span></div>
      <div class="key-hero">
        <div class="key-left">${av(curP, state === 'playing')}
          <div>
            <div class="key-name">${esc(curP.name)}</div>
            <div class="key-mini"><span>Last Score <b>${esc(curLast == null || curLast === '' ? '—' : curLast)}</b></span><span>PPR <b>${esc(curPpr)}</b></span></div>
          </div>
        </div>
        <div class="key-score">${preVisit != null ? `<s class="prev">${esc(preVisit)}</s>` : ''}${curScore !== '' ? `<div class="now">${esc(curScore)}</div>` : ''}</div>
        ${oppP ? `<div class="key-opp"><span>${esc(oppP.name)}</span>${playing && oppP.score != null && oppP.score !== '' ? `<b>${esc(oppP.score)}</b>` : ''}</div>` : ''}
      </div>
    </div>
    <div class="key-visit">
      <div class="turn-total"><small>Turn Total</small><b>${playing ? ((a.darts || []).reduce((s, d) => s + (Number(d.score) || Number(d.points) || 0), 0) || a.turn_score || 0) : ''}</b></div>
      <div class="key-darts">${keyTiles}</div>
    </div>
    ${modesPhone}
    <div class="key-board">${renderBoard()}</div>
    ${co}${bannerMsg}${cr}
    <div class="key-bar">
      <button type="button" class="btn quiet" ${da('call', 'granboard', 'undo', {})} ${ov('undo_phone')}>${ico(ICON.undo)} Undo</button>
      <div class="key-turn">${!isBoardOffline() && state === 'playing' ? esc(curP.name) + '\'s Turn' : (isBoardOffline() ? 'Board Offline' : 'Ready To Throw')}</div>
      <button type="button" class="btn quiet" ${da('call', 'granboard', 'next_player', {})} ${ov('next_phone')}>${ico(ICON.next)} Next</button><button type="button" class="btn quiet warn" ${da('confirm', 'End The Current Game?', 'granboard', 'end_game', {})} ${ov('end_phone')}>${ico(ICON.flag)}</button>
    </div>
  </section>`;
  return `<section class="game-omni" style="--pc:${pc}">
    <div class="omni-left">${banner}${legs}${scores}${tray}${co}${bannerMsg}${cr}${controls}${modesTv}</div>
    <div class="omni-board">${renderBoard()}</div>
  </section>${key}`;
}

function sectionPlayers() {
  const roster = rosterEntries();
  const names = helperNames();
  const rows = (names.length ? names : ['Player 1', 'Player 2']).map((name, i) => {
    const col = (roster[i] && roster[i].color) || pcol(i);
    const id = (roster[i] && roster[i].id) || name;
    const remove = roster.length ? `<button type="button" class="btn quiet" title="Remove Player" ${da('removePlayer', id, name)} ${ov('remove_' + i)}>Remove</button>` : '';
    return `<div class="row" style="--pc:${col}"><button type="button" class="row-main" ${da('cycleColor', i)} ${ov('color_' + i)}><i class="bar"></i><div><div class="nm">${esc(name)}</div><div class="sub">Tap To Change Color</div></div><div class="pts swatch-chip" style="background:${col}"></div></button>${remove}</div>`;
  }).join('');
  const dbl = st(E.double).state === 'on';
  // PLAYER PROFILES HOOK: add-player field calls granboard.add_player when the roster sensor is present
  const add = hasProfileServices() ? `<div class="field"><label for="d-add">Add Player</label><input id="d-add" type="text" placeholder="Name" ${daKey('addPlayer', '$value')}></div>
    <p class="note">Player profiles are stored by the Granboard integration. Lineup changes use <code>granboard.set_lineup</code> when that action is available.</p>` : `<div class="field"><label for="d-players">Players (Comma Separated)</label><input id="d-players" type="text" value="${esc(st(E.players).state || '')}" ${daBlur('savePlayers', '$value')}></div>
    <div class="field"><label for="d-colors">Player Colors (Names Or #Hex)</label><input id="d-colors" type="text" value="${esc(st(E.colors).state || '')}" ${daBlur('saveColors', '$value')}></div>
    <p class="note">Names and colors are stored in helpers until Granboard player profiles (<code>granboard.add_player</code>, <code>update_player</code>, <code>remove_player</code>, <code>set_lineup</code> and <code>sensor.*_players</code>) are available. This tab will use them automatically.</p>`;
  return `<div class="section" style="margin-top:36px">
    <div class="section-h"><h2>Players</h2><span class="lede">Colors stay with each name</span></div>
    <div class="roster">${rows}</div>
    ${add}
    <button type="button" class="toggle ${dbl ? 'on' : ''}" ${da('toggle', 'input_boolean', E.double)} ${ov('double_out')}><span>Double Out (x01)</span><i></i></button>
  </div>`;
}

function swatchRow(items, onclick, isOn) {
  return `<div class="swatches">${items.map(([name, hex]) => `<button type="button" class="swatch ${isOn(hex, name) ? 'on' : ''}" title="${esc(name)}" style="background:${hex}" onclick="${onclick(hex, name)}"></button>`).join('')}</div>`;
}

function sectionRing() {
  const ring = st(E.ring);
  const rgb = (ring.attributes || {}).rgb_color;
  const hexNow = rgb && rgb.length ? ('#' + rgb.map(c => Number(c).toString(16).padStart(2, '0')).join('')) : '';
  const fx = (ring.attributes || {}).effect || '';
  const pal = st(E.palette).state || '';
  const c2 = String(st(E.color2).state || '').toLowerCase();
  const on = ring.state === 'on';
  const bri = Math.round(((ring.attributes || {}).brightness || 0) / 2.55);
  const palettes = paletteBank();
  const colorBtns = COLOR1.map(([n, hex, rgb], i) => `<button type="button" class="swatch ${hexNow.toLowerCase() === hex.toLowerCase() ? 'on' : ''}" title="${n}" style="background:${hex}" ${da('lightOn', E.ring, { rgb_color: rgb })} ${ov('ring_c1_' + i)}></button>`).join('');
  const c2btns = COLOR1.map(([n, hex], i) => `<button type="button" class="swatch ${c2 === hex.toLowerCase() ? 'on' : ''}" title="${n}" style="background:${hex}" ${da('setText', E.color2, hex)} ${ov('ring_c2_' + i)}></button>`).join('');
  return `<div class="section" style="margin-top:36px">
    <div class="section-h"><h2>LED Ring</h2><div class="actions">
      <button type="button" class="btn" ${da('toggle', 'light', E.ring)} ${ov('ring_toggle')}>${on ? 'Turn Off' : 'Turn On'}</button>
      <button type="button" class="btn quiet" ${da('more', E.ring)} ${ov('ring_more')}>More Colors</button>
    </div></div>
    <div class="range"><label>Brightness <span>${on ? bri + '%' : 'Off'}</span></label><input type="range" min="1" max="100" value="${bri || 50}" ${daChange('lightBri', E.ring, '$value')}></div>
    <div class="section-h"><h2>Color 1</h2></div>
    <div class="swatches">${colorBtns}</div>
    <div class="section-h" style="margin-top:36px"><h2>Color 2</h2></div>
    <div class="swatches">${c2btns}<button type="button" class="swatch ${!c2 ? 'on' : ''}" title="Auto" style="background:linear-gradient(135deg,#f3f4f7 0 50%,transparent 50%);border-color:color-mix(in srgb,#f3f4f7 45%,transparent)" ${da('setText', E.color2, '')} ${ov('ring_c2_auto')}></button></div>
    <div class="section-h" style="margin-top:36px"><h2>Effects</h2></div>
    <div class="fx icon-row">${RING_FX.map(n => iconTile('fx', n, fx === n, da('lightOn', E.ring, { effect: n }) + ' ' + ov('ring_fx_' + slug(n)))).join('')}</div>
    <div class="section-h" style="margin-top:36px"><h2>Palettes</h2></div>
    <div class="palettes">${palettes.map((p, i) => `<button type="button" class="pal ${pal === p.name ? 'on' : ''}" style="background:${p.gradient}" ${da('setSelect', E.palette, p.name)} ${ov('ring_pal_' + i)}>${esc(p.name)}</button>`).join('')}</div>
    <div class="section-h" style="margin-top:36px"><h2>Speed And Intensity</h2></div>
    <div class="range"><label>Ring Speed <span>${esc(st(E.speed).state || '')}</span></label><input type="range" min="${attr(E.speed).min ?? 0}" max="${attr(E.speed).max ?? 255}" value="${st(E.speed).state || 0}" ${daChange('setNumber', E.speed, '$value')}></div>
    <div class="range"><label>Ring Intensity <span>${esc(st(E.intensity).state || '')}</span></label><input type="range" min="${attr(E.intensity).min ?? 0}" max="${attr(E.intensity).max ?? 255}" value="${st(E.intensity).state || 0}" ${daChange('setNumber', E.intensity, '$value')}></div>
  </div>`;
}

function sectionRoom() {
  const units = wledUnits();
  if (!units.length) {
    return `<div class="section" style="margin-top:36px">
      <div class="section-h"><h2>Room Lights</h2></div>
      <p class="note">No WLED light is configured. To add cabinet or room lights, set <code>DARTS_CONFIG.wled</code> in this dashboard to your WLED entities. This section is optional.</p>
    </div>`;
  }
  const pals = paletteBank();
  const openMap = wledOpenMap();
  const chevron = '<svg viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M7.4 8.6L12 13.2L16.6 8.6L18 10L12 16L6 10L7.4 8.6Z"></path></svg>';
  const blocks = units.map((u, ui) => {
    const light = st(u.light);
    const on = light.state === 'on';
    const fx = (light.attributes || {}).effect || '';
    const pal = u.palette ? (st(u.palette).state || '') : '';
    const preset = u.preset ? (st(u.preset).state || '') : '';
    const bri = Math.round(((light.attributes || {}).brightness || 0) / 2.55);
    const presets = u.preset ? ((attr(u.preset).options) || ['Aquatic Flow', 'Rainbow']) : [];
    const suffix = slug(u.light) + '_' + ui;
    const defaultOpen = openMap[u.light] !== false;
    const openCls = defaultOpen ? ' open' : '';
    const presetRow = u.preset ? `<div class="section-h"><h2>Presets</h2></div>
    <div class="preset-row icon-row">${presets.map((n, i) => iconTile('preset', n, preset === n, da('setSelect', u.preset, n) + ' ' + ov('room_' + suffix + '_preset_' + i))).join('')}</div>` : '';
    const fxRow = `<div class="section-h" style="margin-top:36px"><h2>Effects</h2></div>
    <div class="fx icon-row">${TREE_FX.map(n => iconTile('fx', n, fx === n, da('lightOn', u.light, { effect: n }) + ' ' + ov('room_' + suffix + '_fx_' + slug(n)))).join('')}</div>`;
    const palRow = u.palette ? `<div class="section-h" style="margin-top:36px"><h2>Palettes</h2></div>
    <div class="palettes">${pals.map((p, i) => `<button type="button" class="pal ${pal === p.name ? 'on' : ''}" style="background:${p.gradient}" ${da('setSelect', u.palette, p.name)} ${ov('room_' + suffix + '_pal_' + i)}>${esc(p.name)}</button>`).join('')}</div>` : '';
    const speedRow = (u.speed || u.intensity) ? `<div class="section-h" style="margin-top:36px"><h2>Speed And Intensity</h2></div>
    ${u.speed ? `<div class="range"><label>Speed <span>${esc(st(u.speed).state || '')}</span></label><input type="range" min="${attr(u.speed).min ?? 0}" max="${attr(u.speed).max ?? 255}" value="${st(u.speed).state || 0}" ${daChange('setNumber', u.speed, '$value')}></div>` : ''}
    ${u.intensity ? `<div class="range"><label>Intensity <span>${esc(st(u.intensity).state || '')}</span></label><input type="range" min="${attr(u.intensity).min ?? 0}" max="${attr(u.intensity).max ?? 255}" value="${st(u.intensity).state || 0}" ${daChange('setNumber', u.intensity, '$value')}></div>` : ''}` : '';
    return `<article class="wled-unit${openCls}" data-wled="${esc(u.light)}" aria-expanded="${defaultOpen ? 'true' : 'false'}">
      <div class="wled-h">
        <button type="button" class="wled-name" ${da('toggleWledPanel', u.light)}>${chevron}<span>${esc(u.name)}</span></button>
        <div class="actions">
          <button type="button" class="btn" ${da('toggle', 'light', u.light)} ${ov('room_' + suffix + '_toggle')}>${on ? 'Turn Off' : 'Turn On'}</button>
          <button type="button" class="btn quiet" ${da('more', u.light)} ${ov('room_' + suffix + '_more')}>More Effects</button>
        </div>
      </div>
      <div class="wled-body">
        <div class="range"><label>Brightness <span>${on ? bri + '%' : 'Off'}</span></label><input type="range" min="1" max="100" value="${bri || 50}" ${daChange('lightBri', u.light, '$value')}></div>
        ${presetRow}${fxRow}${palRow}${speedRow}
      </div>
    </article>`;
  }).join('');
  return `<div class="section" style="margin-top:36px">
    <div class="section-h"><h2>Room Lights</h2></div>
    ${units.length === 1 ? '<p class="note">Only Tree Lights are on this page until the dart area is set up.</p>' : ''}
    ${blocks}
  </div>`;
}

function sectionSounds() {
  const theme = st(E.theme);
  if (theme.state === 'unavailable') return `<div class="section" style="margin-top:36px"><div class="section-h"><h2>Sounds</h2></div><p class="note">The Sound Theme entity is unavailable.</p></div>`;
  const opts = (theme.attributes || {}).options || [];
  const cur = theme.state || '';
  return `<div class="section" style="margin-top:36px">
    <div class="section-h"><h2>Sound Theme</h2></div>
    <div class="theme-row icon-row">${opts.map((n, i) => iconTile('theme', n, cur === n, da('setSelect', E.theme, n) + ' ' + ov('theme_' + i))).join('')}</div>
    <p class="note">Themes live in /config/www/granboard/sounds. Alexa speakers need Alexa Media Player and a public HTTPS URL.</p>
  </div>`;
}


const GLOW_CHOICES = [
  ['auto', 'Auto'],
  ['player', 'Player Color'],
  ['#5dade2', 'Azure'],
  ['#64d2ff', 'Cyan'],
  ['#bf5af2', 'Violet'],
  ['#3dd68c', 'Mint'],
  ['#ff2ad0', 'Magenta'],
  ['off', 'Off']
];
const GLOW_RAINBOW_Z = ['#ff2a6d', '#ff8a00', '#ffe600', '#2bff88', '#00d5ff', '#2f6bff', '#8a2bff', '#ff2ad0'];
const GLOW_KINDS = ['off', 'rainbow', 'solid', 'blink', 'breathe', 'heartbeat', 'wave', 'cycle', 'steps', 'chase', 'bounce', 'wipe', 'twinkle', 'fire', 'police', 'lightning', 'hue'];
const GLOW_TICK_FX = { wave: 1, cycle: 1, steps: 1, chase: 1, bounce: 1, wipe: 1, twinkle: 1, fire: 1, police: 1, lightning: 1 };
const GLOW_DEFAULT_PAL = {
  'Color Cycle': 'Rainbow',
  'Palette Steps': 'Rainbow',
  'Rainbow Chase': 'Rainbow',
  'Circular Rainbow': 'Rainbow',
  'Fire Flicker': 'Fire'
};
function glowMode() {
  try { return localStorage.getItem('dartsArenaGlow') || 'auto'; } catch (e) { return 'auto'; }
}
function hsToRgbArr(h, s, v) {
  s = Number(s); v = (v == null ? 1 : Number(v));
  const c = v * s, x = c * (1 - Math.abs(((h / 60) % 2) - 1)), m = v - c;
  let r = 0, g = 0, b = 0;
  if (h < 60) { r = c; g = x; }
  else if (h < 120) { r = x; g = c; }
  else if (h < 180) { g = c; b = x; }
  else if (h < 240) { g = x; b = c; }
  else if (h < 300) { r = x; b = c; }
  else { r = c; b = x; }
  return [r, g, b].map(n => Math.round((n + m) * 255));
}
function hsToRgbCss(h, s, v) { return 'rgb(' + hsToRgbArr(h, Number(s) / 100, v).join(',') + ')'; }
function rgbCss(rgb) { return 'rgb(' + rgb.map(n => Math.max(0, Math.min(255, Math.round(n)))).join(',') + ')'; }
function lerpRgb(a, b, t) { return a.map((x, i) => Math.round(x + (b[i] - x) * t)); }
function hueAt(pos) { return hsToRgbArr((((pos % 256) + 256) % 256) / 256 * 360, 1, 1); }
function complementRgb(rgb) {
  const mx = Math.max.apply(null, rgb), mn = Math.min.apply(null, rgb);
  if (mx === mn) return [0, 0, 0];
  const [r, g, b] = rgb.map(c => c / 255);
  const max = Math.max(r, g, b), min = Math.min(r, g, b), d = max - min;
  let h = 0;
  if (d) {
    if (max === r) h = ((g - b) / d) % 6;
    else if (max === g) h = (b - r) / d + 2;
    else h = (r - g) / d + 4;
    h *= 60;
    if (h < 0) h += 360;
  }
  const s = max ? d / max : 0;
  return hsToRgbArr((h + 180) % 360, s, max);
}
function parseRgbValue(s) {
  if (!s) return null;
  const t = String(s).trim();
  const m = t.match(/rgb\(\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)/i);
  if (m) return [Number(m[1]), Number(m[2]), Number(m[3])];
  const hx = t.replace(/^#/, '');
  if (/^[0-9a-f]{6}$/i.test(hx)) return [parseInt(hx.slice(0, 2), 16), parseInt(hx.slice(2, 4), 16), parseInt(hx.slice(4, 6), 16)];
  if (/^[0-9a-f]{3}$/i.test(hx)) return [parseInt(hx[0] + hx[0], 16), parseInt(hx[1] + hx[1], 16), parseInt(hx[2] + hx[2], 16)];
  return null;
}
function currentPlayerColor() {
  try {
    const L = lightingState();
    return L.pc || 'var(--primary-color, #5dade2)';
  } catch (e) { return 'var(--primary-color, #5dade2)'; }
}
const RING_EFFECT_NAMES = ['Solid', 'Blink', 'Breathe', 'Heartbeat', 'Wave', 'Color Cycle', 'Palette Steps', 'Chase', 'Rainbow Chase', 'Circular Rainbow', 'Rainbow Sweep', 'Bounce', 'Circular Wipe', 'Twinkle', 'Fire Flicker', 'Police', 'Lightning'];
function hassStateMap() {
  try {
    const h = (typeof hassObj === 'function') ? hassObj() : null;
    if (h && h.states) return h.states;
  } catch (e) {}
  return {};
}
function findEntityId(patterns, fallback) {
  const map = hassStateMap();
  if (fallback && map[fallback]) return fallback;
  const ids = Object.keys(map);
  for (let i = 0; i < patterns.length; i++) {
    const re = patterns[i];
    const hit = ids.find(id => re.test(id) && map[id]);
    if (hit) return hit;
  }
  return fallback || '';
}
function ringEntity(kind) {
  const p = (typeof DARTS_CONFIG !== 'undefined' && DARTS_CONFIG.prefix) || 'game_room_granboard_3s';
  const cfg = (typeof E !== 'undefined' && E) || {};
  if (kind === 'palette') return findEntityId([new RegExp('^select\\.' + p + '_ring_palette$'), /select\.[\w]*granboard[\w]*ring_palette$/], cfg.palette || ('select.' + p + '_ring_palette'));
  if (kind === 'speed') return findEntityId([new RegExp('^number\\.' + p + '_ring_speed$'), /number\.[\w]*granboard[\w]*ring_speed$/], cfg.speed || ('number.' + p + '_ring_speed'));
  if (kind === 'intensity') return findEntityId([new RegExp('^number\\.' + p + '_ring_intensity$'), /number\.[\w]*granboard[\w]*ring_intensity$/], cfg.intensity || ('number.' + p + '_ring_intensity'));
  if (kind === 'color2') return findEntityId([new RegExp('^text\\.' + p + '_ring_color_2$'), /text\.[\w]*granboard[\w]*ring_color_2$/], cfg.color2 || ('text.' + p + '_ring_color_2'));
  return findEntityId([
    new RegExp('^light\\.' + p + '_led_ring$'),
    /light\.[\w]*granboard[\w]*led_ring$/,
    /light\.[\w]*granboard[\w]*_ring$/
  ], cfg.ring || ('light.' + p + '_led_ring'));
}
function ringState() { return st(ringEntity('ring')); }
function canonicalEffect(name) {
  const key = String(name || 'Solid').trim().toLowerCase().replace(/[_-]+/g, ' ').replace(/\s+/g, ' ');
  const exact = RING_EFFECT_NAMES.find(n => n.toLowerCase() === key);
  if (exact) return exact;
  if (/rainbow\s*sweep|native\s*rainbow/.test(key)) return 'Rainbow Sweep';
  if (/circular\s*rainbow/.test(key)) return 'Circular Rainbow';
  if (/rainbow\s*chase/.test(key)) return 'Rainbow Chase';
  if (/color\s*cycle|color\s*loop|colorloop/.test(key)) return 'Color Cycle';
  if (/palette/.test(key)) return 'Palette Steps';
  if (/rainbow/.test(key)) return 'Circular Rainbow';
  if (/breath|fade/.test(key)) return 'Breathe';
  if (/heart/.test(key)) return 'Heartbeat';
  if (/blink/.test(key)) return 'Blink';
  if (/chase/.test(key)) return 'Chase';
  if (/bounce/.test(key)) return 'Bounce';
  if (/wipe/.test(key)) return 'Circular Wipe';
  if (/twinkle|sparkle/.test(key)) return 'Twinkle';
  if (/fire|flicker|candle/.test(key)) return 'Fire Flicker';
  if (/police/.test(key)) return 'Police';
  if (/lightning/.test(key)) return 'Lightning';
  if (/wave/.test(key)) return 'Wave';
  if (/solid|static/.test(key)) return 'Solid';
  return name ? String(name).trim() : 'Solid';
}
function ringIsOn() {
  const l = ringState();
  const s = String((l && l.state) || '').toLowerCase();
  return s === 'on';
}
function ringPausedForGame() {
  const a = (ringState().attributes || {});
  if (a.paused_for_game === true || a.paused_for_game === 'true' || a.paused_for_game === 'on') return true;
  try {
    const gs = String((st(E.game).state) || '').toLowerCase();
    if (gs === 'playing') return true;
  } catch (e) {}
  return false;
}
function ringLedRgb() {
  const l = ringState();
  const a = (l && l.attributes) || {};
  if (Array.isArray(a.rgb_color) && a.rgb_color.length >= 3) return a.rgb_color.slice(0, 3).map(Number);
  if (Array.isArray(a.hs_color) && a.hs_color.length >= 2) {
    const bri = a.brightness != null ? Number(a.brightness) / 255 : 1;
    return hsToRgbArr(Number(a.hs_color[0]), Number(a.hs_color[1]) / 100, bri);
  }
  return [255, 255, 255];
}
function ringLedColor() { return ringIsOn() ? rgbCss(ringLedRgb()) : ''; }
function ringColor2Rgb(c1) {
  try {
    const raw = String((st(ringEntity('color2')).state) || '').trim();
    const parsed = parseRgbValue(raw);
    if (parsed) return parsed;
  } catch (e) {}
  return complementRgb(c1);
}
function glowSpeedFactor() {
  let s = 128;
  try { s = parseInt(st(ringEntity('speed')).state, 10); } catch (e) {}
  if (!Number.isFinite(s)) s = 128;
  return Math.pow(2, (128 - Math.max(0, Math.min(255, s))) / 64);
}
function glowIntensity() {
  let k = 128;
  try { k = parseInt(st(ringEntity('intensity')).state, 10); } catch (e) {}
  if (!Number.isFinite(k)) k = 128;
  return Math.max(0, Math.min(255, k));
}
const _palStopCache = {};
function paletteStops(name) {
  if (_palStopCache[name]) return _palStopCache[name];
  const bank = (typeof DARTS_PALETTES !== 'undefined' && DARTS_PALETTES) || [];
  const found = bank.find(p => p && p.name === name);
  const stops = [];
  if (found && found.gradient) {
    const re = /#([0-9a-f]{6})\s+(\d+)%/gi;
    let m;
    while ((m = re.exec(found.gradient))) {
      const h = m[1];
      stops.push([Math.round(Number(m[2]) * 255 / 100), [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]]);
    }
  }
  _palStopCache[name] = stops;
  return stops;
}
function colorAt(name, pos, c1, c2) {
  pos = ((pos % 256) + 256) % 256;
  if (!name || name === 'Color 1') return c1;
  if (name === 'Colors 1&2') return pos < 128 ? c1 : c2;
  if (name === 'Color Gradient') return lerpRgb(c1, c2, 1 - Math.abs(pos - 128) / 128);
  if (name === 'Rainbow Bands') return hueAt(Math.floor(pos / 32) * 32);
  if (name === 'Rainbow' || name === 'Default') return hueAt(pos);
  const stops = paletteStops(name);
  if (!stops.length) return hueAt(pos);
  let prev = stops[0];
  for (let i = 0; i < stops.length; i++) {
    const stop = stops[i];
    if (stop[0] >= pos) {
      if (stop[0] === prev[0]) return stop[1];
      return lerpRgb(prev[1], stop[1], (pos - prev[0]) / (stop[0] - prev[0]));
    }
    prev = stop;
  }
  return stops[stops.length - 1][1];
}
function paletteForEffect(fx, palName) {
  if (palName && palName !== 'Default') return palName;
  return GLOW_DEFAULT_PAL[fx] || null;
}
function ringEffectName() {
  try { return canonicalEffect((ringState().attributes || {}).effect || 'Solid'); } catch (e) { return 'Solid'; }
}
function ringPaletteName() {
  try { return String((st(ringEntity('palette')).state) || 'Default'); } catch (e) { return 'Default'; }
}
function ringGlowAlpha() {
  let alpha = 0.55;
  try {
    const bri = Number((st(E.ring).attributes || {}).brightness);
    if (Number.isFinite(bri)) alpha = 0.45 + 0.15 * (bri / 255);
  } catch (e) {}
  return alpha;
}
function glowZonesFor(fx, t, ctx) {
  const { pal, c1, c2, alpha, k, factor } = ctx;
  const wait = ms => ms * factor;
  const at = pos => colorAt(pal || 'Color 1', pos, c1, c2);
  const css = pos => rgbCss(at(pos));
  const fill = c => Array(8).fill(c);
  switch (fx) {
    case 'Blink':
      return { kind: 'blink', zones: fill(rgbCss(c1)), alpha, dur: wait(1200) / 1000, color: rgbCss(c1) };
    case 'Breathe': {
      const floor = 1 - 0.9 * k / 255;
      return { kind: 'breathe', zones: fill(rgbCss(c1)), alpha, dur: wait(350 * 16) / 1000, floor: Math.max(0.08, floor * alpha), color: rgbCss(c1) };
    }
    case 'Heartbeat':
      return { kind: 'heartbeat', zones: fill(rgbCss(c1)), alpha, dur: wait(1700) / 1000, color: rgbCss(c1) };
    case 'Wave': {
      const step = Math.floor(t / wait(4000));
      const a = pal ? at(step * 64) : c1;
      const b = pal ? at(step * 64 + 128) : c2;
      const off = (t / wait(4000)) % 1;
      const zones = [];
      for (let i = 0; i < 8; i++) {
        const u = (i / 8 + off) % 1;
        zones.push(rgbCss(lerpRgb(a, b, 0.5 - 0.5 * Math.cos(u * Math.PI * 2))));
      }
      return { kind: 'wave', zones, alpha, color: rgbCss(a) };
    }
    case 'Circular Rainbow': {
      const pos = (t / wait(1200)) * 17;
      const zones = [];
      for (let i = 0; i < 8; i++) zones.push(css(pos + i * 32));
      return { kind: 'wave', zones, alpha, color: css(pos) };
    }
    case 'Color Cycle': {
      const c = css((t / wait(500)) * 8);
      return { kind: 'cycle', zones: fill(c), alpha, color: c };
    }
    case 'Palette Steps': {
      const count = 4 + Math.round(k / 255 * 12);
      const step = Math.floor(t / wait(2500)) % count;
      const c = css(Math.round(step * 256 / count));
      return { kind: 'steps', zones: fill(c), alpha, color: c };
    }
    case 'Chase':
    case 'Rainbow Chase': {
      const step = Math.floor(t / wait(300));
      const i = ((step % 20) + 20) % 20;
      const z = Math.round(i * 8 / 20) % 8;
      const col = at(i * 256 / 20);
      const base = col.map(x => Math.round(x * 0.12));
      const zones = fill(rgbCss(base));
      zones[z] = rgbCss(col);
      zones[(z + 7) % 8] = rgbCss(lerpRgb(col, base, 0.55));
      return { kind: 'chase', zones, alpha, color: rgbCss(col) };
    }
    case 'Bounce': {
      const step = Math.floor(t / wait(250)) % 38;
      const i = step < 20 ? step : 38 - step;
      const z = Math.round(i * 8 / 20) % 8;
      const col = at(i * 256 / 20);
      const base = col.map(x => Math.round(x * 0.12));
      const zones = fill(rgbCss(base));
      zones[z] = rgbCss(col);
      zones[(z + 7) % 8] = rgbCss(lerpRgb(col, base, 0.55));
      return { kind: 'bounce', zones, alpha, color: rgbCss(col) };
    }
    case 'Circular Wipe': {
      const fillMs = 20 * wait(250), gap = wait(1500), u = t % (fillMs + gap);
      if (u >= fillMs) return { kind: 'wipe', zones: fill('rgba(0,0,0,0)'), alpha: 0.04, color: rgbCss(c1) };
      const filled = Math.floor((u / wait(250)) * 8 / 20);
      const zones = [];
      for (let z = 0; z < 8; z++) zones.push(z <= filled ? css(z * 32) : 'rgba(0,0,0,0)');
      return { kind: 'wipe', zones, alpha, color: css(0) };
    }
    case 'Twinkle': {
      const baseMs = Math.max(80, (900 - 600 * k / 255) * factor);
      const n = Math.floor(t / baseMs);
      const zones = fill('rgba(0,0,0,0)');
      for (let j = 0; j < 3; j++) {
        const seed = n - j;
        if (seed < 0) continue;
        const z = ((seed * 7 + j * 3) % 8 + 8) % 8;
        const fade = 1 - j / 3;
        const col = at((seed * 53) % 256).map(x => Math.round(x * fade));
        zones[z] = rgbCss(col);
      }
      return { kind: 'twinkle', zones, alpha };
    }
    case 'Fire Flicker': {
      const depth = 0.6 * k / 255;
      const p = pal || 'Fire';
      const zones = [];
      for (let i = 0; i < 8; i++) {
        const seed = Math.floor(t / (400 + i * 37));
        const col = colorAt(p, 110 + ((seed * 37 + i * 19) % 120), c1, c2);
        const level = 1 - depth * (((seed * 13 + i * 7) % 100) / 100);
        zones.push(rgbCss(col.map(x => Math.round(x * level))));
      }
      return { kind: 'fire', zones, alpha, color: zones[0] };
    }
    case 'Police': {
      const onRed = Math.floor(t / wait(400)) % 2 === 0;
      const c = onRed ? 'rgb(255,0,0)' : 'rgb(0,0,255)';
      return { kind: 'police', zones: fill(c), alpha, color: c, dur: wait(400) / 1000 };
    }
    case 'Lightning': {
      const gap = (6000 - 4500 * k / 255) * factor;
      const u = t % Math.max(400, gap);
      const flash = u < 80 || (u > 140 && u < 200) || (u > 240 && u < 280);
      const c = rgbCss(c1);
      return { kind: 'lightning', zones: fill(c), alpha: flash ? Math.min(0.6, Math.max(0.5, alpha)) : 0.08, color: c };
    }
    case 'Rainbow Sweep':
      return { kind: 'rainbow', zones: GLOW_RAINBOW_Z.slice(), alpha, dur: 2, color: '' };
    default: {
      if (pal && pal !== 'Color 1') {
        const c = css((t / wait(800)) * 8);
        return { kind: 'cycle', zones: fill(c), alpha, color: c };
      }
      return { kind: 'solid', zones: fill(rgbCss(c1)), alpha, color: rgbCss(c1) };
    }
  }
}
function boardGlowState(now) {
  const mode = glowMode();
  const empty = ['', '', '', '', '', '', '', ''];
  if (mode === 'off') return { kind: 'off', color: '', zones: empty, alpha: 0, dur: 8 };
  if (mode === 'player') {
    const c = currentPlayerColor();
    return { kind: 'solid', color: c, zones: Array(8).fill(c), alpha: 0.55, dur: 8 };
  }
  if (mode && mode.charAt(0) === '#') {
    return { kind: 'solid', color: mode, zones: Array(8).fill(mode), alpha: 0.55, dur: 8 };
  }
  if (ringPausedForGame()) {
    let c = currentPlayerColor();
    let hit = '';
    let fresh = false;
    try {
      const L = lightingState();
      if (L.pc) c = L.pc;
      fresh = !!L.fresh;
      hit = L.hitColor || c;
    } catch (e) {}
    if (fresh && hit) {
      const zones = Array(8).fill(c);
      const z = (typeof lastHitZone === 'function') ? lastHitZone() : -1;
      if (z >= 0) { zones[z] = hit; zones[(z + 7) % 8] = hit; }
      else { for (let i = 0; i < 8; i++) zones[i] = hit; }
      return { kind: 'solid', color: hit, zones, alpha: 0.6, dur: 8 };
    }
    return { kind: 'solid', color: c, zones: Array(8).fill(c), alpha: 0.55, dur: 8 };
  }
  if (!ringIsOn()) return { kind: 'rainbow', color: '', zones: GLOW_RAINBOW_Z.slice(), alpha: 0.55, dur: 18 };
  const c1 = ringLedRgb();
  const c2 = ringColor2Rgb(c1);
  const fx = ringEffectName();
  const pal = paletteForEffect(fx, ringPaletteName());
  const t = (now == null ? (typeof performance !== 'undefined' ? performance.now() : Date.now()) : now);
  const g = glowZonesFor(fx, t, { pal, c1, c2, alpha: ringGlowAlpha(), k: glowIntensity(), factor: glowSpeedFactor() });
  return g;
}
function boardGlowNeedsTick() {
  const g = boardGlowState(0);
  return !!(g && GLOW_TICK_FX[g.kind]);
}
function applyBoardGlow(root, now) {
  const host = root || appRoot();
  if (!host) return;
  const g = boardGlowState(now);
  host.querySelectorAll('.board-side').forEach(el => {
    GLOW_KINDS.forEach(k => el.classList.toggle('glow-' + k, g.kind === k));
    if (g.color) el.style.setProperty('--board-glow', g.color);
    el.style.setProperty('--board-glow-a', String(g.alpha));
    if (g.dur) el.style.setProperty('--board-glow-dur', g.dur + 's');
    if (g.floor != null) el.style.setProperty('--glow-floor', String(g.floor));
    const bloom = el.querySelector('.board-glow-bloom') || el;
    (g.zones || []).forEach((c, i) => { if (c) bloom.style.setProperty('--z' + i, c); });
  });
  host.querySelectorAll('[data-glow]').forEach(el => {
    el.classList.toggle('on', el.getAttribute('data-glow') === glowMode());
  });
}
function tickBoardGlow(root, now) { applyBoardGlow(root, now); }

function sectionSettings() {
  const on = st(E.sw).state === 'on';
  const connected = st(E.conn).state === 'on';
  const sig = st(E.signal).state;
  const glow = glowMode();
  const glowBtns = GLOW_CHOICES.map(([id, label], i) => {
    const swatch = id.charAt(0) === '#' ? `<i class="glow-swatch" style="background:${id}"></i>` : '';
    return `<button type="button" class="icon-tile${glow === id ? ' on' : ''}" data-glow="${id}" title="${esc(label)}" ${da('setGlow', id)} ${ov('glow_' + i)}>${swatch}<span class="icon-label">${esc(label)}</span></button>`;
  }).join('');
  return `<div class="section" style="margin-top:36px">
    <div class="section-h"><h2>Board</h2></div>
    <button type="button" class="toggle ${on ? 'on' : ''}" ${da('toggle', 'switch', E.sw)} ${ov('conn')}><span>Granboard Connection</span><i></i></button>
    <div class="def"><dt>Connected</dt><dd>${connected ? 'Yes' : 'No'}</dd></div>
    <div class="def"><dt>Signal Strength</dt><dd>${esc(sig && sig !== 'unknown' ? sig : '—')}</dd></div>
    <div class="play-actions"><button type="button" class="btn" ${da('press', E.release)} ${ov('release')}>Release Board</button></div>
    <div class="section-h" style="margin-top:36px"><h2>Glow</h2></div>
    <div class="icon-row glow-row">${glowBtns}</div>
    <p class="note">Auto follows the board LED ring effect, palette, colors, speed and intensity. During a game it follows the current player and hit colors (the ambient ring effect is paused). When the ring is off, a circular rainbow glow is used.</p>
  </div>`;
}

function modalHtml() {
  const p = (typeof window !== 'undefined' && window.__dartsPending) || null;
  if (!p) return '';
  return `<div class="modal-bg" ${da('no')}><div class="modal" data-stop><p>${esc(p.msg)}</p><div class="actions"><button type="button" class="btn" ${da('yes')}>Confirm</button><button type="button" class="btn quiet" ${da('no')}>Cancel</button></div></div></div>`;
}


const HUE_FX = ['color cycle', 'palette steps', 'rainbow chase', 'circular rainbow', 'rainbow sweep', 'wave', 'chase'];
const BREATHE_FX = ['breathe', 'heartbeat', 'blink', 'fire flicker', 'twinkle'];
const RAINBOW_Z = ['#ff2a6d', '#ff8a00', '#ffe600', '#2bff88', '#00d5ff', '#2f6bff', '#8a2bff', '#ff2ad0'];
const HIT_COL = { treble: '#ff4d57', bullseye: '#ff4d57', double: '#3dd68c', bull: '#3dd68c' };

function parseRgb(c) {
  if (!c) return [180, 180, 190];
  if (Array.isArray(c)) return c.slice(0, 3).map(Number);
  const s = String(c).trim();
  if (s[0] === '#') {
    const h = s.slice(1);
    const n = parseInt(h.length === 3 ? h.split('').map(x => x + x).join('') : h, 16);
    return [n >> 16 & 255, n >> 8 & 255, n & 255];
  }
  const m = s.match(/\d+/g);
  return (m || [180, 180, 190]).slice(0, 3).map(Number);
}
function toneColor(c) {
  const [r, g, b] = parseRgb(c);
  const mx = Math.max(r, g, b), mn = Math.min(r, g, b);
  if (mx < 20) return [[0, 0, 0], 0];
  let sat = (mx - mn) / mx;
  sat = sat > 0.06 ? Math.min(1, Math.max(0.6, sat * 2.2)) : sat;
  const out = [r, g, b].map(v => {
    const t = mx === mn ? 1 : (v - mn) / (mx - mn);
    return Math.round(255 * (1 - sat * (1 - t)));
  });
  return [out, Math.max(0.75, Math.sqrt(mx / 255))];
}
function glowShadow(c, bri) {
  const [v, f] = toneColor(c);
  const B = (bri == null ? 0.7 : Number(bri));
  const k = 0.35 + 0.65 * B, w = 0.55 + 0.45 * B;
  const q = a => `rgba(${v[0]},${v[1]},${v[2]},${Math.min(1, a * f * k).toFixed(2)})`;
  const p = (bl, s, a) => `0 0 ${bl * w | 0}px ${s * w | 0}px ${q(a)}`;
  return [p(6, 4, 0.7), p(16, 10, 0.45), p(36, 20, 0.28), p(70, 36, 0.14), p(110, 52, 0.07)].join(',');
}
function lightingState() {
  const a = gs();
  const state = st(E.game).state;
  const playing = state === 'playing' || state === 'finished';
  const curIdx = playing ? (a.current_player || 0) : -1;
  const pc = a.current_player_color || pcol(curIdx >= 0 ? curIdx : 0);
  const people = (a.players && a.players.length) ? a.players : helperNames().map((name, i) => ({ name, color: pcol(i) }));
  const accent2 = (people[1] && (people[1].color || pcol(1))) || pcol(1);
  const ring = st(E.ring);
  const ringOn = ring.state === 'on';
  const rgb = (ring.attributes || {}).rgb_color;
  const ringHex = (rgb && rgb.length) ? ('#' + rgb.map(c => Number(c).toString(16).padStart(2, '0')).join('')) : '#5dade2';
  const fx = String((ring.attributes || {}).effect || '').toLowerCase();
  const bri = ringOn ? (((ring.attributes || {}).brightness || 180) / 255) : 0.35;
  const hue = ringOn && HUE_FX.includes(fx);
  const breathe = ringOn && BREATHE_FX.includes(fx);
  const spd = parseInt(st(E.speed).state, 10);
  const dur = (12 - (Number.isFinite(spd) ? spd / 255 * 10 : 4)).toFixed(1);
  const lh = attr(E.last);
  const t = lh.time || '';
  const fresh = !!t && !Number.isNaN(Date.parse(t)) && (Date.now() - Date.parse(t) < 20000);
  const hitColor = HIT_COL[lh.ring] || pc;
  let zones;
  if (hue) zones = RAINBOW_Z;
  else if (ringOn && playing) zones = [pc, ringHex, pc, ringHex, accent2, ringHex, pc, accent2];
  else if (ringOn) zones = [ringHex, ringHex, accent2 || ringHex, ringHex, ringHex, pc, ringHex, pc];
  else zones = [pc, pc, accent2, accent2, pc, accent2, pc, accent2];
  return { pc, ringHex, accent2, bri, hue, breathe, dur, fresh, hitColor, zones, playing, ringOn };
}
function renderLights() {
  const L = lightingState();
  const cls = ['lights', L.playing ? 'is-play' : 'is-idle', L.hue ? 'is-hue' : '', L.breathe ? 'is-breathe' : '', L.fresh ? 'is-hit' : ''].filter(Boolean).join(' ');
  const vars = [
    `--pc:${L.pc}`, `--ring:${L.ringOn ? L.ringHex : L.pc}`, `--hit:${L.hitColor}`,
    `--accent-2:${L.accent2}`, `--bri:${L.bri.toFixed(3)}`, `--fx-dur:${L.dur}s`
  ].concat(L.zones.map((c, i) => `--z${i}:${glowShadow(c, L.bri)}`)).join(';');
  return `<div class="${cls}" style="${vars}" aria-hidden="true">
    <div class="wash wash-player"></div>
    <div class="wash wash-ring"></div>
    <div class="wash wash-accent"></div>
    <div class="wash wash-hit"></div>
    <div class="edge"><i class="t0"></i><i class="t1"></i><i class="t2"></i><i class="r0"></i><i class="r1"></i><i class="r2"></i><i class="b2"></i><i class="b1"></i><i class="b0"></i><i class="l2"></i><i class="l1"></i><i class="l0"></i></div>
  </div>`;
}
function appVars() {
  const L = lightingState();
  return `--pc:${L.pc};--ring:${L.ringOn ? L.ringHex : L.pc};--hit:${L.hitColor};--accent-2:${L.accent2};--bri:${L.bri.toFixed(3)};--fx-dur:${L.dur}s`;
}

function safeSection(fn) {
  try { return fn(); } catch (err) { try { console.error(err); } catch (e) {} return '<div class="section"><p class="note">This section could not be drawn, but the controls below still work.</p></div>'; }
}
function renderApp() {
  try {
    /* listeners are bound once on the card shadowRoot */
    const tab = tabName();
    const body = {
      game: sectionGame,
      players: sectionPlayers,
      ring: sectionRing,
      room: sectionRoom,
      sounds: sectionSounds,
      settings: sectionSettings
    };
    const sections = isVisualOnly() ? `<div data-section="game">${safeSection(sectionGame)}</div>` : TABS.map(([id]) => `<div data-section="${id}" ${tab === id ? '' : 'hidden'}>${safeSection(body[id] || (() => ''))}</div>`).join('');
    let playCls = '';
    try { playCls = lightingState().playing ? ' is-play' : ''; } catch (e) { playCls = ''; }
    let vars = '';
    try { vars = appVars(); } catch (e) { vars = ''; }
    let lights = '';
    try { lights = renderLights(); } catch (e) { lights = ''; }
    return `<div class="app${playCls}" id="darts-app" style="${vars}">${lights}<div class="stage">${chrome()}<div class="main">${sections}${modalHtml()}</div></div></div>`;
  } catch (err) {
    try { console.error(err); } catch (e) {}
    const badge = isBoardOffline() ? '<span class="offline-badge">Board Offline</span>' : '';
    return `<div class="app" id="darts-app"><div class="stage"><header class="top"><div class="brand"><span class="name">Darts</span><span class="tag">Arena</span></div><div class="status">${badge}</div></header><div class="main"><p class="note">The board view could not be drawn. Use the controls on this page to start a game, undo, or change settings.</p></div></div></div>`;
  }
}


const DEFAULT_CONFIG = {
  prefix: 'game_room_granboard_3s',
  newGameScript: 'darts_preview_new_game',
  helpers: {
    players: 'input_text.darts_players',
    colors: 'input_text.darts_colors',
    double: 'input_boolean.darts_double_out'
  },
  wled: {
    light: 'light.wled_4',
    palette: 'select.wled_color_palette_3',
    preset: 'select.wled_preset_3',
    intensity: 'number.wled_intensity_3',
    speed: 'number.wled_speed_3'
  }
};

function applyConfig(user) {
  const src = user || {};
  let wled;
  if (src.wled === null) wled = null;
  else if (Array.isArray(src.wled)) wled = src.wled;
  else wled = Object.assign({}, DEFAULT_CONFIG.wled || {}, src.wled || {});
  DARTS_CONFIG = Object.assign({}, DEFAULT_CONFIG, src, {
    helpers: Object.assign({}, DEFAULT_CONFIG.helpers, src.helpers || {}),
    wled
  });
  E = cfgEntities(DARTS_CONFIG);
}

function dartsSyncAttrs(from, to) {
  if (!from || !to || from.nodeType !== 1 || to.nodeType !== 1) return;
  const root = from.getRootNode && from.getRootNode();
  const focused = root && root.activeElement === from;
  const skipValue = focused && from.tagName === 'INPUT';
  const skipStyle = from.classList && from.classList.contains('board-side');
  for (const a of to.attributes) {
    if (a.name === 'hidden' && from.hasAttribute('data-section')) continue;
    if (skipValue && a.name === 'value') continue;
    if (skipStyle && a.name === 'style') continue;
    if (from.getAttribute(a.name) !== a.value) from.setAttribute(a.name, a.value);
  }
  for (const a of Array.from(from.attributes)) {
    if (a.name === 'hidden' && from.hasAttribute('data-section')) continue;
    if (!to.hasAttribute(a.name) && a.name !== 'style') from.removeAttribute(a.name);
  }
  if (from.tagName === 'INPUT' && !skipValue && to.value !== undefined && from.value !== to.value) {
    from.value = to.value;
  }
}

function dartsPatchNode(from, to) {
  if (!from || !to) return;
  if (from.nodeType === 3 && to.nodeType === 3) {
    if (from.nodeValue !== to.nodeValue) from.nodeValue = to.nodeValue;
    return;
  }
  if (from.nodeType !== to.nodeType || (from.tagName && from.tagName !== to.tagName)) {
    from.replaceWith(to.cloneNode(true));
    return;
  }
  if (from.nodeType !== 1) return;
  if (from.classList && from.classList.contains('lights')) {
    if (from.className !== to.className) from.className = to.className;
    const stl = to.getAttribute('style');
    if (stl) from.setAttribute('style', stl);
    return;
  }
  if (from.classList && (from.classList.contains('wash') || from.classList.contains('edge') || from.classList.contains('key-halo') || from.classList.contains('halo-wrap') || from.classList.contains('halo-glow') || from.classList.contains('halo-ring'))) {
    if (from.className !== to.className) from.className = to.className;
    return;
  }
  if (from.classList && (from.classList.contains('board-glow-bloom') || from.classList.contains('board-glow-rainbow-clip') || from.classList.contains('board-glow-prism'))) {
    return;
  }
  dartsSyncAttrs(from, to);
  const fc = from.childNodes;
  const tc = to.childNodes;
  const n = Math.min(fc.length, tc.length);
  for (let i = 0; i < n; i++) dartsPatchNode(fc[i], tc[i]);
  if (tc.length > fc.length) {
    for (let i = n; i < tc.length; i++) from.appendChild(tc[i].cloneNode(true));
  } else if (fc.length > tc.length) {
    for (let i = fc.length - 1; i >= n; i--) from.removeChild(fc[i]);
  }
}


class DartsArenaCard extends HTMLElement {
  constructor() {
    super();
    this._hass = null;
    this._config = null;
    this._rendered = false;
    this._section = 'game';
    if (!this.shadowRoot) this.attachShadow({ mode: 'open' });
  }
  setConfig(config) {
    if (!config) throw new Error('Invalid darts-arena-card config');
    this._config = config;
    applyConfig(config);
    if (this._rendered) this._update();
  }
  set hass(h) {
    this._hass = h;
    try {
      window.__dartsCard = this;
      window.__dartsHass = h;
    } catch (e) {}
    if (this._config) applyConfig(this._config);
    if (!this._rendered) {
      if (this.isConnected) this._first();
    } else {
      this._update();
    }
  }
  get hass() { return this._hass; }
  connectedCallback() {
    try { window.__dartsCard = this; if (this._hass) window.__dartsHass = this._hass; } catch (e) {}
    if (this._hass && this._config && !this._rendered) this._first();
  }
  getCardSize() { return 16; }
  _bindOnce() {
    installApi(this);
    attachDartsHost(this.shadowRoot);
  }
  _lockGlowHeight(force) {
    const app = this.shadowRoot && this.shadowRoot.getElementById('darts-app');
    if (!app) return;
    const w = Math.round(this.clientWidth || app.clientWidth || 0);
    const widthChanged = !!(force || !this._glowW || Math.abs(this._glowW - w) >= 2);
    const hNow = Math.max(app.scrollHeight || 0, this.scrollHeight || 0, this.clientHeight || 0);
    if (widthChanged) {
      this._glowW = w;
      this._glowH = Math.max(hNow, this._glowH || 0);
    } else if (hNow > (this._glowH || 0) + 8) {
      this._glowH = hNow;
    } else {
      return;
    }
    if (this._glowH > 0) app.style.setProperty('--arena-glow-h', this._glowH + 'px');
  }
  _onResize() { this._lockGlowHeight(false); }
  _first() {
    applyConfig(this._config || {});
    if (this._section) {
      try { window.__dartsSection = this._section; } catch (e) {}
    }
    this.shadowRoot.innerHTML = '<style>' + DARTS_ARENA_CSS + '</style>' + renderApp();
    this._bindOnce();
    this._rendered = true;
    this._section = tabName();
    this._glowW = 0;
    this._glowH = 0;
    this._lockGlowHeight(true);
    if (!this._resizeBound) {
      this._resizeBound = true;
      this._onResize = this._onResize.bind(this);
      window.addEventListener('resize', this._onResize, { passive: true });
    }
    this._syncBoardGlow();
  }
  _syncBoardGlow() {
    if (typeof applyBoardGlow === 'function') applyBoardGlow(this.shadowRoot);
    if (typeof boardGlowNeedsTick === 'function' && boardGlowNeedsTick()) this._startGlowTick();
    else this._stopGlowTick();
  }
  _startGlowTick() {
    if (this._glowRaf) return;
    const step = (ts) => {
      this._glowRaf = 0;
      if (!this.isConnected) return;
      if (typeof tickBoardGlow === 'function') tickBoardGlow(this.shadowRoot, ts);
      if (typeof boardGlowNeedsTick === 'function' && boardGlowNeedsTick()) {
        this._glowRaf = requestAnimationFrame(step);
      }
    };
    this._glowRaf = requestAnimationFrame(step);
  }
  _stopGlowTick() {
    if (this._glowRaf) {
      cancelAnimationFrame(this._glowRaf);
      this._glowRaf = 0;
    }
  }
  disconnectedCallback() {
    this._stopGlowTick();
    if (this._resizeBound && this._onResize) {
      window.removeEventListener('resize', this._onResize);
      this._resizeBound = false;
    }
  }
  _update() {
    applyConfig(this._config || {});
    try { window.__dartsCard = this; window.__dartsHass = this._hass; window.__dartsSection = this._section || window.__dartsSection; } catch (e) {}
    const ae = this.shadowRoot.activeElement;
    if (ae && ae.matches && ae.matches('input[type="range"], input[type="text"]')) return;
    const y = this.scrollTop;
    const tpl = document.createElement('template');
    tpl.innerHTML = renderApp();
    const nu = tpl.content.querySelector('#darts-app');
    const cur = this.shadowRoot.getElementById('darts-app');
    if (!cur || !nu) { this._rendered = false; this._first(); return; }
    const glow = cur.style.getPropertyValue('--arena-glow-h');
    dartsPatchNode(cur, nu);
    if (glow) cur.style.setProperty('--arena-glow-h', glow);
    const tab = this._section || (typeof window !== 'undefined' && window.__dartsSection) || tabName();
    cur.querySelectorAll('[data-section]').forEach(sec => {
      sec.hidden = sec.getAttribute('data-section') !== tab;
    });
    if (typeof window !== 'undefined' && window.__dartsPending) {
      if (!cur.querySelector('.modal-bg')) cur.insertAdjacentHTML('beforeend', modalHtml());
    } else {
      const m = cur.querySelector('.modal-bg');
      if (m) m.remove();
    }
    this._lockGlowHeight(false);
    this.scrollTop = y;
    this._syncBoardGlow();
  }

}

if (!customElements.get('darts-arena-card')) {
  customElements.define('darts-arena-card', DartsArenaCard);
}
window.customCards = window.customCards || [];
if (!window.customCards.some(c => c && c.type === 'darts-arena-card')) {
  window.customCards.push({
    type: 'darts-arena-card',
    name: 'Darts Arena',
    description: 'Granboard Arena dashboard card',
    preview: false
  });
}
