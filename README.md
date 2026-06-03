# WeGS — Ground Station Web Visualizer

Local-first pipeline that monitors satellite image folders and serves an interactive web dashboard. One command to install. Zero cloud dependencies.

```bash
curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash
```

## What it does

- 🛰️ **Monitors** SatDump output folders in real-time
- 🖼️ **Generates** thumbnails and image metadata
- 🌐 **Serves** an interactive web dashboard on localhost
- 📱 **Optionally** sends Telegram notifications
- ☁️ **Optionally** syncs to Supabase for public sharing

## Quick Start

```bash
# Install (60 seconds)
curl -fsSL https://raw.githubusercontent.com/andrettiprz/WeGS/main/install.sh | bash

# The wizard asks:
#   📡 Where are your satellite images?
#   🏷️  What's your station name?
#   🗺️  Google Maps embed URL? (optional)

# Done! Open http://localhost:5173
```

## Requirements

- **Python** 3.8+
- **Node.js** 18+
- A folder with satellite PNGs (e.g., SatDump live_output)

## Optional Features

```bash
wegs add telegram     # BotFather → token → AOS alerts on your phone
wegs add supabase     # Cloud publishing → public website
wegs add deploy       # Deploy web UI to Vercel
```

## Commands

```
wegs start            Start watchdog + web server
wegs stop             Stop all services
wegs status           Show system status
wegs reconfigure      Re-run setup wizard
wegs sync             Upload pending passes to Supabase
wegs update           Update to latest version
```

## Web Dashboard

| View | Features |
|------|----------|
| **Home** | Hero, pass gallery, system status, statistics, station info + map |
| **Passes** | Filterable table, thumbnail previews, pagination, satellite filter |
| **Detail** | All images per pass (RAW + FILLED), navigation |
| **Lightbox** | Zoom (scroll/click 0.5×-5×), drag/pan, keyboard shortcuts |

## Architecture

```
SatDump / GNU Radio
        ↓
  WeGS Watchdog (Python)
  ├─ Monitors folders
  ├─ Generates thumbnails
  ├─ Writes manifest.json
  ├─ [Telegram] notifications
  └─ [Supabase] cloud sync
        ↓
  WeGS Web (React + Vite)
  ├─ Reads manifest.json (local mode)
  ├─ Bilingual EN/ES UI
  └─ Serves on localhost:5173
```

## License

MIT — free for anyone, anywhere.
