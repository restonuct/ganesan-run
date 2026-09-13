# 🐘 Eco-Friendly Ganesh Chaturthi Chase

<p align="center">
  <img src="title_logo.jpg" alt="Eco-Friendly Ganesh Chase Title Logo" width="100%" style="max-width: 820px; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.3);" />
</p>

[![Three.js](https://img.shields.io/badge/Three.js-r128-black?style=for-the-badge&logo=three.js)](https://threejs.org/)
[![JavaScript](https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/en-US/docs/Web/JavaScript)
[![WebGL](https://img.shields.io/badge/WebGL-2.0-990000?style=for-the-badge&logo=webgl)](https://www.khronos.org/webgl/)
[![HTML5 / CSS3](https://img.shields.io/badge/HTML5_&_CSS3-Glassmorphism-E34F26?style=for-the-badge&logo=html5)](https://developer.mozilla.org/en-US/docs/Web/CSS)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

> A high-performance 3D Endless Runner built in **Three.js** inspired by *Subway Surfers*, featuring Lord Ganesha on a sacred mission to clean up the city and protect the environment.

---

## 📖 Overview

In **Eco-Friendly Ganesh Chaturthi Chase**, the traditional endless runner narrative is turned upside down. The player controls **Lord Ganesha**, chasing a Polluter Villain who flees along the ceremonial highway, dropping hazardous waste, roadblocks, and garbage trucks. 

Ganesha's divine mission: clean up the path by collecting sacred **Modaks**, wielding mystical power-ups, surfing on the celestial **Mooshikan** hoverboard, and purifying the streets for a greener, eco-friendly Ganesh Chaturthi.

---

## ✨ Key Features

- **Custom 3D Low-Poly Models**:
  - **Lord Ganesha**: Features animated golden crown (Mukut), trunk, ceremonial visor, and dynamic stride physics.
  - **Mooshikan Steed**: Celestial purple and gold hoverboard that acts as a crash shield.
  - **Polluter Villain**: Procedural runner in the horizon who continuously scatters obstacles.
  - **3 Train/Truck Variants**: Static roadblocks, oncoming moving trucks, and **Ramp Trucks** that allow Ganesha to smoothly sprint onto roof catwalks.
  - **Custom Pickups**: 3D Modaks, Super Sneakers, Coin Magnet, Jetpack, Multiplier, and the sacred Golden Gada.

- **Power-Up Arsenal & Pacing Guarantee**:
  - **🔱 Divine Gada (Mace)**: Wield Lord Ganesha's golden mace to smash directly through garbage trucks and barricades safely with expanding golden shockwave rings and bonus Modaks!
  - **🚀 Jetpack**: Elevate high into the sky above all ground obstacles and collect linear, dense sky Modak trails.
  - **👟 Super Sneakers**: High vertical leap with 360-degree acrobatic front-flips and expanded vertical collection bounding boxes.
  - **🧲 Coin Magnet**: Generates a 3-lane horizontal magnetic aura that draws all Modaks from adjacent lanes.
  - **⭐ 2X Multiplier**: Doubles all Modak collection scores.
  - **📏 350m Minimum Distance Spacing**: Guaranteed minimum 350-meter gap between power-up spawns so items feel earned and balanced.

- **Fair Obstacle Level Design**:
  - Architectural guarantee that **never spawns 3 full-blocking trucks side-by-side**.
  - Every obstacle wave guarantees at least one viable path: an open lane, an inclined **Ramp Truck**, a leapable low barrier, or a high hurdle to slide underneath.

- **Mooshikan Workshop & In-Game Economy**:
  - **Persistent Currency**: Collect Modaks during runs to build your permanent Modak Bank, saved securely in `localStorage`.
  - **Interactive Store**: Accessible from HUD, Pause Menu, or Game Over screen to purchase Mooshikan Hoverboards (1 Board = 30 🟡, with discount bundles available).
  - **Zero-Board Feedback**: If boards hit zero, double-tap attempts trigger an 8-bit error buzzer, shaking HUD animation, and helpful toast alerts.

- **Procedural Synthesizer Audio Engine**:
  - 100% native **Web Audio API** sound synthesis: coin collection chimes, jumping whooshes, board activations, error buzzers, and deep resonant Gada smash impacts without needing external audio files.

- **AAA Glassmorphic UI & Smooth Controls**:
  - Ultra-crisp glassmorphism overlay system with responsive touch swipes for mobile and full keyboard navigation for desktop.
  - Live power-up shelves with countdown timers and dynamic CSS `@keyframes scoreBump` effects.

---

## 🎮 Controls

The game supports both desktop keyboards and mobile touch swipe controls:

| Action | Keyboard Controls | Mobile Touch Controls |
|---|---|---|
| **Move Left** | `←` or `A` | Swipe Left |
| **Move Right** | `→` or `D` | Swipe Right |
| **Jump / Leap** | `↑`, `W`, or `Space` | Swipe Up |
| **Slide / Roll / Fast Drop** | `↓` or `S` | Swipe Down |
| **Deploy Mooshikan Board** | `B` or Double-tap `Space` | Double-Tap Screen / Tap HUD Icon |
| **Open Shop (🛒)** | Click HUD / Menu `🛒` | Tap HUD `🛒` Button |
| **Pause / Resume** | `Esc` or `P` / Click `⏸️` | Tap HUD `⏸️` Button |

---

## 🛠️ Tech Stack

- **Graphics Engine**: [Three.js r128](https://threejs.org/) (WebGL rendering, PCF soft shadow mapping, procedural geometry, and GLTF preloading)
- **Programming Language**: Vanilla JavaScript (ES6+ modular architecture, zero runtime compilation or bundlers needed)
- **Audio Engine**: Native HTML5 Web Audio API (real-time frequency synthesis)
- **Styling**: Modern CSS3 (Glassmorphism, backdrop filters, CSS Grid, Flexbox, dynamic animations)
- **Persistence**: Web Storage API (`localStorage`) with fail-safe error boundaries
- **3D Asset Generation**: Python 3 + `trimesh` scripts for procedural `.glb` asset generation

---

## 🚀 How to Run Locally

Because the game loads 3D model assets (`.glb`) via `THREE.GLTFLoader`, modern browsers require the files to be served via a local HTTP server rather than `file://`.

### Option 1: Python 3 (Quickest)
Run the built-in HTTP server in the repository root:
```bash
python3 -m http.server 8088
```
Then open your browser and navigate to:
```
http://localhost:8088
```

### Option 2: Node.js / NPX
```bash
npx serve . -p 8088
```

### Option 3: VS Code Live Server
1. Install the **Live Server** extension in Visual Studio Code.
2. Right-click `index.html` and select **"Open with Live Server"**.

---

## 📂 Project Structure

```
ganesan-one/
├── index.html              # Core game markup, HUD elements & glassmorphic modals
├── style.css               # Glassmorphic UI styling, HUD cards & animations
├── main.js                 # Three.js scene, physics loop, input & economy system
├── .gitignore              # Git ignore rules for clean repository hygiene
├── LICENSE                 # Standard MIT open-source license
├── README.md               # Project documentation & guide
│
├── *.glb                   # Optimized 3D model assets:
│   ├── ganesha.glb         # Lord Ganesha character mesh
│   ├── mooshikan.glb       # Sacred hoverboard mesh
│   ├── villain.glb         # Polluter villain mesh
│   ├── truck.glb           # Static garbage truck
│   ├── truck_moving.glb    # Oncoming diesel truck
│   ├── truck_ramp.glb      # Inclined ramp truck
│   ├── shoes.glb           # Super sneakers pickup
│   ├── jetpack.glb         # Sky flight jetpack
│   ├── magnet.glb          # 3-lane coin magnet
│   ├── multiplier.glb      # 2X score star
│   ├── modak.glb           # Sacred modak currency
│   └── garbage_jar.glb     # Road obstacle jar
│
└── generate_*.py           # Python 3D asset generator scripts (trimesh)
```

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

<div align="center">
  <b>🌸 Ganpati Bappa Morya! Celebrate an Eco-Friendly Festival! 🌸</b>
</div>
