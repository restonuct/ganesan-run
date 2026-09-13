/**
 * Eco-Friendly Ganesh Chaturthi - Subway Surfers Endless Chase
 * 100% Pure JavaScript with Three.js (No external dependencies)
 */

(function () {
  'use strict';

  // ==========================================
  // CONFIGURATION & CONSTANTS
  // ==========================================
  const LANES = [-3.0, 0, 3.0];
  const LANE_LEFT = 0;
  const LANE_CENTER = 1;
  const LANE_RIGHT = 2;

  const BASE_SPEED = 18.0;              // Smooth, easily controllable base running speed
  const MAX_SPEED = 36.0;               // Gentle top speed cap as distance increases
  let gameSpeed = BASE_SPEED;           // Dynamic progressive difficulty speed

  // Snappy, responsive Subway Surfers jump physics (NOT floaty)
  const NORMAL_JUMP_FORCE = 16.5;       // Fast initial upward burst
  const SNEAKERS_JUMP_FORCE = 28.5;     // High jump velocity clearing trucks with ease
  const GRAVITY = 52.0;                 // Fast, responsive gravity

  const VILLAIN_LEAD_DISTANCE = 58.0;   // Villain stays ~58m ahead in direct, clear view
  const JETPACK_Y = 11.0;               // Flight height in sky during Jetpack mode

  // Power-up Durations (seconds)
  const JETPACK_DURATION = 10.0;
  const SNEAKERS_DURATION = 14.0;
  const MAGNET_DURATION = 15.0;         // Magnet duration (horizontal 3-lane collector)
  const MULTIPLIER_DURATION = 18.0;
  const BOARD_DURATION = 30.0;
  const GADA_DURATION = 12.0;           // Divine Gada duration (smash through obstacles)
  const MIN_POWERUP_SPAWN_GAP = 350.0;  // Strict minimum 350m between any two spawned power-ups

  const SPAWN_DISTANCE = 115;           // Distance ahead to spawn new waves
  const DESPAWN_DISTANCE = 18;          // Distance behind camera to clean up objects

  const STATE = {
    LOADING: -1,
    MENU: 0,
    PLAYING: 1,
    DIVINE_ASCENT: 2,
    GAMEOVER: 3,
    PAUSED: 4
  };

  let gameState = STATE.LOADING;

  // Game Metrics & Scoring
  let score = 0;                        // Modaks collected in current run
  let totalDistanceRun = 0;             // Distance in meters
  let bestModakScore = 0;               // Persisted best modak score
  let bestEcoScore = 0;                 // Persisted best eco distance
  let boardsRemaining = 3;              // Player starts with 3 Mooshikan Boards
  let soundEnabled = true;

  // Active Power-Ups State
  let isJetpackActive = false;
  let isJetpackDescending = false;
  let jetpackTimer = 0;
  let jetpackSkyLane = LANE_CENTER;

  let isSneakersActive = false;
  let sneakersTimer = 0;

  let isMagnetActive = false;           // The Magnet: Horizontal 3-lane collector
  let magnetTimer = 0;

  let isMultiplierActive = false;
  let multiplierTimer = 0;

  let isBoardActive = false;
  let boardTimer = 0;

  let isGadaActive = false;             // Divine Gada: Mace weapon to smash obstacles
  let gadaTimer = 0;
  let activeGadaMesh = null;
  let lastPowerupSpawnDistance = -200.0;// Minimum 350m spacing tracker
  let cameraShakeTimer = 0;

  // Invincibility (after board shield breaks or jetpack landing)
  let isInvincible = false;
  let invincibleTimer = 0;

  // Respectful Divine Game Over State
  let divineAscentTimer = 0;
  let divineAuraMesh = null;
  let divineSphereMesh = null;

  // Player Physics & Ground/Roof Tracking
  let currentLane = LANE_CENTER;
  let targetX = LANES[LANE_CENTER];
  let playerY = 0;                      // Current elevation (0 = ground, >0 = jumping/roof/flying)
  let playerVelocityY = 0;
  let currentBaseY = 0;                 // Height of surface player is on (0 or truck.roofY)
  let isGrounded = true;
  let isJumping = false;                // Explicit jump lifecycle tracking (never float or double-jump)

  // Slide / Roll Mechanics State
  let isSliding = false;                // When true: collider height halved & character compresses
  let slideTimer = 0;
  const SLIDE_DURATION = 0.8;           // Duration of slide in seconds
  let queuedSlide = false;              // Queued slide if fast-dropped in mid-air

  // Garbage Truck Dimensions (Subway Surfers Train scale: tall & long)
  const TRUCK_ROOF_Y = 3.8;             // Tall roof (normal jump cannot reach without sneakers or ramp)
  const TRUCK_LENGTH = 24.0;            // Extended multi-segment train length
  const TRUCK_WIDTH = 2.4;

  // Animation State Blending Variables
  let playerPitchX = 0;                 // Tilting forward on jump/descent/slide
  let playerRollZ = 0;                  // Banking into turns
  let playerBobY = 0;                   // Running step bounce
  let isSneakersFlipping = false;       // 360-degree acrobatic front-flip with Super Sneakers
  let sneakersFlipAngle = 0;

  // Cinematic Camera State (for buttery smooth transitions)
  let currentSkyFactor = 0.0;           // 0.0 (ground) -> 1.0 (sky jetpack)
  let currentLookY = 1.8;
  let currentLookZ = -18.0;

  // Input Tracking
  let lastSpacePressTime = 0;
  let lastTouchTapTime = 0;

  // Active Game Entities
  const activeObstacles = [];           // Garbage trucks (static, moving, ramp), high hurdles, low barricades
  const activeCollectibles = [];         // Modaks and power-up pickups
  const activeParticles = [];            // Sparkles, explosions, jet flames, divine aura
  const activeOverbridges = [];          // Overhead ceremonial arches & overbridges
  const activeScenery = [];             // Parallax peripheral scenery (trees, rocks, banners)

  // Dedicated THREE.Box3 Reusable Collision Bounding Boxes (Zero GC Allocations)
  const playerColliderBox = new THREE.Box3();
  const obstacleColliderBox = new THREE.Box3();
  const truckBodyBox = new THREE.Box3();

  let spawnTimer = 0;
  const SPAWN_INTERVAL = 1.05;          // Frequency of dynamic waves spawned by villain
  let overbridgeTimer = 0;
  const OVERBRIDGE_INTERVAL = 12.0;     // Frequency of overhead bridges
  let scenerySpawnTimer = 0;
  const SCENERY_SPAWN_INTERVAL = 0.42;  // High-cadence parallax scenery spawning

  // ==========================================
  // BROWSER LOCALSTORAGE PERSISTENCE MANAGER
  // ==========================================
  const StorageManager = {
    KEYS: {
      BEST_MODAKS: 'ganesh_run_best_modaks',
      BEST_DISTANCE: 'ganesh_run_best_distance',
      LEGACY_HIGHSCORE: 'ganesh_run_highscore',
      TOTAL_MODAKS: 'ganesh_run_total_modaks',
      MOOSHIKAN_BOARDS: 'ganesh_run_mooshikan_boards',
      GAMES_PLAYED: 'ganesh_run_games_played'
    },

    isAvailable() {
      try {
        const probe = '__storage_probe__';
        window.localStorage.setItem(probe, probe);
        window.localStorage.removeItem(probe);
        return true;
      } catch (e) {
        return false;
      }
    },

    getBestModakScore() {
      if (!this.isAvailable()) return 0;
      try {
        const val = window.localStorage.getItem(this.KEYS.BEST_MODAKS);
        return val ? parseInt(val, 10) || 0 : 0;
      } catch (e) {
        return 0;
      }
    },

    saveBestModakScore(val) {
      if (!this.isAvailable()) return;
      try {
        const num = Math.max(0, parseInt(val, 10) || 0);
        window.localStorage.setItem(this.KEYS.BEST_MODAKS, num.toString());
      } catch (e) {
        console.warn('StorageManager: Unable to persist best modaks', e);
      }
    },

    getBestEcoScore() {
      if (!this.isAvailable()) return 0;
      try {
        const val = window.localStorage.getItem(this.KEYS.BEST_DISTANCE) ||
                    window.localStorage.getItem(this.KEYS.LEGACY_HIGHSCORE);
        return val ? parseInt(val, 10) || 0 : 0;
      } catch (e) {
        return 0;
      }
    },

    saveBestEcoScore(val) {
      if (!this.isAvailable()) return;
      try {
        const num = Math.max(0, parseInt(val, 10) || 0).toString();
        window.localStorage.setItem(this.KEYS.BEST_DISTANCE, num);
        window.localStorage.setItem(this.KEYS.LEGACY_HIGHSCORE, num);
      } catch (e) {
        console.warn('StorageManager: Unable to persist best distance', e);
      }
    },

    getTotalModaks() {
      if (!this.isAvailable()) return 0;
      try {
        const val = window.localStorage.getItem(this.KEYS.TOTAL_MODAKS);
        return val ? parseInt(val, 10) || 0 : 0;
      } catch (e) {
        return 0;
      }
    },

    saveTotalModaks(val) {
      if (!this.isAvailable()) return;
      try {
        const num = Math.max(0, parseInt(val, 10) || 0);
        window.localStorage.setItem(this.KEYS.TOTAL_MODAKS, num.toString());
      } catch (e) {
        console.warn('StorageManager: Unable to persist total modaks', e);
      }
    },

    addModaks(count) {
      const current = this.getTotalModaks();
      const updated = current + Math.max(0, parseInt(count, 10) || 0);
      this.saveTotalModaks(updated);
      return updated;
    },

    getMooshikanBoards(defaultCount = 3) {
      if (!this.isAvailable()) return defaultCount;
      try {
        const val = window.localStorage.getItem(this.KEYS.MOOSHIKAN_BOARDS);
        if (val === null || val === undefined) return defaultCount;
        const parsed = parseInt(val, 10);
        return isNaN(parsed) ? defaultCount : Math.max(0, parsed);
      } catch (e) {
        return defaultCount;
      }
    },

    saveMooshikanBoards(count) {
      if (!this.isAvailable()) return;
      try {
        const num = Math.max(0, parseInt(count, 10) || 0);
        window.localStorage.setItem(this.KEYS.MOOSHIKAN_BOARDS, num.toString());
      } catch (e) {
        console.warn('StorageManager: Unable to persist mooshikan boards', e);
      }
    },

    getGamesPlayed() {
      if (!this.isAvailable()) return 0;
      try {
        const val = window.localStorage.getItem(this.KEYS.GAMES_PLAYED);
        return val ? parseInt(val, 10) || 0 : 0;
      } catch (e) {
        return 0;
      }
    },

    incrementGamesPlayed() {
      const current = this.getGamesPlayed();
      const updated = current + 1;
      if (this.isAvailable()) {
        try {
          window.localStorage.setItem(this.KEYS.GAMES_PLAYED, updated.toString());
        } catch (e) {
          console.warn('StorageManager: Unable to persist games played', e);
        }
      }
      return updated;
    },

    getAllStats() {
      return {
        bestModakScore: this.getBestModakScore(),
        bestEcoScore: this.getBestEcoScore(),
        totalModaksCollected: this.getTotalModaks(),
        mooshikanBoards: this.getMooshikanBoards(3),
        gamesPlayed: this.getGamesPlayed()
      };
    },

    recordGameOver(runModaks, runDistance, remainingBoards) {
      const modaks = Math.max(0, parseInt(runModaks, 10) || 0);
      const distance = Math.max(0, parseInt(runDistance, 10) || 0);
      const currentBestModaks = this.getBestModakScore();
      const currentBestEco = this.getBestEcoScore();

      let newBestModaks = false;
      let newBestEco = false;

      if (modaks > currentBestModaks) {
        this.saveBestModakScore(modaks);
        newBestModaks = true;
      }
      if (distance > currentBestEco) {
        this.saveBestEcoScore(distance);
        newBestEco = true;
      }

      // Modaks are banked in real-time upon collection; query current total
      const totalModaks = this.getTotalModaks();
      const gamesPlayed = this.incrementGamesPlayed();
      if (remainingBoards !== undefined && remainingBoards !== null) {
        this.saveMooshikanBoards(remainingBoards);
      }

      return {
        newBestModaks,
        newBestEco,
        bestModakScore: Math.max(modaks, currentBestModaks),
        bestEcoScore: Math.max(distance, currentBestEco),
        totalModaksCollected: totalModaks,
        gamesPlayed,
        mooshikanBoards: this.getMooshikanBoards(3)
      };
    },

    resetAll() {
      if (!this.isAvailable()) return;
      try {
        window.localStorage.removeItem(this.KEYS.BEST_MODAKS);
        window.localStorage.removeItem(this.KEYS.BEST_DISTANCE);
        window.localStorage.removeItem(this.KEYS.LEGACY_HIGHSCORE);
        window.localStorage.removeItem(this.KEYS.TOTAL_MODAKS);
        window.localStorage.removeItem(this.KEYS.MOOSHIKAN_BOARDS);
        window.localStorage.removeItem(this.KEYS.GAMES_PLAYED);
        this.saveMooshikanBoards(3);
      } catch (e) {
        console.warn('StorageManager: Unable to reset progress', e);
      }
    }
  };

  // Expose StorageManager globally for developer console and debugging
  window.StorageManager = StorageManager;

  // Initialize game metrics from persistent storage
  bestModakScore = StorageManager.getBestModakScore();
  bestEcoScore = StorageManager.getBestEcoScore();
  boardsRemaining = StorageManager.getMooshikanBoards(3);

  // ==========================================
  // AUDIO SYNTHESIZER (Web Audio API)
  // ==========================================
  let audioCtx = null;

  function initAudio() {
    if (!audioCtx) {
      const AudioCtxClass = window.AudioContext || window.webkitAudioContext;
      if (AudioCtxClass) audioCtx = new AudioCtxClass();
    }
    if (audioCtx && audioCtx.state === 'suspended') {
      audioCtx.resume();
    }
  }

  function playTone(freq, type = 'sine', duration = 0.15, gainVal = 0.12) {
    if (!soundEnabled || !audioCtx) return;
    try {
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = type;
      osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
      gain.gain.setValueAtTime(gainVal, audioCtx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.0001, audioCtx.currentTime + duration);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(audioCtx.currentTime + duration);
    } catch (e) {}
  }

  function playModakSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      const freq = isMultiplierActive ? 988 : 880;
      osc.frequency.setValueAtTime(freq, now);
      osc.frequency.exponentialRampToValueAtTime(freq * 1.5, now + 0.12);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.12);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + 0.12);
    } catch (e) {}
  }

  function playJumpSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      if (isSneakersActive) {
        osc.frequency.setValueAtTime(260, now);
        osc.frequency.exponentialRampToValueAtTime(780, now + 0.22);
        gain.gain.setValueAtTime(0.18, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.22);
      } else {
        osc.frequency.setValueAtTime(220, now);
        osc.frequency.exponentialRampToValueAtTime(520, now + 0.15);
        gain.gain.setValueAtTime(0.12, now);
        gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
      }
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + (isSneakersActive ? 0.22 : 0.15));
    } catch (e) {}
  }

  function playLandingSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(320, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.18);
      gain.gain.setValueAtTime(0.12, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.18);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + 0.18);
    } catch (e) {}
  }

  function playSlideSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(380, now);
      osc.frequency.exponentialRampToValueAtTime(110, now + 0.28);
      gain.gain.setValueAtTime(0.14, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + 0.28);
    } catch (e) {}
  }

  function playPowerupPickupSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const notes = [523.25, 659.25, 783.99, 1046.5];
      notes.forEach((freq, idx) => {
        setTimeout(() => playTone(freq, 'sine', 0.18, 0.15), idx * 55);
      });
    } catch (e) {}
  }

  function playBoardDeploySound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(180, now);
      osc.frequency.exponentialRampToValueAtTime(650, now + 0.25);
      gain.gain.setValueAtTime(0.14, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + 0.25);
    } catch (e) {}
  }

  function playShieldBreakSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const bufferSize = audioCtx.sampleRate * 0.25;
      const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;

      const noise = audioCtx.createBufferSource();
      noise.buffer = buffer;
      const gain = audioCtx.createGain();
      gain.gain.setValueAtTime(0.25, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.25);
      noise.connect(gain);
      gain.connect(audioCtx.destination);
      noise.start();

      playTone(1200, 'sine', 0.2, 0.18);
    } catch (e) {}
  }

  function playSacredTempleBell() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const harmonics = [
        { freq: 432, gain: 0.25, dur: 2.5 },
        { freq: 864, gain: 0.15, dur: 2.0 },
        { freq: 1296, gain: 0.09, dur: 1.6 },
        { freq: 1728, gain: 0.05, dur: 1.2 }
      ];

      harmonics.forEach(h => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'sine';
        osc.frequency.setValueAtTime(h.freq, now);
        gain.gain.setValueAtTime(h.gain, now);
        gain.gain.exponentialRampToValueAtTime(0.0001, now + h.dur);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start();
        osc.stop(now + h.dur);
      });
    } catch (e) {}
  }

  function playPurchaseSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      // Cheerful upward arpeggio: C5 -> E5 -> G5 -> C6
      const notes = [523.25, 659.25, 783.99, 1046.50];
      notes.forEach((freq, idx) => {
        const osc = audioCtx.createOscillator();
        const gain = audioCtx.createGain();
        osc.type = 'triangle';
        const start = now + idx * 0.055;
        osc.frequency.setValueAtTime(freq, start);
        gain.gain.setValueAtTime(0.14, start);
        gain.gain.exponentialRampToValueAtTime(0.0001, start + 0.2);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(start);
        osc.stop(start + 0.2);
      });
    } catch (e) {}
  }

  function playErrorBuzzer() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(140, now);
      osc.frequency.linearRampToValueAtTime(90, now + 0.22);
      gain.gain.setValueAtTime(0.15, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + 0.22);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start(now);
      osc.stop(now + 0.22);
    } catch (e) {}
  }

  function playGadaSmashSound() {
    if (!soundEnabled || !audioCtx) return;
    try {
      const now = audioCtx.currentTime;
      // 1. Heavy resonant impact thud
      const osc = audioCtx.createOscillator();
      const gain = audioCtx.createGain();
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(110, now);
      osc.frequency.exponentialRampToValueAtTime(25, now + 0.28);
      gain.gain.setValueAtTime(0.35, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.28);
      osc.connect(gain);
      gain.connect(audioCtx.destination);
      osc.start();
      osc.stop(now + 0.28);

      // 2. Divine golden chime shatter
      const chime = audioCtx.createOscillator();
      const chimeGain = audioCtx.createGain();
      chime.type = 'sine';
      chime.frequency.setValueAtTime(880, now);
      chime.frequency.exponentialRampToValueAtTime(1760, now + 0.35);
      chimeGain.gain.setValueAtTime(0.2, now);
      chimeGain.gain.exponentialRampToValueAtTime(0.001, now + 0.35);
      chime.connect(chimeGain);
      chimeGain.connect(audioCtx.destination);
      chime.start();
      chime.stop(now + 0.35);
    } catch (e) {}
  }

  // ==========================================
  // SCENE, CAMERA & LIGHTING SETUP
  // ==========================================
  const container = document.getElementById('game-container');
  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0xd7ebfb);
  scene.fog = new THREE.FogExp2(0xd7ebfb, 0.007);

  const camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 400);
  camera.position.set(0, 5.0, 10.0);

  const canvas = document.getElementById('game-canvas');
  const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    antialias: true,
    alpha: false,
    powerPreference: 'high-performance'
  });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // Add camera to scene to support child HUD objects
  scene.add(camera);

  // ==========================================
  // IN-CANVAS DYNAMIC 2D TEXT OVERLAY SPRITE
  // (Pure Canvas text rendered directly into WebGL)
  // ==========================================
  const overlayCanvas = document.createElement('canvas');
  overlayCanvas.width = 1024;
  overlayCanvas.height = 512;
  const overlayCtx = overlayCanvas.getContext('2d');
  const overlayTexture = new THREE.CanvasTexture(overlayCanvas);
  overlayTexture.minFilter = THREE.LinearFilter;
  overlayTexture.magFilter = THREE.LinearFilter;

  const overlayMat = new THREE.SpriteMaterial({
    map: overlayTexture,
    transparent: true,
    depthTest: false,
    depthWrite: false
  });
  const overlaySprite = new THREE.Sprite(overlayMat);
  overlaySprite.position.set(0, 0, -4.0);
  camera.add(overlaySprite);

  function updateOverlaySpriteScale() {
    if (!overlaySprite) return;
    const dist = 4.0;
    const vHeight = 2.0 * dist * Math.tan(THREE.MathUtils.degToRad(camera.fov / 2));
    const vWidth = vHeight * camera.aspect;
    const maxW = vWidth * 0.92;
    const maxH = vHeight * 0.65;
    let targetW = maxW;
    let targetH = targetW / 2.0;
    if (targetH > maxH) {
      targetH = maxH;
      targetW = targetH * 2.0;
    }
    overlaySprite.scale.set(targetW, targetH, 1.0);
  }
  updateOverlaySpriteScale();

  function drawRoundedRect(ctx, x, y, width, height, radius) {
    ctx.beginPath();
    ctx.moveTo(x + radius, y);
    ctx.lineTo(x + width - radius, y);
    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
    ctx.lineTo(x + width, y + height - radius);
    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
    ctx.lineTo(x + radius, y + height);
    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
    ctx.lineTo(x, y + radius);
    ctx.quadraticCurveTo(x, y, x + radius, y);
    ctx.closePath();
  }

  function renderCanvasOverlay(time) {
    if (gameState === STATE.PLAYING || gameState === STATE.PAUSED || gameState === STATE.GAMEOVER) {
      overlaySprite.visible = false;
      return;
    }

    overlaySprite.visible = true;
    overlayCtx.clearRect(0, 0, 1024, 512);

    const pulse = 0.65 + 0.35 * Math.sin(time * 5.0);

    overlayCtx.save();
    overlayCtx.textAlign = 'center';
    overlayCtx.textBaseline = 'middle';

    if (gameState === STATE.LOADING) {
      // Background card
      overlayCtx.fillStyle = 'rgba(15, 23, 42, 0.90)';
      overlayCtx.strokeStyle = 'rgba(255, 255, 255, 0.24)';
      overlayCtx.lineWidth = 3;
      drawRoundedRect(overlayCtx, 150, 120, 724, 272, 28);
      overlayCtx.fill();
      overlayCtx.stroke();

      // Title
      overlayCtx.font = '900 44px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#fbbf24';
      overlayCtx.shadowColor = 'rgba(245, 158, 11, 0.85)';
      overlayCtx.shadowBlur = 24;
      overlayCtx.fillText('Loading Assets...', 512, 205);

      // Subtitle
      overlayCtx.font = '600 20px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#38bdf8';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText(`Importing Procedural 3D GLB Models • ${loadingProgress}%`, 512, 265);

      // Loading Progress Bar
      const barW = 420;
      const barH = 14;
      const barX = 512 - barW / 2;
      const barY = 308;
      overlayCtx.fillStyle = 'rgba(30, 41, 59, 0.85)';
      drawRoundedRect(overlayCtx, barX, barY, barW, barH, 7);
      overlayCtx.fill();

      const fillW = Math.max(14, (barW * loadingProgress) / 100);
      overlayCtx.fillStyle = '#fbbf24';
      drawRoundedRect(overlayCtx, barX, barY, fillW, barH, 7);
      overlayCtx.fill();

      overlayCtx.restore();
      overlayTexture.needsUpdate = true;
      return;
    }

    if (gameState === STATE.MENU) {
      // Background card
      overlayCtx.fillStyle = 'rgba(15, 23, 42, 0.82)';
      overlayCtx.strokeStyle = 'rgba(255, 255, 255, 0.22)';
      overlayCtx.lineWidth = 3;
      drawRoundedRect(overlayCtx, 54, 30, 916, 452, 28);
      overlayCtx.fill();
      overlayCtx.stroke();

      // Title
      overlayCtx.font = '900 44px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#fbbf24';
      overlayCtx.shadowColor = 'rgba(245, 158, 11, 0.85)';
      overlayCtx.shadowBlur = 24;
      overlayCtx.fillText('GANESH CHATURTHI CHASE', 512, 115);

      // Subtitle
      overlayCtx.font = '700 20px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#34d399';
      overlayCtx.shadowColor = 'rgba(16, 185, 129, 0.6)';
      overlayCtx.shadowBlur = 10;
      overlayCtx.fillText('Eco-Friendly Endless Runner • Chase the Polluter', 512, 170);

      // Divider
      overlayCtx.strokeStyle = 'rgba(255, 255, 255, 0.14)';
      overlayCtx.lineWidth = 1.5;
      overlayCtx.beginPath();
      overlayCtx.moveTo(220, 210);
      overlayCtx.lineTo(804, 210);
      overlayCtx.stroke();

      // High scores
      overlayCtx.font = '600 18px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#94a3b8';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText(`Best Modaks: ${bestModakScore}   •   Best Eco Distance: ${bestEcoScore} m`, 512, 245);

      // Pulsating Start Text
      overlayCtx.font = '900 42px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = `rgba(255, 255, 255, ${pulse.toFixed(2)})`;
      overlayCtx.shadowColor = `rgba(56, 189, 248, ${pulse.toFixed(2)})`;
      overlayCtx.shadowBlur = 32;
      overlayCtx.fillText('Press Space or Tap to Start', 512, 325);

      // Controls guidance
      overlayCtx.font = '500 16px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = 'rgba(203, 213, 225, 0.9)';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText('Swipe or Arrow Keys: Move • Space / Up: Jump • Down: Slide • Double Tap: Shield', 512, 400);

    } else if (gameState === STATE.GAMEOVER) {
      // Background card
      overlayCtx.fillStyle = 'rgba(15, 23, 42, 0.88)';
      overlayCtx.strokeStyle = 'rgba(245, 158, 11, 0.4)';
      overlayCtx.lineWidth = 3;
      drawRoundedRect(overlayCtx, 54, 30, 916, 452, 28);
      overlayCtx.fill();
      overlayCtx.stroke();

      // Title
      overlayCtx.font = '900 44px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#f59e0b';
      overlayCtx.shadowColor = 'rgba(251, 191, 36, 0.9)';
      overlayCtx.shadowBlur = 24;
      overlayCtx.fillText('DIVINE BLESSING ASCENT', 512, 115);

      overlayCtx.font = '600 18px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#94a3b8';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText('Lord Ganesha blessed the sacred grounds and ascended peacefully.', 512, 165);

      // Divider
      overlayCtx.strokeStyle = 'rgba(255, 255, 255, 0.14)';
      overlayCtx.lineWidth = 1.5;
      overlayCtx.beginPath();
      overlayCtx.moveTo(220, 200);
      overlayCtx.lineTo(804, 200);
      overlayCtx.stroke();

      // Current Run Stats
      overlayCtx.font = '800 30px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#fbbf24';
      overlayCtx.shadowColor = 'rgba(245, 158, 11, 0.5)';
      overlayCtx.shadowBlur = 10;
      overlayCtx.fillText(`Modaks: ${score}     Eco Distance: ${Math.round(totalDistanceRun)} m`, 512, 240);

      // Records
      overlayCtx.font = '700 18px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = '#34d399';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText(`Best Modaks: ${bestModakScore}   •   Best Distance: ${bestEcoScore} m`, 512, 280);

      // Pulsating CTA
      overlayCtx.font = '900 40px Outfit, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = `rgba(255, 255, 255, ${pulse.toFixed(2)})`;
      overlayCtx.shadowColor = `rgba(56, 189, 248, ${pulse.toFixed(2)})`;
      overlayCtx.shadowBlur = 30;
      overlayCtx.fillText('Press Space or Tap to Chase Again', 512, 350);

      overlayCtx.font = '500 16px Inter, -apple-system, BlinkMacSystemFont, sans-serif';
      overlayCtx.fillStyle = 'rgba(203, 213, 225, 0.85)';
      overlayCtx.shadowBlur = 0;
      overlayCtx.fillText('Clean the environment and chase the polluter villain!', 512, 415);
    }

    overlayCtx.restore();
    overlayTexture.needsUpdate = true;
  }

  // ==========================================
  // PROFESSIONAL LIGHTING & DYNAMIC SHADOWS
  // ==========================================
  // HemisphereLight for ambient illumination: sky color white, ground color soft blue
  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x38bdf8, 0.85);
  hemiLight.position.set(0, 50, 0);
  scene.add(hemiLight);

  // DirectionalLight acting as the sun with dynamic shadow casting
  const dirLight = new THREE.DirectionalLight(0xfffaf0, 1.35);
  dirLight.position.set(24, 48, 26);
  dirLight.castShadow = true;
  dirLight.shadow.mapSize.width = 2048;
  dirLight.shadow.mapSize.height = 2048;
  dirLight.shadow.camera.near = 0.5;
  dirLight.shadow.camera.far = 140;
  dirLight.shadow.camera.left = -24;
  dirLight.shadow.camera.right = 24;
  dirLight.shadow.camera.top = 24;
  dirLight.shadow.camera.bottom = -24;
  dirLight.shadow.bias = -0.0003;
  scene.add(dirLight);

  // Subtle complementary fill light for lustrous metallic reflections
  const fillLight = new THREE.DirectionalLight(0xcce7ff, 0.4);
  fillLight.position.set(-20, 25, -25);
  scene.add(fillLight);

  // ==========================================
  // GLOBAL ASSET MANAGEMENT & GLTF PRELOADER
  // ==========================================
  const assets = {
    modak: null,
    truck: null,
    truck_ramp: null,
    villain: null,
    mooshikan: null,
    ganesha: null,
    garbage_jar: null
  };

  let assetsLoaded = false;
  let loadingProgress = 0;

  const loadingManager = new THREE.LoadingManager(
    // onLoad: Triggered once all 7 GLB assets are fully loaded and parsed
    () => {
      assetsLoaded = true;
      console.log('✓ All 7 procedural 3D GLB assets loaded successfully:', Object.keys(assets));
      if (gameState === STATE.LOADING) {
        gameState = STATE.MENU;
      }
    },
    // onProgress: Track percentage of loaded files
    (url, itemsLoaded, itemsTotal) => {
      loadingProgress = Math.round((itemsLoaded / itemsTotal) * 100);
    },
    // onError
    (url) => {
      console.warn('Could not load asset from:', url);
    }
  );

  const gltfLoader = new THREE.GLTFLoader(loadingManager);

  // 1. Modak (Collectibles)
  gltfLoader.load('modak.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        if (child.material) {
          child.material.metalness = Math.max(child.material.metalness || 0, 0.85);
          child.material.roughness = Math.min(child.material.roughness || 1, 0.22);
        }
      }
    });
    const container = new THREE.Group();
    root.scale.set(0.95, 0.95, 0.95);
    root.position.set(0, 0.1, 0);
    container.add(root);
    assets.modak = container;
  });

  // 2a. Standard Garbage Truck (Solid Blockage Obstacle)
  gltfLoader.load('truck.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    assets.truck = root;
  });

  // 2b. Ramp Garbage Truck (Climbable Front-Ramp Obstacle)
  gltfLoader.load('truck_ramp.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    assets.truck_ramp = root;
  });

  // 2c. Moving Garbage Truck (Container Body with Side Chevrons)
  gltfLoader.load('truck_moving.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    assets.truck_moving = root;
  });

  // 3. Polluter Villain (Target Ahead)
  gltfLoader.load('villain.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
      }
    });
    assets.villain = root;
    if (typeof attachVillainModel === 'function') {
      attachVillainModel();
    }
  });

  // 4. Mooshikan Hoverboard (Shield Power-Up)
  gltfLoader.load('mooshikan.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });
    assets.mooshikan = root;
  });

  // 5. Lord Ganesha (Playable Runner Character)
  gltfLoader.load('ganesha.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        if (child.material) {
          if (child.material.name === 'DivineGold') {
            child.material.metalness = Math.max(child.material.metalness || 0, 0.88);
            child.material.roughness = Math.min(child.material.roughness || 1, 0.2);
          }
        }
      }
    });
    // Blender front (+Z) to Three.js runner forward (-Z)
    root.rotation.y = Math.PI;
    assets.ganesha = root;
    if (typeof attachPlayerModel === 'function') {
      attachPlayerModel();
    }
  });

  // 6. Toxic Garbage Jar / Barrel (Roadblock Hazard)
  gltfLoader.load('garbage_jar.glb', (gltf) => {
    const root = gltf.scene;
    root.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
        if (child.material) {
          if (child.material.name === 'NeonToxicGoo') {
            child.material.emissive = new THREE.Color(0x15f838);
            child.material.emissiveIntensity = 0.85;
          } else if (child.material.name === 'RustyMetal' || child.material.name === 'RustOxide') {
            child.material.roughness = 0.85;
            child.material.metalness = 0.35;
          }
        }
      }
    });
    assets.garbage_jar = root;
  });

  // ==========================================
  // PROCEDURAL SNOWY TRACK & ENVIRONMENT
  // ==========================================
  const TRACK_SEGMENT_LENGTH = 50;
  const TRACK_SEGMENT_COUNT = 6;
  const trackSegments = [];

  function createTree() {
    const group = new THREE.Group();
    const trunk = new THREE.Mesh(
      new THREE.CylinderGeometry(0.22, 0.32, 1.4, 7),
      new THREE.MeshStandardMaterial({ color: 0x5c4033, roughness: 0.9 })
    );
    trunk.position.y = 0.7;
    trunk.castShadow = true;
    group.add(trunk);

    const foliageMat = new THREE.MeshStandardMaterial({ color: 0x1e3a2b, roughness: 0.8 });
    const snowTopMat = new THREE.MeshStandardMaterial({ color: 0xf0fdf4, roughness: 0.6 });

    const c1 = new THREE.Mesh(new THREE.ConeGeometry(1.6, 2.2, 7), foliageMat);
    c1.position.y = 2.1;
    c1.castShadow = true;
    group.add(c1);

    const c2 = new THREE.Mesh(new THREE.ConeGeometry(1.2, 1.8, 7), foliageMat);
    c2.position.y = 3.2;
    c2.castShadow = true;
    group.add(c2);

    const snowCap = new THREE.Mesh(new THREE.ConeGeometry(0.7, 1.0, 7), snowTopMat);
    snowCap.position.y = 4.1;
    group.add(snowCap);

    return group;
  }

  // Peripheral Decorative Scenery Models (Low-poly pine trees, rocks, eco-banners)
  function createSceneryRock() {
    const group = new THREE.Group();
    const rockGeo = new THREE.DodecahedronGeometry(1.2, 0);
    const rockMat = new THREE.MeshStandardMaterial({
      color: 0x64748b,
      roughness: 0.9,
      flatShading: true
    });
    const rock = new THREE.Mesh(rockGeo, rockMat);
    rock.position.y = 0.85;
    rock.scale.set(1.0 + Math.random() * 0.4, 0.7 + Math.random() * 0.35, 1.0 + Math.random() * 0.4);
    rock.rotation.set(Math.random() * Math.PI, Math.random() * Math.PI, 0);
    rock.castShadow = true;
    rock.receiveShadow = true;
    group.add(rock);

    // Snow patch cap
    const snowGeo = new THREE.ConeGeometry(0.9, 0.35, 6);
    const snowMat = new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.6 });
    const snow = new THREE.Mesh(snowGeo, snowMat);
    snow.position.y = rock.position.y + 0.65;
    group.add(snow);

    return group;
  }

  function createSceneryEcoBanner() {
    const group = new THREE.Group();

    // Wooden / Copper lamppost
    const poleGeo = new THREE.CylinderGeometry(0.12, 0.16, 4.2, 8);
    const poleMat = new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.7 });
    const pole = new THREE.Mesh(poleGeo, poleMat);
    pole.position.y = 2.1;
    pole.castShadow = true;
    group.add(pole);

    // Crossbar
    const armGeo = new THREE.CylinderGeometry(0.08, 0.08, 1.4, 8);
    const arm = new THREE.Mesh(armGeo, poleMat);
    arm.rotation.z = Math.PI / 2;
    arm.position.set(0.6, 3.8, 0);
    group.add(arm);

    // Festive Eco-friendly banner (Emerald green with gold border)
    const bannerGeo = new THREE.PlaneGeometry(1.0, 1.8);
    const bannerMat = new THREE.MeshStandardMaterial({
      color: 0x059669,
      emissive: 0x047857,
      emissiveIntensity: 0.2,
      roughness: 0.6,
      side: THREE.DoubleSide
    });
    const banner = new THREE.Mesh(bannerGeo, bannerMat);
    banner.position.set(0.6, 2.7, 0);
    banner.castShadow = true;
    group.add(banner);

    // Golden hanging lantern
    const lanternGeo = new THREE.OctahedronGeometry(0.28, 0);
    const lanternMat = new THREE.MeshStandardMaterial({
      color: 0xfbbf24,
      emissive: 0xf59e0b,
      emissiveIntensity: 0.85,
      roughness: 0.3
    });
    const lantern = new THREE.Mesh(lanternGeo, lanternMat);
    lantern.position.set(1.15, 3.4, 0);
    group.add(lantern);

    return group;
  }

  function spawnPeripheralScenery(spawnZ) {
    const sides = [-1, 1];
    for (let side of sides) {
      if (Math.random() < 0.72) {
        const roll = Math.random();
        let mesh;
        if (roll < 0.45) {
          mesh = createTree();
          mesh.scale.setScalar(0.75 + Math.random() * 0.45);
        } else if (roll < 0.78) {
          mesh = createSceneryRock();
          mesh.scale.setScalar(0.8 + Math.random() * 0.5);
        } else {
          mesh = createSceneryEcoBanner();
          mesh.scale.setScalar(0.9 + Math.random() * 0.25);
          if (side > 0) mesh.rotation.y = Math.PI; // Face inward
        }

        const posX = side * (6.0 + Math.random() * 4.5);
        mesh.position.set(posX, 0, spawnZ + (Math.random() - 0.5) * 5.0);
        scene.add(mesh);
        activeScenery.push({ mesh: mesh });
      }
    }
  }

  function createTrackSegment(zPos) {
    const group = new THREE.Group();
    group.position.z = zPos;

    const road = new THREE.Mesh(
      new THREE.PlaneGeometry(10.5, TRACK_SEGMENT_LENGTH),
      new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.85 })
    );
    road.rotation.x = -Math.PI / 2;
    road.receiveShadow = true;
    group.add(road);

    for (let lx of [-1.5, 1.5]) {
      const line = new THREE.Mesh(
        new THREE.PlaneGeometry(0.12, TRACK_SEGMENT_LENGTH),
        new THREE.MeshBasicMaterial({ color: 0xcbd5e1 })
      );
      line.rotation.x = -Math.PI / 2;
      line.position.set(lx, 0.01, 0);
      group.add(line);
    }

    for (let side of [-1, 1]) {
      const bank = new THREE.Mesh(
        new THREE.BoxGeometry(16, 0.55, TRACK_SEGMENT_LENGTH),
        new THREE.MeshStandardMaterial({ color: 0xf1f5f9, roughness: 0.9 })
      );
      bank.position.set(side * 13.5, 0.25, 0);
      bank.receiveShadow = true;
      group.add(bank);

      for (let t = -TRACK_SEGMENT_LENGTH / 2 + 5; t < TRACK_SEGMENT_LENGTH / 2; t += 12) {
        const tree = createTree();
        tree.position.set(side * (7.5 + Math.random() * 5), 0.5, t + (Math.random() - 0.5) * 4);
        tree.scale.setScalar(0.75 + Math.random() * 0.4);
        group.add(tree);
      }
    }

    scene.add(group);
    return group;
  }

  for (let i = 0; i < TRACK_SEGMENT_COUNT; i++) {
    trackSegments.push(createTrackSegment(-i * TRACK_SEGMENT_LENGTH + TRACK_SEGMENT_LENGTH / 2));
  }

  const SNOWFLAKE_COUNT = 350;
  const snowGeo = new THREE.BufferGeometry();
  const snowPositions = new Float32Array(SNOWFLAKE_COUNT * 3);
  const snowVelocities = new Float32Array(SNOWFLAKE_COUNT);

  for (let i = 0; i < SNOWFLAKE_COUNT; i++) {
    snowPositions[i * 3 + 0] = (Math.random() - 0.5) * 55;
    snowPositions[i * 3 + 1] = Math.random() * 28;
    snowPositions[i * 3 + 2] = (Math.random() - 0.5) * 120;
    snowVelocities[i] = 1.8 + Math.random() * 2.5;
  }

  snowGeo.setAttribute('position', new THREE.BufferAttribute(snowPositions, 3));
  const snowParticles = new THREE.Points(
    snowGeo,
    new THREE.PointsMaterial({ color: 0xffffff, size: 0.24, transparent: true, opacity: 0.85 })
  );
  scene.add(snowParticles);

  function updateSnow(delta) {
    const pos = snowGeo.attributes.position.array;
    for (let i = 0; i < SNOWFLAKE_COUNT; i++) {
      pos[i * 3 + 1] -= snowVelocities[i] * delta;
      if (pos[i * 3 + 1] < 0) pos[i * 3 + 1] = 28;
    }
    snowGeo.attributes.position.needsUpdate = true;
  }

  // ==========================================
  // PLAYER: GANESHA (Blue Runner + Attachments)
  // ==========================================
  const playerGroup = new THREE.Group();

  const playerBodyGeo = new THREE.BoxGeometry(1.2, 1.2, 1.2);
  const playerMat = new THREE.MeshStandardMaterial({
    color: 0x1d4ed8,
    roughness: 0.3,
    metalness: 0.3,
    emissive: 0x1e3a8a,
    emissiveIntensity: 0.25,
    transparent: true,
    opacity: 1.0
  });
  const playerMesh = new THREE.Mesh(playerBodyGeo, playerMat);
  playerMesh.position.y = 0.6;
  playerMesh.castShadow = true;
  playerGroup.add(playerMesh);

  // Crown
  const crownMat = new THREE.MeshStandardMaterial({
    color: 0xf59e0b,
    metalness: 0.7,
    roughness: 0.25,
    transparent: true,
    opacity: 1.0
  });
  const crown = new THREE.Mesh(new THREE.ConeGeometry(0.35, 0.45, 6), crownMat);
  crown.position.set(0, 1.45, 0);
  crown.castShadow = true;
  playerGroup.add(crown);

  // Visor
  const visorMat = new THREE.MeshStandardMaterial({
    color: 0x67e8f9,
    emissive: 0x06b6d4,
    emissiveIntensity: 0.5,
    transparent: true,
    opacity: 1.0
  });
  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.7, 0.25, 0.15), visorMat);
  visor.position.set(0, 0.8, -0.6);
  playerGroup.add(visor);

  // Note: Circular floor shadow disk completely removed per design.
  // Clean 3D shadows are cast dynamically by directional sunlight on all models.

  // ------------------------------------------
  // PROCEDURAL 3D LORD GANESHA MODEL
  // ------------------------------------------
  let ganeshaModelInstance = null;

  function attachPlayerModel() {
    if (!assets.ganesha) return;
    if (ganeshaModelInstance) {
      playerGroup.remove(ganeshaModelInstance);
      ganeshaModelInstance = null;
    }

    ganeshaModelInstance = assets.ganesha.clone(true);
    ganeshaModelInstance.position.set(0, 0, 0);
    ganeshaModelInstance.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
        child.receiveShadow = true;
      }
    });

    playerGroup.add(ganeshaModelInstance);

    // Hide placeholder blue cube, cone crown, and visor
    playerMesh.visible = false;
    crown.visible = false;
    visor.visible = false;
    console.log('✓ Procedural 3D Lord Ganesha model successfully integrated into player!');
  }

  function setGaneshaOpacity(alpha) {
    if (!ganeshaModelInstance) return;
    ganeshaModelInstance.traverse((child) => {
      if (child.isMesh && child.material) {
        child.material.transparent = alpha < 0.99;
        child.material.opacity = alpha;
      }
    });
  }

  // Attach Lord Ganesha if already loaded
  attachPlayerModel();

  // ------------------------------------------
  // ATTACHMENT A: MOOSHIKAN SKATEBOARD (GROUNDED)
  // ------------------------------------------
  const skateboardGroup = new THREE.Group();

  const deck = new THREE.Mesh(
    new THREE.BoxGeometry(1.4, 0.08, 2.4),
    new THREE.MeshStandardMaterial({ color: 0x6d28d9, metalness: 0.6, roughness: 0.3, emissive: 0x4c1d95, emissiveIntensity: 0.3 })
  );
  deck.position.y = 0.18;
  deck.castShadow = true;
  skateboardGroup.add(deck);

  const grip = new THREE.Mesh(
    new THREE.BoxGeometry(1.2, 0.02, 2.2),
    new THREE.MeshStandardMaterial({ color: 0xf59e0b, roughness: 0.7, metalness: 0.4 })
  );
  grip.position.y = 0.23;
  skateboardGroup.add(grip);

  const earGeo = new THREE.CylinderGeometry(0.2, 0.2, 0.05, 16);
  const earMat = new THREE.MeshStandardMaterial({ color: 0xa855f7, metalness: 0.4 });
  const earL = new THREE.Mesh(earGeo, earMat);
  earL.position.set(-0.55, 0.26, -1.05);
  earL.rotation.x = Math.PI / 2;
  skateboardGroup.add(earL);

  const earR = new THREE.Mesh(earGeo, earMat);
  earR.position.set(0.55, 0.26, -1.05);
  earR.rotation.x = Math.PI / 2;
  skateboardGroup.add(earR);

  const wheelGeo = new THREE.CylinderGeometry(0.12, 0.12, 0.12, 16);
  const wheelMat = new THREE.MeshStandardMaterial({ color: 0x06b6d4, emissive: 0x0891b2, emissiveIntensity: 0.5 });
  const skateboardWheels = [];

  [[-0.65, -0.75], [0.65, -0.75], [-0.65, 0.75], [0.65, 0.75]].forEach(([wx, wz]) => {
    const wheel = new THREE.Mesh(wheelGeo, wheelMat);
    wheel.rotation.z = Math.PI / 2;
    wheel.position.set(wx, 0.12, wz);
    wheel.castShadow = true;
    skateboardGroup.add(wheel);
    skateboardWheels.push(wheel);
  });

  skateboardGroup.visible = false;
  playerGroup.add(skateboardGroup);

  // ------------------------------------------
  // ATTACHMENT B: JETPACK (ON PLAYER BACK)
  // ------------------------------------------
  const jetpackGroup = new THREE.Group();

  const thrusterGeo = new THREE.CylinderGeometry(0.18, 0.22, 0.9, 14);
  const thrusterMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8, metalness: 0.8, roughness: 0.2 });
  const nozzleMat = new THREE.MeshStandardMaterial({ color: 0x0284c7, emissive: 0x00f5ff, emissiveIntensity: 0.6 });

  for (let side of [-0.35, 0.35]) {
    const body = new THREE.Mesh(thrusterGeo, thrusterMat);
    body.position.set(side, 0.7, 0.75);
    jetpackGroup.add(body);

    const nozzle = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.18, 0.2, 14), nozzleMat);
    nozzle.position.set(side, 0.2, 0.75);
    jetpackGroup.add(nozzle);
  }

  const brace = new THREE.Mesh(
    new THREE.BoxGeometry(0.9, 0.25, 0.15),
    new THREE.MeshStandardMaterial({ color: 0xef4444, metalness: 0.5 })
  );
  brace.position.set(0, 0.7, 0.7);
  jetpackGroup.add(brace);

  jetpackGroup.visible = false;
  playerGroup.add(jetpackGroup);

  // ------------------------------------------
  // ATTACHMENT C: SUPER SNEAKERS (ON FEET)
  // ------------------------------------------
  const sneakersGroup = new THREE.Group();
  const shoeMat = new THREE.MeshStandardMaterial({ color: 0xf97316, roughness: 0.3, emissive: 0xea580c, emissiveIntensity: 0.4 });
  const soleMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.5 });

  for (let side of [-0.35, 0.35]) {
    const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.38, 0.28, 0.65), shoeMat);
    shoe.position.set(side, 0.14, 0.05);
    shoe.castShadow = true;
    sneakersGroup.add(shoe);

    const sole = new THREE.Mesh(new THREE.BoxGeometry(0.42, 0.08, 0.72), soleMat);
    sole.position.set(side, 0.04, 0.05);
    sneakersGroup.add(sole);

    const spring = new THREE.Mesh(
      new THREE.TorusGeometry(0.18, 0.04, 8, 16),
      new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.8 })
    );
    spring.rotation.x = Math.PI / 2;
    spring.position.set(side, -0.02, 0.05);
    sneakersGroup.add(spring);
  }

  sneakersGroup.visible = false;
  playerGroup.add(sneakersGroup);

  // ------------------------------------------
  // ATTACHMENT D: COIN MAGNET (DUAL AURA RINGS ON PLAYER)
  // Visual distinct from Jumping Shoes
  // ------------------------------------------
  const magnetAuraGroup = new THREE.Group();

  const magRingMat = new THREE.MeshStandardMaterial({
    color: 0xef4444,
    emissive: 0x38bdf8,
    emissiveIntensity: 0.9,
    transparent: true,
    opacity: 0.85
  });

  const magRing1 = new THREE.Mesh(new THREE.TorusGeometry(1.15, 0.035, 8, 28), magRingMat);
  magRing1.rotation.x = Math.PI / 2.3;
  magRing1.position.y = 0.6;
  magnetAuraGroup.add(magRing1);

  const magRing2 = new THREE.Mesh(new THREE.TorusGeometry(1.1, 0.03, 8, 28), magRingMat);
  magRing2.rotation.x = -Math.PI / 2.3;
  magRing2.position.y = 0.6;
  magnetAuraGroup.add(magRing2);

  // Twin magnetic pole indicator nodes
  const poleL = new THREE.Mesh(
    new THREE.BoxGeometry(0.22, 0.35, 0.22),
    new THREE.MeshStandardMaterial({ color: 0xef4444, emissive: 0xdc2626, emissiveIntensity: 0.6 })
  );
  poleL.position.set(-0.76, 0.6, 0);
  magnetAuraGroup.add(poleL);

  const poleR = new THREE.Mesh(
    new THREE.BoxGeometry(0.22, 0.35, 0.22),
    new THREE.MeshStandardMaterial({ color: 0x38bdf8, emissive: 0x0284c7, emissiveIntensity: 0.6 })
  );
  poleR.position.set(0.76, 0.6, 0);
  magnetAuraGroup.add(poleR);

  magnetAuraGroup.visible = false;
  playerGroup.add(magnetAuraGroup);

  playerGroup.position.set(0, 0, 0);
  playerGroup.traverse((child) => {
    if (child.isMesh) {
      child.castShadow = true;
    }
  });
  scene.add(playerGroup);

  // ==========================================
  // THE VILLAIN / POLLUTER (RUNNING AHEAD)
  // ==========================================
  const villainGroup = new THREE.Group();
  villainGroup.scale.set(1.25, 1.25, 1.25);
  villainGroup.position.set(0, 0, -VILLAIN_LEAD_DISTANCE);
  scene.add(villainGroup);

  function attachVillainModel() {
    if (!assets.villain) return;
    while (villainGroup.children.length > 0) {
      villainGroup.remove(villainGroup.children[0]);
    }
    const vModel = assets.villain.clone(true);
    // Face forward away from player towards negative Z
    vModel.rotation.y = Math.PI;
    vModel.traverse((child) => {
      if (child.isMesh) {
        child.castShadow = true;
      }
    });
    villainGroup.add(vModel);
  }

  // Attach villain if already loaded
  attachVillainModel();

  let villainCurrentLane = LANE_CENTER;
  let villainTargetX = 0;
  let villainLaneTimer = 0;

  // ==========================================
  // 3D MODELS: CLIMBABLE TRUCKS, HURDLES & OVERBRIDGES
  // ==========================================

  // 1. CLIMBABLE GARBAGE TRUCKS (SUBWAY SURFERS TRAINS: STATIC, MOVING & RAMP)
  function createGarbageTruck(variant = 'static') {
    const isMoving = variant === 'moving';
    const isRamp = variant === 'ramp';
    const length = TRUCK_LENGTH; // 24.0m
    const width = TRUCK_WIDTH;   // 2.4m
    const height = TRUCK_ROOF_Y; // 3.8m (Roof level: normal jump cannot reach without sneakers or ramp)
    const rampLength = 8.5;

    const wheelsList = [];
    const beaconsList = [];
    const group = new THREE.Group();

    // High-performance procedural 3D GLB model integration
    const sourceModel = isRamp ? (assets.truck_ramp || assets.truck) : (isMoving ? (assets.truck_moving || assets.truck) : assets.truck);
    if (sourceModel) {
      const truckModel = sourceModel.clone(true);
      // Scale length to 24.0m to perfectly wrap the obstacle bounding box
      truckModel.scale.set(1.0, 1.0, length / 18.0);
      truckModel.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
          const lower = child.name.toLowerCase();
          if (lower.includes('wheel')) {
            wheelsList.push(child);
          }
          if (lower.includes('beacon')) {
            beaconsList.push(child);
          }
        }
      });
      group.add(truckModel);

      return {
        mesh: group,
        length: length,
        width: width,
        roofY: height,
        variant: variant,
        isClimbable: true,
        hasRamp: isRamp,
        rampLength: rampLength,
        extraSpeed: isMoving ? 6.0 : 0,
        wheels: wheelsList,
        beacons: beaconsList
      };
    }

    // Body colors based on variant
    let bodyColor = 0x0284c7; // Vibrant Blue for Static
    let cabColor = 0x0369a1;
    if (isMoving) {
      bodyColor = 0xd97706;  // Safety Orange / Diesel for Moving
      cabColor = 0xb45309;
    } else if (isRamp) {
      bodyColor = 0x0f766e;  // Industrial Teal for Ramp Truck
      cabColor = 0x115e59;
    }

    // A. Main Cargo Container
    const cargoLen = length - 5.0; // 19.0m
    const cargoMat = new THREE.MeshStandardMaterial({
      color: bodyColor,
      roughness: 0.45,
      metalness: 0.35
    });
    const cargo = new THREE.Mesh(new THREE.BoxGeometry(width, height - 0.7, cargoLen), cargoMat);
    cargo.position.set(0, (height - 0.7) / 2 + 0.55, 2.5);
    cargo.castShadow = true;
    cargo.receiveShadow = true;
    group.add(cargo);

    // Corrugated Side Panels (industrial freight ribs)
    const ribMat = new THREE.MeshStandardMaterial({ color: cabColor, roughness: 0.5, metalness: 0.4 });
    for (let rz = -cargoLen / 2 + 1.2; rz <= cargoLen / 2 - 1.2; rz += 2.2) {
      for (let side of [-width / 2 - 0.03, width / 2 + 0.03]) {
        const rib = new THREE.Mesh(new THREE.BoxGeometry(0.06, height - 1.0, 0.25), ribMat);
        rib.position.set(side, (height - 1.0) / 2 + 0.65, 2.5 + rz);
        group.add(rib);
      }
    }

    // B. Roof Catwalk Platform (Subway Surfers running surface at y = 3.8)
    const roofMat = new THREE.MeshStandardMaterial({ color: 0x1e293b, roughness: 0.85, metalness: 0.2 });
    const roof = new THREE.Mesh(new THREE.BoxGeometry(width + 0.12, 0.14, cargoLen + 0.1), roofMat);
    roof.position.set(0, height - 0.07, 2.5);
    roof.receiveShadow = true;
    group.add(roof);

    // Roof walkway center strip
    const roofStrip = new THREE.Mesh(
      new THREE.BoxGeometry(1.4, 0.04, cargoLen - 0.4),
      new THREE.MeshStandardMaterial({ color: 0x475569, roughness: 0.9 })
    );
    roofStrip.position.set(0, height + 0.01, 2.5);
    roofStrip.receiveShadow = true;
    group.add(roofStrip);

    // C. Driver Cab at Front
    const cabMat = new THREE.MeshStandardMaterial({ color: cabColor, roughness: 0.35, metalness: 0.4 });
    const cabHeight = height - 0.5;
    const cab = new THREE.Mesh(new THREE.BoxGeometry(width - 0.08, cabHeight, 4.8), cabMat);
    cab.position.set(0, cabHeight / 2 + 0.5, -(length / 2 - 2.4));
    cab.castShadow = true;
    cab.receiveShadow = true;
    group.add(cab);

    // Cab Windshield
    const windshield = new THREE.Mesh(
      new THREE.BoxGeometry(width - 0.3, 0.95, 0.12),
      new THREE.MeshStandardMaterial({ color: 0x38bdf8, roughness: 0.1, metalness: 0.9, opacity: 0.9, transparent: true })
    );
    windshield.position.set(0, height - 1.1, -(length / 2 - 0.05));
    group.add(windshield);

    // Front Grille & Heavy Bumper
    const grille = new THREE.Mesh(
      new THREE.BoxGeometry(width - 0.4, 0.85, 0.2),
      new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.7 })
    );
    grille.position.set(0, 1.15, -(length / 2 + 0.02));
    group.add(grille);

    const bumper = new THREE.Mesh(
      new THREE.BoxGeometry(width + 0.15, 0.45, 0.4),
      new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.6, metalness: 0.5 })
    );
    bumper.position.set(0, 0.45, -(length / 2 + 0.1));
    bumper.castShadow = true;
    group.add(bumper);

    // Headlights
    for (let side of [-0.85, 0.85]) {
      const headlight = new THREE.Mesh(
        new THREE.BoxGeometry(0.38, 0.3, 0.12),
        new THREE.MeshBasicMaterial({ color: 0xfef08a })
      );
      headlight.position.set(side, 1.15, -(length / 2 + 0.15));
      group.add(headlight);
    }

    // Heavy Industrial Wheels (Fallback)
    const truckWheelGeo = new THREE.CylinderGeometry(0.55, 0.55, 0.36, 16);
    const truckWheelMat = new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.85 });
    const wheelHubMat = new THREE.MeshStandardMaterial({ color: 0x64748b, metalness: 0.7 });

    const wheelZOffsets = [-length / 2 + 2.5, 0, length / 2 - 5.5, length / 2 - 2.0];
    for (let wz of wheelZOffsets) {
      for (let wx of [-width / 2 - 0.08, width / 2 + 0.08]) {
        const wheelGroup = new THREE.Group();
        const tire = new THREE.Mesh(truckWheelGeo, truckWheelMat);
        tire.rotation.z = Math.PI / 2;
        tire.castShadow = true;
        wheelGroup.add(tire);

        const hub = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.38, 12), wheelHubMat);
        hub.rotation.z = Math.PI / 2;
        wheelGroup.add(hub);

        wheelGroup.position.set(wx, 0.55, wz);
        group.add(wheelGroup);
        wheelsList.push(wheelGroup);
      }
    }

    // D. Moving Variant Special Features (flashing amber beacons, high-beams)
    if (isMoving) {
      for (let side of [-0.75, 0.75]) {
        const beacon = new THREE.Mesh(
          new THREE.CylinderGeometry(0.18, 0.22, 0.35, 12),
          new THREE.MeshBasicMaterial({ color: 0xfbbf24 })
        );
        beacon.position.set(side, height - 0.32, -(length / 2 - 1.8));
        group.add(beacon);
        beaconsList.push(beacon);
      }

      // Headlight light cones (projecting forward)
      for (let side of [-0.85, 0.85]) {
        const cone = new THREE.Mesh(
          new THREE.ConeGeometry(0.85, 4.5, 12, 1, true),
          new THREE.MeshBasicMaterial({ color: 0xfef08a, transparent: true, opacity: 0.22, side: THREE.DoubleSide })
        );
        cone.rotation.x = -Math.PI / 2;
        cone.position.set(side, 1.15, -(length / 2 + 2.4));
        group.add(cone);
      }
    }

    // E. Ramp Variant Special Features (Wedge Incline at Front: Run up to Roof!)
    if (isRamp) {
      const rampGroup = new THREE.Group();
      // Length along slope: hyp = sqrt(8.5^2 + 3.8^2) ≈ 9.31m
      const hyp = Math.sqrt(rampLength * rampLength + height * height);
      const rampAngle = Math.atan2(height, rampLength); // ~0.42 rad

      // Inclined ramp deck
      const rampDeckGeo = new THREE.BoxGeometry(width - 0.08, 0.22, hyp);
      const rampDeckMat = new THREE.MeshStandardMaterial({
        color: 0x0f766e,
        roughness: 0.5,
        metalness: 0.3
      });
      const rampDeck = new THREE.Mesh(rampDeckGeo, rampDeckMat);
      rampDeck.rotation.x = rampAngle;
      rampDeck.position.set(0, height / 2, -(length / 2 + rampLength / 2));
      rampDeck.receiveShadow = true;
      rampGroup.add(rampDeck);

      // High-contrast yellow/black hazard chevron center strip
      const chevronStrip = new THREE.Mesh(
        new THREE.BoxGeometry(1.6, 0.04, hyp - 0.2),
        new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.4, emissive: 0xca8a04, emissiveIntensity: 0.25 })
      );
      chevronStrip.rotation.x = rampAngle;
      chevronStrip.position.set(0, height / 2 + 0.12, -(length / 2 + rampLength / 2));
      chevronStrip.receiveShadow = true;
      rampGroup.add(chevronStrip);

      // Side guardrails along ramp
      for (let side of [-width / 2 + 0.08, width / 2 - 0.08]) {
        const rail = new THREE.Mesh(
          new THREE.BoxGeometry(0.12, 0.55, hyp),
          new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.6 })
        );
        rail.rotation.x = rampAngle;
        rail.position.set(side, height / 2 + 0.35, -(length / 2 + rampLength / 2));
        rampGroup.add(rail);
      }

      group.add(rampGroup);
    }

    return {
      mesh: group,
      length: length,
      width: width,
      roofY: height,
      variant: variant,
      isClimbable: true,
      hasRamp: isRamp,
      rampLength: isRamp ? rampLength : 0,
      extraSpeed: isMoving ? 6.0 : 0,
      wheels: wheelsList,
      beacons: beaconsList
    };
  }

  // 2. HIGH HURDLE (OVERHEAD HIGHWAY SIGN / GANTRY: MUST SLIDE UNDER)
  function createHighHurdle() {
    const group = new THREE.Group();
    const width = 2.5;
    const clearanceY = 1.15; // Clearance from ground: 0 to 1.15m is open air
    const topY = 2.65;       // Top of sign structure

    // Side Support Upright Pillars
    const postGeo = new THREE.CylinderGeometry(0.08, 0.08, topY, 12);
    const postMat = new THREE.MeshStandardMaterial({ color: 0x334155, metalness: 0.7, roughness: 0.3 });

    for (let side of [-width / 2 + 0.08, width / 2 - 0.08]) {
      const post = new THREE.Mesh(postGeo, postMat);
      post.position.set(side, topY / 2, 0);
      post.castShadow = true;
      group.add(post);

      const foot = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.25, 0.15, 12), postMat);
      foot.position.set(side, 0.075, 0);
      group.add(foot);
    }

    // Overhead Crossbeam
    const beam = new THREE.Mesh(
      new THREE.BoxGeometry(width + 0.15, 0.14, 0.18),
      postMat
    );
    beam.position.set(0, topY - 0.07, 0);
    group.add(beam);

    // Suspended Signboard (spans from y = 1.15 to y = 2.5)
    const signHeight = topY - 0.14 - clearanceY; // ~1.36m
    const signBoard = new THREE.Mesh(
      new THREE.BoxGeometry(width - 0.25, signHeight, 0.22),
      new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.35, emissive: 0xb45309, emissiveIntensity: 0.25 })
    );
    signBoard.position.set(0, clearanceY + signHeight / 2, 0);
    signBoard.castShadow = true;
    group.add(signBoard);

    // Hazard Caution Stripes on Signboard
    const stripe = new THREE.Mesh(
      new THREE.BoxGeometry(width - 0.32, 0.45, 0.25),
      new THREE.MeshStandardMaterial({ color: 0x0f172a, roughness: 0.8 })
    );
    stripe.position.set(0, clearanceY + signHeight / 2, 0);
    group.add(stripe);

    // Flashing Warning Lights on corners
    const beaconGeo = new THREE.SphereGeometry(0.14, 12, 10);
    const beaconMat = new THREE.MeshBasicMaterial({ color: 0xef4444 });
    for (let side of [-width / 2 + 0.25, width / 2 - 0.25]) {
      const light = new THREE.Mesh(beaconGeo, beaconMat);
      light.position.set(side, topY + 0.08, 0);
      group.add(light);
    }

    return {
      mesh: group,
      length: 0.6,
      width: width,
      roofY: topY,
      clearanceY: clearanceY,
      isHighHurdle: true,
      isClimbable: false
    };
  }

  // 3. LOW BARRICADE (GROUND ROADBLOCK: MUST JUMP OVER, SLIDING CRASHES)
  function createLowBarricade() {
    const group = new THREE.Group();
    const width = 2.4;
    const height = 1.15; // Sitting on ground from y = 0 to 1.15m

    if (assets.garbage_jar) {
      // Cloned procedural 3D toxic garbage jar roadblock cluster
      const positions = [
        { x: -0.65, z: 0.02, rotY: 0.35, scale: 1.0 },
        { x: 0.0, z: -0.08, rotY: -1.2, scale: 0.95 },
        { x: 0.65, z: 0.04, rotY: 1.8, scale: 1.0 }
      ];
      positions.forEach(p => {
        const jar = assets.garbage_jar.clone(true);
        jar.position.set(p.x, 0, p.z);
        jar.rotation.y = p.rotY;
        jar.scale.set(p.scale, p.scale, p.scale);
        jar.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
          }
        });
        group.add(jar);
      });
    } else {
      // Concrete Base
      const baseMat = new THREE.MeshStandardMaterial({ color: 0x64748b, roughness: 0.9 });
      const base = new THREE.Mesh(new THREE.BoxGeometry(width, 0.35, 0.65), baseMat);
      base.position.set(0, 0.175, 0);
      base.castShadow = true;
      base.receiveShadow = true;
      group.add(base);

      // Striped Barrier Board
      const boardMat = new THREE.MeshStandardMaterial({
        color: 0xef4444,
        roughness: 0.4,
        emissive: 0x991b1b,
        emissiveIntensity: 0.25
      });
      const board = new THREE.Mesh(new THREE.BoxGeometry(width - 0.1, height - 0.35, 0.25), boardMat);
      board.position.set(0, 0.35 + (height - 0.35) / 2, 0);
      board.castShadow = true;
      group.add(board);

      // White reflective stripes
      for (let wx of [-0.65, 0, 0.65]) {
        const whiteStripe = new THREE.Mesh(
          new THREE.BoxGeometry(0.35, height - 0.4, 0.28),
          new THREE.MeshStandardMaterial({ color: 0xf8fafc, roughness: 0.3 })
        );
        whiteStripe.position.set(wx, 0.35 + (height - 0.35) / 2, 0);
        group.add(whiteStripe);
      }

      // Flashing Warning Beacons on top
      for (let side of [-0.85, 0.85]) {
        const beacon = new THREE.Mesh(
          new THREE.SphereGeometry(0.12, 10, 10),
          new THREE.MeshBasicMaterial({ color: 0xfacc15 })
        );
        beacon.position.set(side, height + 0.1, 0);
        group.add(beacon);
      }
    }

    return {
      mesh: group,
      length: 0.65,
      width: width,
      roofY: height,
      isLowBarricade: true,
      isClimbable: false
    };
  }

  // 4. TOXIC WASTE BARREL (GROUND OBSTACLE)
  function createBarrelObstacle() {
    const group = new THREE.Group();
    if (assets.garbage_jar) {
      const jar = assets.garbage_jar.clone(true);
      jar.position.set(0, 0, 0);
      jar.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
      group.add(jar);
    } else {
      const barrelGeo = new THREE.CylinderGeometry(0.55, 0.55, 1.25, 16);
      const barrelMat = new THREE.MeshStandardMaterial({
        color: 0xef4444,
        roughness: 0.35,
        metalness: 0.4,
        emissive: 0x991b1b,
        emissiveIntensity: 0.3
      });
      const barrel = new THREE.Mesh(barrelGeo, barrelMat);
      barrel.position.y = 0.62;
      barrel.castShadow = true;
      group.add(barrel);

      for (let ry of [0.35, 0.9]) {
        const ring = new THREE.Mesh(
          new THREE.CylinderGeometry(0.57, 0.57, 0.12, 16),
          new THREE.MeshStandardMaterial({ color: 0xfacc15, roughness: 0.5 })
        );
        ring.position.y = ry;
        group.add(ring);
      }
    }

    return {
      mesh: group,
      length: 1.2,
      width: 1.2,
      roofY: 1.25,
      isClimbable: false
    };
  }

  // 5. OVERHEAD CEREMONIAL OVERBRIDGE / ARCH (SPANS ALL 3 LANES)
  function createOverbridge() {
    const group = new THREE.Group();
    const archSpan = 14.0;       // Spans comfortably across all 3 lanes (-3, 0, +3)
    const clearanceY = 6.4;      // Bottom clearance: 6.4m (tall trucks are 3.8m, so trucks pass easily)
    const deckHeight = 1.2;

    const stoneMat = new THREE.MeshStandardMaterial({
      color: 0xf8fafc,
      roughness: 0.75,
      metalness: 0.15
    });
    const goldTrimMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      metalness: 0.7,
      roughness: 0.25
    });

    // Left and Right Giant Support Pillars (positioned outside the road at x = -5.8 and +5.8)
    for (let side of [-5.8, 5.8]) {
      const pillar = new THREE.Mesh(new THREE.BoxGeometry(1.6, clearanceY + deckHeight, 2.2), stoneMat);
      pillar.position.set(side, (clearanceY + deckHeight) / 2, 0);
      pillar.castShadow = true;
      pillar.receiveShadow = true;
      group.add(pillar);

      // Pillar base & capital trim
      for (let py of [0.4, clearanceY]) {
        const trim = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.35, 2.5), goldTrimMat);
        trim.position.set(side, py, 0);
        group.add(trim);
      }

      // Golden Kalash Finial on top of pillar
      const kalash = new THREE.Mesh(new THREE.ConeGeometry(0.45, 1.1, 12), goldTrimMat);
      kalash.position.set(side, clearanceY + deckHeight + 0.65, 0);
      group.add(kalash);
    }

    // Overhead Bridge Deck Span
    const deck = new THREE.Mesh(
      new THREE.BoxGeometry(archSpan, deckHeight, 2.8),
      stoneMat
    );
    deck.position.set(0, clearanceY + deckHeight / 2, 0);
    deck.castShadow = true;
    deck.receiveShadow = true;
    group.add(deck);

    // Decorative Gateway Arch Header Banner
    const banner = new THREE.Mesh(
      new THREE.BoxGeometry(archSpan - 2.5, 0.8, 0.25),
      new THREE.MeshStandardMaterial({ color: 0xd97706, roughness: 0.4, emissive: 0xb45309, emissiveIntensity: 0.3 })
    );
    banner.position.set(0, clearanceY + deckHeight / 2, -1.45);
    group.add(banner);

    // Hanging Festive Marigold Garlands
    const garlandGeo = new THREE.TorusGeometry(1.4, 0.08, 8, 20, Math.PI);
    const garlandMat = new THREE.MeshStandardMaterial({ color: 0xf59e0b, emissive: 0xd97706, emissiveIntensity: 0.4 });
    for (let gx of [-3.2, 0, 3.2]) {
      const garland = new THREE.Mesh(garlandGeo, garlandMat);
      garland.rotation.z = Math.PI;
      garland.position.set(gx, clearanceY - 0.1, -1.35);
      group.add(garland);
    }

    return {
      mesh: group,
      clearanceY: clearanceY
    };
  }

  // ==========================================
  // 3D MODELS: COLLECTIBLES & POWER-UPS
  // ==========================================

  // 1. MODAK (GOLDEN COIN / CURRENCY)
  const modakGoldMat = new THREE.MeshStandardMaterial({
    color: 0xffb703,
    roughness: 0.25,
    metalness: 0.65,
    emissive: 0xd97706,
    emissiveIntensity: 0.3
  });

  function createModakModel() {
    if (assets.modak) {
      return assets.modak.clone(true);
    }

    // High quality procedural fallback if spawned before async GLB load finishes
    const group = new THREE.Group();
    const bottom = new THREE.Mesh(
      new THREE.SphereGeometry(0.48, 16, 12, 0, Math.PI * 2, 0, Math.PI * 0.65),
      modakGoldMat
    );
    bottom.rotation.x = Math.PI;
    bottom.position.y = 0.46;
    bottom.castShadow = true;
    group.add(bottom);

    const top = new THREE.Mesh(new THREE.ConeGeometry(0.44, 0.7, 16), modakGoldMat);
    top.position.y = 0.72;
    top.castShadow = true;
    group.add(top);

    group.scale.set(1.05, 1.05, 1.05);
    return group;
  }

  // 2. POWER-UP: JETPACK PICKUP ITEM
  function createJetpackPickup() {
    const group = new THREE.Group();
    const mat = new THREE.MeshStandardMaterial({ color: 0x00f5ff, emissive: 0x0284c7, emissiveIntensity: 0.5, metalness: 0.7 });

    for (let s of [-0.25, 0.25]) {
      const rocket = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.2, 0.75, 12), mat);
      rocket.position.set(s, 0.5, 0);
      group.add(rocket);

      const nose = new THREE.Mesh(new THREE.ConeGeometry(0.18, 0.35, 12), new THREE.MeshStandardMaterial({ color: 0xef4444 }));
      nose.position.set(s, 1.0, 0);
      group.add(nose);
    }

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.65, 0.05, 8, 20),
      new THREE.MeshBasicMaterial({ color: 0x00f5ff })
    );
    ring.position.y = 0.6;
    ring.rotation.x = Math.PI / 2;
    group.add(ring);

    group.scale.set(1.2, 1.2, 1.2);
    return group;
  }

  // 3. POWER-UP: SUPER SNEAKERS PICKUP ITEM
  function createSneakersPickup() {
    const group = new THREE.Group();
    const shoeMat = new THREE.MeshStandardMaterial({ color: 0xf97316, emissive: 0xea580c, emissiveIntensity: 0.4 });
    const shoe = new THREE.Mesh(new THREE.BoxGeometry(0.5, 0.35, 0.8), shoeMat);
    shoe.position.y = 0.5;
    shoe.castShadow = true;
    group.add(shoe);

    const wingMat = new THREE.MeshStandardMaterial({ color: 0xfacc15, metalness: 0.7 });
    for (let s of [-0.3, 0.3]) {
      const wing = new THREE.Mesh(new THREE.ConeGeometry(0.2, 0.5, 6), wingMat);
      wing.rotation.z = s * -Math.PI / 3;
      wing.position.set(s, 0.65, -0.1);
      group.add(wing);
    }

    const ring = new THREE.Mesh(
      new THREE.TorusGeometry(0.65, 0.05, 8, 20),
      new THREE.MeshBasicMaterial({ color: 0xf97316 })
    );
    ring.position.y = 0.5;
    ring.rotation.x = Math.PI / 2;
    group.add(ring);

    group.scale.set(1.2, 1.2, 1.2);
    return group;
  }

  // 4. POWER-UP: THE COIN MAGNET PICKUP ITEM (HORSESHOE MAGNET)
  function createMagnetPickup() {
    const group = new THREE.Group();
    const magnetRedMat = new THREE.MeshStandardMaterial({
      color: 0xef4444,
      metalness: 0.6,
      roughness: 0.25,
      emissive: 0xb91c1c,
      emissiveIntensity: 0.35
    });
    const magnetSilverMat = new THREE.MeshStandardMaterial({
      color: 0x38bdf8,
      metalness: 0.85,
      roughness: 0.15,
      emissive: 0x0284c7,
      emissiveIntensity: 0.5
    });

    // Horseshoe curved arch
    const archGeo = new THREE.TorusGeometry(0.48, 0.14, 12, 24, Math.PI);
    const arch = new THREE.Mesh(archGeo, magnetRedMat);
    arch.position.set(0, 0.55, 0);
    arch.castShadow = true;
    group.add(arch);

    // Left Prong
    const prongGeo = new THREE.CylinderGeometry(0.14, 0.14, 0.45, 12);
    const prongL = new THREE.Mesh(prongGeo, magnetRedMat);
    prongL.position.set(-0.48, 0.35, 0);
    group.add(prongL);

    const tipL = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.2, 12), magnetSilverMat);
    tipL.position.set(-0.48, 0.1, 0);
    group.add(tipL);

    // Right Prong
    const prongR = new THREE.Mesh(prongGeo, magnetRedMat);
    prongR.position.set(0.48, 0.35, 0);
    group.add(prongR);

    const tipR = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.2, 12), magnetSilverMat);
    tipR.position.set(0.48, 0.1, 0);
    group.add(tipR);

    // Glowing magnetic field halo
    const aura = new THREE.Mesh(
      new THREE.TorusGeometry(0.72, 0.045, 8, 24),
      new THREE.MeshBasicMaterial({ color: 0x38bdf8 })
    );
    aura.rotation.x = Math.PI / 2;
    aura.position.y = 0.5;
    group.add(aura);

    group.scale.set(1.2, 1.2, 1.2);
    return group;
  }

  // 5. POWER-UP: 2X MULTIPLIER PICKUP ITEM
  function createMultiplierPickup() {
    const group = new THREE.Group();
    const starMat = new THREE.MeshStandardMaterial({
      color: 0xfacc15,
      emissive: 0xeab308,
      emissiveIntensity: 0.6,
      metalness: 0.8,
      roughness: 0.2
    });

    const star = new THREE.Mesh(new THREE.CylinderGeometry(0.55, 0.55, 0.15, 8), starMat);
    star.rotation.x = Math.PI / 2;
    star.position.y = 0.55;
    group.add(star);

    const orbit = new THREE.Mesh(
      new THREE.TorusGeometry(0.8, 0.04, 8, 24),
      new THREE.MeshBasicMaterial({ color: 0xfde047 })
    );
    orbit.position.y = 0.55;
    group.add(orbit);

    group.scale.set(1.25, 1.25, 1.25);
    return group;
  }

  // 6. POWER-UP: DIVINE GADA (LORD GANESHA'S SACRED MACE)
  function createGadaPickup() {
    const group = new THREE.Group();
    const goldMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      metalness: 0.85,
      roughness: 0.2,
      emissive: 0xd97706,
      emissiveIntensity: 0.45
    });
    const jewelMat = new THREE.MeshStandardMaterial({
      color: 0xfef08a,
      metalness: 0.9,
      roughness: 0.1,
      emissive: 0xfbbf24,
      emissiveIntensity: 0.75
    });

    // Handle shaft
    const shaftGeo = new THREE.CylinderGeometry(0.06, 0.08, 1.1, 12);
    const shaft = new THREE.Mesh(shaftGeo, goldMat);
    shaft.position.y = 0.55;
    shaft.castShadow = true;
    group.add(shaft);

    // Mace head (fluted golden sphere)
    const headGeo = new THREE.SphereGeometry(0.32, 16, 16);
    headGeo.scale(1.0, 1.25, 1.0);
    const head = new THREE.Mesh(headGeo, goldMat);
    head.position.y = 0.95;
    head.castShadow = true;
    group.add(head);

    // Fluted decorative jewel band
    const ringGeo = new THREE.TorusGeometry(0.33, 0.04, 8, 20);
    const ring = new THREE.Mesh(ringGeo, jewelMat);
    ring.rotation.x = Math.PI / 2;
    ring.position.y = 0.95;
    group.add(ring);

    // Top spike / finial
    const spikeGeo = new THREE.ConeGeometry(0.12, 0.32, 12);
    const spike = new THREE.Mesh(spikeGeo, jewelMat);
    spike.position.y = 1.4;
    spike.castShadow = true;
    group.add(spike);

    // Bottom pommel
    const pommelGeo = new THREE.SphereGeometry(0.12, 12, 12);
    const pommel = new THREE.Mesh(pommelGeo, jewelMat);
    pommel.position.y = 0.02;
    group.add(pommel);

    // Radiant divine aura ring
    const aura = new THREE.Mesh(
      new THREE.TorusGeometry(0.68, 0.04, 8, 24),
      new THREE.MeshBasicMaterial({ color: 0xfbbf24 })
    );
    aura.rotation.x = Math.PI / 2;
    aura.position.y = 0.75;
    group.add(aura);

    group.scale.set(1.15, 1.15, 1.15);
    return group;
  }

  function createGadaHandheld() {
    const gada = createGadaPickup();
    // Remove glowing aura ring for wielded weapon
    const childrenToKeep = gada.children.filter(c => !(c.geometry instanceof THREE.TorusGeometry && c.material instanceof THREE.MeshBasicMaterial));
    gada.children = childrenToKeep;
    gada.scale.set(1.05, 1.05, 1.05);
    gada.rotation.z = -Math.PI / 4;
    gada.rotation.y = Math.PI / 6;
    gada.position.set(0.72, 0.95, -0.2); // Positioned beside Ganesha's right side
    return gada;
  }

  // Golden Shockwave VFX System
  const activeShockwaves = [];
  function createGoldenShockwave(pos) {
    const shockwaveGeo = new THREE.RingGeometry(0.4, 0.9, 32);
    const shockwaveMat = new THREE.MeshBasicMaterial({
      color: 0xfbbf24,
      transparent: true,
      opacity: 0.95,
      side: THREE.DoubleSide,
      depthWrite: false
    });
    const mesh = new THREE.Mesh(shockwaveGeo, shockwaveMat);
    mesh.position.set(pos.x, Math.max(0.18, pos.y), pos.z);
    mesh.rotation.x = -Math.PI / 2;
    scene.add(mesh);

    activeShockwaves.push({
      mesh: mesh,
      radius: 0.9,
      maxRadius: 7.0,
      opacity: 0.95,
      expandSpeed: 22.0
    });
  }

  function updateShockwaves(delta) {
    for (let i = activeShockwaves.length - 1; i >= 0; i--) {
      const sw = activeShockwaves[i];
      sw.radius += sw.expandSpeed * delta;
      const progress = sw.radius / sw.maxRadius;
      sw.mesh.scale.set(sw.radius, sw.radius, 1.0);
      sw.mesh.material.opacity = Math.max(0, (1.0 - progress) * 0.95);
      if (progress >= 1.0) {
        scene.remove(sw.mesh);
        sw.mesh.geometry.dispose();
        sw.mesh.material.dispose();
        activeShockwaves.splice(i, 1);
      }
    }
  }

  // ==========================================
  // PARABOLIC BEZIER ARCS (LEVEL DESIGN)
  // ==========================================
  function spawnModakParabolicArc(lane, startZ, endZ, startY, peakY, endY, count = 8) {
    for (let i = 0; i < count; i++) {
      const t = i / (count - 1);
      const z = startZ + t * (endZ - startZ);
      const y = (1 - t) * (1 - t) * startY + 2 * (1 - t) * t * peakY + t * t * endY;

      const modakMesh = createModakModel();
      modakMesh.position.set(LANES[lane], y, z);
      scene.add(modakMesh);

      activeCollectibles.push({
        type: 'modak',
        mesh: modakMesh,
        lane: lane,
        baseY: y,
        isSkyItem: false,
        hoverOffset: 0
      });
    }
  }

  // ==========================================
  // DYNAMIC PROCEDURAL SPAWNING SYSTEM
  // ==========================================
  function spawnTruckInLane(lane, variant, spawnZ) {
    const truckData = createGarbageTruck(variant);
    truckData.mesh.position.set(LANES[lane], 0, spawnZ);
    scene.add(truckData.mesh);

    activeObstacles.push({
      type: 'truck',
      variant: variant,
      isClimbable: true,
      hasRamp: truckData.hasRamp,
      rampLength: truckData.rampLength,
      extraSpeed: truckData.extraSpeed,
      mesh: truckData.mesh,
      lane: lane,
      x: LANES[lane],
      width: truckData.width,
      length: truckData.length,
      roofY: truckData.roofY,
      wheels: truckData.wheels,
      beacons: truckData.beacons
    });

    if (variant === 'ramp') {
      // Modaks along the ramp slope up to roof and down the back (Ramp Trucks only!)
      // Front ramp incline (spawnZ + 12.0 down to spawnZ + 2.5):
      spawnModakParabolicArc(lane, spawnZ + 12.5, spawnZ + 2.5, 0.5, 2.4, 4.3, 6);
      // Flat roof catwalk (spawnZ + 2.5 down to spawnZ - 9.0):
      spawnModakParabolicArc(lane, spawnZ + 2.5, spawnZ - 9.0, 4.3, 4.5, 4.3, 7);
      // Rear descent leap (spawnZ - 9.0 down to spawnZ - 15.0):
      spawnModakParabolicArc(lane, spawnZ - 9.0, spawnZ - 15.0, 4.3, 2.8, 0.5, 5);
    } else {
      // Standard / Moving Blockage Trucks: Clean! No Modaks spawned on top!
    }
  }

  function spawnHighHurdleInLane(lane, spawnZ) {
    const hurdleData = createHighHurdle();
    hurdleData.mesh.position.set(LANES[lane], 0, spawnZ);
    scene.add(hurdleData.mesh);

    activeObstacles.push({
      type: 'high_hurdle',
      isHighHurdle: true,
      isClimbable: false,
      mesh: hurdleData.mesh,
      lane: lane,
      x: LANES[lane],
      width: hurdleData.width,
      length: hurdleData.length,
      roofY: hurdleData.roofY,
      clearanceY: hurdleData.clearanceY
    });

    // Low ground Modak trail under the signboard to reward rolling/sliding!
    for (let mz = -3.5; mz <= 3.5; mz += 1.6) {
      const modakMesh = createModakModel();
      modakMesh.position.set(LANES[lane], 0.35, spawnZ + mz);
      scene.add(modakMesh);
      activeCollectibles.push({
        type: 'modak',
        mesh: modakMesh,
        lane: lane,
        baseY: 0.35,
        isSkyItem: false,
        hoverOffset: mz
      });
    }
  }

  function spawnLowBarricadeInLane(lane, spawnZ) {
    const barData = createLowBarricade();
    barData.mesh.position.set(LANES[lane], 0, spawnZ);
    scene.add(barData.mesh);

    activeObstacles.push({
      type: 'low_barricade',
      isLowBarricade: true,
      isClimbable: false,
      mesh: barData.mesh,
      lane: lane,
      x: LANES[lane],
      width: barData.width,
      length: barData.length,
      roofY: barData.roofY
    });

    // Parabolic Modak jump arc over the roadblock!
    spawnModakParabolicArc(lane, spawnZ - 4.5, spawnZ + 4.5, 0.4, 3.2, 0.4, 7);
  }

  // ----------------------------------------------------
  // POWER-UP PACING (MINIMUM 350m DISTANCE GUARANTEE)
  // ----------------------------------------------------
  function canSpawnPowerup() {
    if (isJetpackActive) return false;
    return (totalDistanceRun - lastPowerupSpawnDistance) >= MIN_POWERUP_SPAWN_GAP;
  }

  function recordPowerupSpawn() {
    lastPowerupSpawnDistance = totalDistanceRun;
  }

  // ----------------------------------------------------
  // FAIR OBSTACLE SPAWNING (PATH GUARANTEE SYSTEM)
  // Ensures 3 solid garbage trucks NEVER block all 3 lanes
  // ----------------------------------------------------
  function isLaneSolidTruckBlocked(lane, targetZ, radius = 22.0) {
    for (let obs of activeObstacles) {
      if (obs.lane === lane && obs.type === 'truck' && !obs.hasRamp) {
        const halfL = (obs.length || 24.0) / 2;
        if (Math.abs(obs.mesh.position.z - targetZ) <= (halfL + radius)) {
          return true;
        }
      }
    }
    return false;
  }

  function getSolidTruckBlockedLanes(targetZ) {
    return [0, 1, 2].filter(l => isLaneSolidTruckBlocked(l, targetZ));
  }

  function spawnWave() {
    const spawnZ = -SPAWN_DISTANCE;

    // ----------------------------------------------------
    // JETPACK COIN TRAILS (LINEAR DENSE SKY SPAWNING)
    // When Jetpack is active, STOP spawning ground obstacles!
    // ----------------------------------------------------
    if (isJetpackActive && !isJetpackDescending) {
      if (Math.random() < 0.32) {
        jetpackSkyLane = Math.floor(Math.random() * 3);
      }

      // Dense straight line of Modaks perfectly aligned in the sky lane
      for (let mz = -14; mz <= 14; mz += 2.2) {
        const modakMesh = createModakModel();
        modakMesh.position.set(LANES[jetpackSkyLane], JETPACK_Y, spawnZ + mz);
        scene.add(modakMesh);

        activeCollectibles.push({
          type: 'modak',
          mesh: modakMesh,
          lane: jetpackSkyLane,
          baseY: JETPACK_Y,
          isSkyItem: true,
          hoverOffset: mz
        });
      }
      return; // Stop here! No ground obstacles during jetpack flight!
    }

    // Inspect existing solid trucks in upcoming section to prevent 3-lane impassable choke points
    const blockedLanes = getSolidTruckBlockedLanes(spawnZ);

    // If 2 or more lanes already have solid non-ramp trucks overlapping this Z-zone,
    // we MUST NOT spawn any solid trucks! Provide an open Modak run or a Ramp Truck.
    if (blockedLanes.length >= 2) {
      const openLanes = [0, 1, 2].filter(l => !blockedLanes.includes(l));
      const safeLane = openLanes.length > 0 ? openLanes[0] : 1;

      if (Math.random() < 0.45) {
        spawnTruckInLane(safeLane, 'ramp', spawnZ);
      } else {
        spawnLaneItem(safeLane, spawnZ);
      }
      return;
    }

    const rand = Math.random();

    // ----------------------------------------------------
    // PATTERN 1: 2-LANE CHOKE POINT (GUARANTEED AT LEAST 1 RAMP + 1 CLEAR ESCAPE LANE)
    // ----------------------------------------------------
    if (rand < 0.22) {
      const unblocked = [0, 1, 2].filter(l => !blockedLanes.includes(l));
      const openLane = unblocked[Math.floor(Math.random() * unblocked.length)];
      const targetBlocked = [0, 1, 2].filter(l => l !== openLane);

      // FAIRNESS RULE: When 2 trucks spawn together, at least ONE must have an inclined front ramp!
      // This guarantees the player can always leap/run on top of one or choose the open lane.
      spawnTruckInLane(targetBlocked[0], 'ramp', spawnZ);

      // Second truck can be moving or static, as long as it does not create a 3-lane wall
      const secondVariant = Math.random() < 0.5 ? 'moving' : 'static';
      spawnTruckInLane(targetBlocked[1], secondVariant, spawnZ);

      // Open Lane: Guaranteed safe path with Modaks or paced power-up
      spawnLaneItem(openLane, spawnZ);
      return;
    }

    // ----------------------------------------------------
    // PATTERN 2: SINGLE GARBAGE TRUCK (RAMP, MOVING, OR STATIC)
    // ----------------------------------------------------
    if (rand < 0.58) {
      const availableLanes = [0, 1, 2].filter(l => !blockedLanes.includes(l));
      const truckLane = availableLanes.splice(Math.floor(Math.random() * availableLanes.length), 1)[0];

      // If any other lane was already blocked ahead, force this truck to be a Ramp Truck!
      const mustBeRamp = blockedLanes.length >= 1;
      const variantRoll = Math.random();
      const variant = mustBeRamp ? 'ramp' : (variantRoll < 0.40 ? 'ramp' : (variantRoll < 0.72 ? 'moving' : 'static'));
      spawnTruckInLane(truckLane, variant, spawnZ);

      const remainingLanes = [0, 1, 2].filter(l => l !== truckLane);
      const secondLane = remainingLanes[0];
      const thirdLane = remainingLanes[1];

      spawnLaneItem(secondLane, spawnZ);

      if (Math.random() < 0.45) {
        spawnLowBarricadeInLane(thirdLane, spawnZ);
      } else {
        spawnLaneItem(thirdLane, spawnZ);
      }
      return;
    }

    // ----------------------------------------------------
    // PATTERN 3: HURDLES & BARRICADES (ROLL/SLIDE VS JUMP VARIETY)
    // ----------------------------------------------------
    if (rand < 0.84) {
      const lanesAvailable = [0, 1, 2];
      const hurdleLane = lanesAvailable.splice(Math.floor(Math.random() * lanesAvailable.length), 1)[0];
      const barLane = lanesAvailable.splice(Math.floor(Math.random() * lanesAvailable.length), 1)[0];
      const freeLane = lanesAvailable[0];

      spawnHighHurdleInLane(hurdleLane, spawnZ);
      spawnLowBarricadeInLane(barLane, spawnZ);
      spawnLaneItem(freeLane, spawnZ);
      return;
    }

    // ----------------------------------------------------
    // PATTERN 4: CLEAN MODAK & POWER-UP RUN
    // ----------------------------------------------------
    for (let lane of [0, 1, 2]) {
      if (Math.random() < 0.78) {
        spawnLaneItem(lane, spawnZ);
      }
    }
  }

  function spawnGadaItem(lane, z) {
    const mesh = createGadaPickup();
    mesh.position.set(LANES[lane], 0.35, z);
    scene.add(mesh);

    activeCollectibles.push({
      type: 'gada',
      mesh: mesh,
      lane: lane,
      baseY: 0.35,
      isSkyItem: false,
      hoverOffset: Math.random() * Math.PI
    });
  }

  function spawnSneakersItem(lane, z) {
    const mesh = createSneakersPickup();
    mesh.position.set(LANES[lane], 0.35, z);
    scene.add(mesh);

    activeCollectibles.push({
      type: 'sneakers',
      mesh: mesh,
      lane: lane,
      baseY: 0.35,
      isSkyItem: false,
      hoverOffset: Math.random() * Math.PI
    });
  }

  function spawnMagnetItem(lane, z) {
    const mesh = createMagnetPickup();
    mesh.position.set(LANES[lane], 0.35, z);
    scene.add(mesh);

    activeCollectibles.push({
      type: 'magnet',
      mesh: mesh,
      lane: lane,
      baseY: 0.35,
      isSkyItem: false,
      hoverOffset: Math.random() * Math.PI
    });
  }

  function spawnLaneItem(lane, z) {
    // Enforce strict 350m minimum distance between spawned power-ups
    if (canSpawnPowerup()) {
      recordPowerupSpawn();
      const pRand = Math.random();
      let type, mesh;

      if (pRand < 0.25) {
        type = 'gada';
        mesh = createGadaPickup();
      } else if (pRand < 0.50) {
        type = 'sneakers';
        mesh = createSneakersPickup();
      } else if (pRand < 0.70) {
        type = 'magnet';
        mesh = createMagnetPickup();
      } else if (pRand < 0.85) {
        type = 'jetpack';
        mesh = createJetpackPickup();
      } else {
        type = 'multiplier';
        mesh = createMultiplierPickup();
      }

      mesh.position.set(LANES[lane], 0.35, z);
      scene.add(mesh);

      activeCollectibles.push({
        type: type,
        mesh: mesh,
        lane: lane,
        baseY: 0.35,
        isSkyItem: false,
        hoverOffset: Math.random() * Math.PI
      });
    } else {
      // Standard Modak coin line
      for (let offset = -2.5; offset <= 2.5; offset += 2.5) {
        const modakMesh = createModakModel();
        modakMesh.position.set(LANES[lane], 0.3, z + offset);
        scene.add(modakMesh);

        activeCollectibles.push({
          type: 'modak',
          mesh: modakMesh,
          lane: lane,
          baseY: 0.3,
          isSkyItem: false,
          hoverOffset: offset
        });
      }
    }
  }

  // ==========================================
  // PARTICLE FX & DIVINE AURA
  // ==========================================
  function createPopParticles(position, color, count = 16, spread = 6) {
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = [];

    for (let i = 0; i < count; i++) {
      positions[i * 3 + 0] = position.x;
      positions[i * 3 + 1] = position.y + 0.4;
      positions[i * 3 + 2] = position.z;
      velocities.push(
        new THREE.Vector3(
          (Math.random() - 0.5) * spread,
          Math.random() * spread + 2,
          (Math.random() - 0.5) * spread
        )
      );
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({ color: color, size: 0.28, transparent: true, opacity: 1 });
    const pSystem = new THREE.Points(geo, mat);
    scene.add(pSystem);

    activeParticles.push({ system: pSystem, velocities: velocities, life: 0.5, maxLife: 0.5 });
  }

  function createDivineSacredParticles(position, count = 45) {
    const geo = new THREE.BufferGeometry();
    const positions = new Float32Array(count * 3);
    const velocities = [];

    for (let i = 0; i < count; i++) {
      const angle = (i / count) * Math.PI * 2 + Math.random() * 0.5;
      const radius = 0.8 + Math.random() * 1.2;
      positions[i * 3 + 0] = position.x + Math.cos(angle) * radius;
      positions[i * 3 + 1] = position.y + (Math.random() - 0.2) * 1.5;
      positions[i * 3 + 2] = position.z + Math.sin(angle) * radius;

      velocities.push(
        new THREE.Vector3(
          -Math.sin(angle) * 1.5 + (Math.random() - 0.5) * 0.5,
          Math.random() * 2.5 + 1.8,
          Math.cos(angle) * 1.5 + (Math.random() - 0.5) * 0.5
        )
      );
    }

    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    const mat = new THREE.PointsMaterial({
      color: 0xfef08a,
      size: 0.32,
      transparent: true,
      opacity: 0.95
    });
    const pSystem = new THREE.Points(geo, mat);
    scene.add(pSystem);

    activeParticles.push({ system: pSystem, velocities: velocities, life: 1.8, maxLife: 1.8 });
  }

  function updateParticles(delta) {
    for (let i = activeParticles.length - 1; i >= 0; i--) {
      const p = activeParticles[i];
      p.life -= delta;
      if (p.life <= 0) {
        scene.remove(p.system);
        p.system.geometry.dispose();
        p.system.material.dispose();
        activeParticles.splice(i, 1);
        continue;
      }
      const positions = p.system.geometry.attributes.position.array;
      for (let j = 0; j < p.velocities.length; j++) {
        p.velocities[j].y -= 8 * delta;
        positions[j * 3 + 0] += p.velocities[j].x * delta;
        positions[j * 3 + 1] += p.velocities[j].y * delta;
        positions[j * 3 + 2] += p.velocities[j].z * delta;
      }
      p.system.geometry.attributes.position.needsUpdate = true;
      p.system.material.opacity = p.life / p.maxLife;
    }
  }

  // ==========================================
  // INPUT CONTROLS & ACTIVATION
  // ==========================================
  function moveLeft() {
    if (gameState !== STATE.PLAYING) return;
    if (currentLane > LANE_LEFT) {
      currentLane--;
      targetX = LANES[currentLane];
      playTone(320, 'sine', 0.08, 0.06);
    }
  }

  function moveRight() {
    if (gameState !== STATE.PLAYING) return;
    if (currentLane < LANE_RIGHT) {
      currentLane++;
      targetX = LANES[currentLane];
      playTone(320, 'sine', 0.08, 0.06);
    }
  }

  function jump() {
    if (gameState !== STATE.PLAYING) return;
    if (isJetpackActive) return;

    if (isGrounded && !isJumping) {
      isJumping = true;
      isGrounded = false;
      isSliding = false; // Jumping cancels active slide
      slideTimer = 0;
      queuedSlide = false;
      playerVelocityY = isSneakersActive ? SNEAKERS_JUMP_FORCE : NORMAL_JUMP_FORCE;
      playJumpSound();

      if (isSneakersActive) {
        isSneakersFlipping = true;
        sneakersFlipAngle = 0;
        createPopParticles(playerGroup.position, 0xf97316, 20, 8);
      } else {
        isSneakersFlipping = false;
        sneakersFlipAngle = 0;
      }
    }
  }

  function startSlide() {
    if (gameState !== STATE.PLAYING || isJetpackActive) return;
    isSliding = true;
    slideTimer = SLIDE_DURATION;
    playSlideSound();
    createPopParticles(
      new THREE.Vector3(playerGroup.position.x, currentBaseY + 0.1, playerGroup.position.z),
      0xe2e8f0,
      10,
      2.5
    );
  }

  function fastDropOrSlide() {
    if (gameState !== STATE.PLAYING || isJetpackActive) return;
    if (!isGrounded) {
      // In mid-air: slam down immediately and queue slide upon landing
      playerVelocityY = -38.0;
      queuedSlide = true;
      playTone(180, 'sine', 0.1, 0.08);
    } else {
      // On ground or roof: initiate roll/slide!
      startSlide();
    }
  }

  let activeMooshikanMesh = null;

  function activateMooshikanBoard() {
    if (gameState !== STATE.PLAYING) return;
    if (isBoardActive) return;

    if (boardsRemaining <= 0) {
      playErrorBuzzer();
      if (shieldPill) {
        shieldPill.classList.remove('error-shake');
        void shieldPill.offsetWidth;
        shieldPill.classList.add('error-shake');
      }
      showToast('No Mooshikan Boards! Visit the Shop 🛒 to buy more.');
      return;
    }

    boardsRemaining = Math.max(0, boardsRemaining - 1);
    StorageManager.saveMooshikanBoards(boardsRemaining);

    isBoardActive = true;
    boardTimer = BOARD_DURATION;

    // Attach custom 3D Mooshikan hoverboard directly beneath player's mesh
    if (assets.mooshikan) {
      if (activeMooshikanMesh) {
        playerGroup.remove(activeMooshikanMesh);
      }
      activeMooshikanMesh = assets.mooshikan.clone(true);
      activeMooshikanMesh.scale.set(0.95, 0.95, 0.95);
      activeMooshikanMesh.position.set(0, 0.08, 0.05);
      activeMooshikanMesh.traverse((child) => {
        if (child.isMesh) {
          child.castShadow = true;
          child.receiveShadow = true;
        }
      });
      playerGroup.add(activeMooshikanMesh);
      skateboardGroup.visible = false;
    } else {
      skateboardGroup.visible = true;
    }

    playBoardDeploySound();
    createPopParticles(playerGroup.position, 0x00f5ff, 24, 6);
    updateHUD();
  }

  function removeMooshikanBoard() {
    isBoardActive = false;
    if (activeMooshikanMesh) {
      playerGroup.remove(activeMooshikanMesh);
      activeMooshikanMesh = null;
    }
    skateboardGroup.visible = false;
  }

  // ==========================================
  // INPUT CONTROLS (NATIVE KEYBOARD & TOUCH SWIPE)
  // ==========================================

  // Keyboard Event Listeners
  // Keyboard Event Listeners
  window.addEventListener('keydown', (e) => {
    initAudio();

    // Close shop on Escape if open
    if (e.code === 'Escape' && shopOverlay && !shopOverlay.classList.contains('hidden')) {
      e.preventDefault();
      closeShop();
      return;
    }

    // Pause toggle hotkeys (Esc or P)
    if (e.code === 'KeyP' || e.code === 'Escape') {
      e.preventDefault();
      togglePause();
      return;
    }

    // Ignore game controls while shop modal is open
    if (shopOverlay && !shopOverlay.classList.contains('hidden')) {
      return;
    }

    if (gameState === STATE.MENU || gameState === STATE.GAMEOVER) {
      if (e.code === 'Space' || e.code === 'Enter' || e.code === 'ArrowUp' || e.code === 'KeyW') {
        e.preventDefault();
        startGame();
        return;
      }
    }

    if (gameState !== STATE.PLAYING) return;

    if (e.code === 'ArrowLeft' || e.code === 'KeyA') {
      moveLeft();
    } else if (e.code === 'ArrowRight' || e.code === 'KeyD') {
      moveRight();
    } else if (e.code === 'ArrowDown' || e.code === 'KeyS') {
      e.preventDefault();
      fastDropOrSlide();
    } else if (e.code === 'KeyB') {
      activateMooshikanBoard();
    } else if (e.code === 'Space' || e.code === 'ArrowUp' || e.code === 'KeyW') {
      e.preventDefault();

      if (e.code === 'Space') {
        const now = performance.now();
        if (now - lastSpacePressTime < 340) {
          activateMooshikanBoard();
        }
        lastSpacePressTime = now;
      }
      jump();
    }
  });

  // Touch & Swipe Event Listeners
  let touchStartX = 0;
  let touchStartY = 0;
  let touchStartTime = 0;
  let lastTapReleaseTime = 0;

  window.addEventListener('touchstart', (e) => {
    initAudio();

    if (e.touches.length > 0) {
      touchStartX = e.touches[0].clientX;
      touchStartY = e.touches[0].clientY;
      touchStartTime = performance.now();
    }
  }, { passive: true });

  window.addEventListener('touchend', (e) => {
    if (shopOverlay && !shopOverlay.classList.contains('hidden')) {
      return;
    }

    if (gameState === STATE.MENU || gameState === STATE.GAMEOVER) {
      startGame();
      return;
    }

    if (e.changedTouches.length > 0) {
      const deltaX = e.changedTouches[0].clientX - touchStartX;
      const deltaY = e.changedTouches[0].clientY - touchStartY;
      const absX = Math.abs(deltaX);
      const absY = Math.abs(deltaY);
      const elapsed = performance.now() - touchStartTime;
      const now = performance.now();

      // Detect quick double-tap (tap with little movement within 340ms of last tap)
      if (absX < 20 && absY < 20 && elapsed < 300) {
        if (now - lastTapReleaseTime < 340) {
          activateMooshikanBoard();
          lastTapReleaseTime = 0;
          return;
        }
        lastTapReleaseTime = now;
        return;
      }

      // Swipe gestures
      if (Math.max(absX, absY) > 28) {
        if (absX > absY) {
          if (deltaX > 0) moveRight();
          else moveLeft();
        } else {
          if (deltaY < 0) jump();
          else if (deltaY > 0) fastDropOrSlide();
        }
      }
    }
  }, { passive: true });

  // Canvas click / pointer down to start or restart
  window.addEventListener('pointerdown', (e) => {
    // Ignore clicks on HUD interactive buttons (like sound toggle, pause, shop, shield) or modals
    if (e.target && (e.target.closest('#sound-btn') || e.target.closest('#pause-btn') || e.target.closest('#shop-btn') || e.target.closest('.modal-overlay') || e.target.closest('.hud-pill-shield'))) {
      return;
    }
    if (shopOverlay && !shopOverlay.classList.contains('hidden')) {
      return;
    }
    initAudio();
    if (gameState === STATE.MENU || gameState === STATE.GAMEOVER) {
      startGame();
    }
  });

  // ==========================================
  // UI & STATE MANAGEMENT
  // ==========================================
  const modakScoreEl = document.getElementById('modak-score');
  const runModakScoreEl = document.getElementById('run-modak-score');
  const bestModakScoreEl = document.getElementById('best-modak-score');
  const ecoScoreEl = document.getElementById('eco-score');
  const bestEcoScoreEl = document.getElementById('best-eco-score');
  const boardsCountEl = document.getElementById('boards-count');
  const hudBuyBoardBtn = document.getElementById('hud-buy-board-btn');
  const hudMultBadge = document.getElementById('hud-mult-badge');
  const soundBtn = document.getElementById('sound-btn');
  const controlsHint = document.getElementById('controls-hint');

  const hudJetpack = document.getElementById('hud-jetpack');
  const jetpackTimeEl = document.getElementById('jetpack-time');
  const jetpackBar = document.getElementById('jetpack-bar');

  const hudSneakers = document.getElementById('hud-sneakers');
  const sneakersTimeEl = document.getElementById('sneakers-time');
  const sneakersBar = document.getElementById('sneakers-bar');

  const hudMagnet = document.getElementById('hud-magnet');
  const magnetTimeEl = document.getElementById('magnet-time');
  const magnetBar = document.getElementById('magnet-bar');

  const hudMultiplier = document.getElementById('hud-multiplier');
  const multiplierTimeEl = document.getElementById('multiplier-time');
  const multiplierBar = document.getElementById('multiplier-bar');

  const hudGada = document.getElementById('hud-gada');
  const gadaTimeEl = document.getElementById('gada-time');
  const gadaBar = document.getElementById('gada-bar');

  const shieldPill = document.querySelector('.hud-pill-shield');
  if (shieldPill) {
    shieldPill.addEventListener('click', (e) => {
      // Prevent shield activation if clicking the quick-buy button
      if (e.target && e.target.closest('#hud-buy-board-btn')) {
        return;
      }
      e.stopPropagation();
      activateMooshikanBoard();
    });
  }

  if (hudBuyBoardBtn) {
    hudBuyBoardBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      purchaseBoards(1, 30);
    });
  }

  if (soundBtn) {
    soundBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      initAudio();
      soundEnabled = !soundEnabled;
      soundBtn.textContent = soundEnabled ? '🔊' : '🔇';
      soundBtn.classList.toggle('muted', !soundEnabled);
    });
  }

  // Pause and Game Over UI Elements
  const pauseBtn = document.getElementById('pause-btn');
  const pauseOverlay = document.getElementById('pause-overlay');
  const pauseModaks = document.getElementById('pause-modaks');
  const pauseDistance = document.getElementById('pause-distance');
  const resumeBtn = document.getElementById('resume-btn');
  const pauseRestartBtn = document.getElementById('pause-restart-btn');

  const gameoverOverlay = document.getElementById('gameover-overlay');
  const gameoverModaks = document.getElementById('gameover-modaks');
  const gameoverBestModaks = document.getElementById('gameover-best-modaks');
  const gameoverEco = document.getElementById('gameover-eco');
  const gameoverDistance = document.getElementById('gameover-distance');
  const gameoverBestDistance = document.getElementById('gameover-best-distance');
  const gameoverLifetimeModaks = document.getElementById('gameover-lifetime-modaks');
  const gameoverRunsPlayed = document.getElementById('gameover-runs-played');
  const playAgainBtn = document.getElementById('play-again-btn');
  const resetStorageBtn = document.getElementById('reset-storage-btn');

  function pauseGame() {
    if (gameState !== STATE.PLAYING) return;
    gameState = STATE.PAUSED;
    if (pauseModaks) pauseModaks.textContent = `${score}`;
    if (pauseDistance) pauseDistance.textContent = `${Math.round(totalDistanceRun)} m`;
    if (pauseOverlay) pauseOverlay.classList.remove('hidden');
  }

  function resumeGame() {
    if (gameState !== STATE.PAUSED) return;
    if (pauseOverlay) pauseOverlay.classList.add('hidden');
    clock.getDelta(); // Clear delta jump so entities don't skip
    gameState = STATE.PLAYING;
  }

  function togglePause() {
    if (gameState === STATE.PLAYING) {
      pauseGame();
    } else if (gameState === STATE.PAUSED) {
      resumeGame();
    }
  }

  if (pauseBtn) {
    pauseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePause();
    });
  }

  if (resumeBtn) {
    resumeBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      resumeGame();
    });
  }

  if (pauseRestartBtn) {
    pauseRestartBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (pauseOverlay) pauseOverlay.classList.add('hidden');
      startGame();
    });
  }

  if (playAgainBtn) {
    playAgainBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      if (gameoverOverlay) gameoverOverlay.classList.add('hidden');
      startGame();
    });
  }

  if (resetStorageBtn) {
    resetStorageBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      const confirmed = window.confirm('Are you sure you want to reset all high scores and lifetime game statistics?');
      if (confirmed) {
        StorageManager.resetAll();
        bestModakScore = 0;
        bestEcoScore = 0;
        boardsRemaining = 3;
        updateHUD();

        if (gameoverBestModaks) gameoverBestModaks.textContent = 'Best: 0';
        if (gameoverBestDistance) gameoverBestDistance.textContent = 'Best: 0 m';
        if (gameoverLifetimeModaks) gameoverLifetimeModaks.textContent = '0';
        if (gameoverRunsPlayed) gameoverRunsPlayed.textContent = '0';
        console.log('Game progress and high scores successfully reset.');
        updateShopUI();
      }
    });
  }

  // ==========================================
  // IN-GAME STORE & ECONOMY SYSTEM (MOOSHIKAN WORKSHOP)
  // ==========================================
  const shopBtn = document.getElementById('shop-btn');
  const pauseShopBtn = document.getElementById('pause-shop-btn');
  const gameoverShopBtn = document.getElementById('gameover-shop-btn');
  const shopCloseBtn = document.getElementById('shop-close-btn');
  const shopOverlay = document.getElementById('shop-overlay');
  const shopModakBalance = document.getElementById('shop-modak-balance');
  const shopBoardCount = document.getElementById('shop-board-count');
  const buyBoard1 = document.getElementById('buy-board-1');
  const buyBoard3 = document.getElementById('buy-board-3');
  const buyBoard5 = document.getElementById('buy-board-5');

  let toastTimeout = null;
  function showToast(msg, duration = 2400, isError = false) {
    const toast = document.getElementById('toast-notification');
    if (!toast) return;
    toast.textContent = msg;
    if (isError) {
      toast.classList.add('error');
    } else {
      toast.classList.remove('error');
    }
    toast.classList.remove('hidden');
    if (toastTimeout) clearTimeout(toastTimeout);
    toastTimeout = setTimeout(() => {
      toast.classList.add('hidden');
      toast.classList.remove('error');
    }, duration);
  }

  function updateShopUI() {
    const totalModaks = StorageManager.getTotalModaks();
    const currentBoards = StorageManager.getMooshikanBoards(3);

    if (shopModakBalance) shopModakBalance.textContent = `${totalModaks}`;
    if (shopBoardCount) shopBoardCount.textContent = `${currentBoards}`;

    const packages = [
      { btn: buyBoard1, qty: 1, cost: 30, baseLabel: 'Buy 1' },
      { btn: buyBoard3, qty: 3, cost: 75, baseLabel: 'Buy 3' },
      { btn: buyBoard5, qty: 5, cost: 110, baseLabel: 'Buy 5' }
    ];

    packages.forEach(pkg => {
      if (!pkg.btn) return;
      const labelSpan = pkg.btn.querySelector('.buy-label');
      // Do NOT disable so user clicks can trigger the "Not enough Modaks!" notification/alert
      pkg.btn.disabled = false;
      if (totalModaks >= pkg.cost) {
        pkg.btn.classList.remove('cant-afford');
        if (labelSpan) labelSpan.textContent = pkg.baseLabel;
      } else {
        pkg.btn.classList.add('cant-afford');
        const diff = pkg.cost - totalModaks;
        if (labelSpan) labelSpan.textContent = `Need ${diff} 🟡`;
      }
    });
  }

  function openShop() {
    if (gameState === STATE.PLAYING) {
      pauseGame();
    }
    updateShopUI();
    if (shopOverlay) shopOverlay.classList.remove('hidden');
  }

  function closeShop() {
    if (shopOverlay) shopOverlay.classList.add('hidden');
  }

  function purchaseBoards(quantity, cost) {
    const totalModaks = StorageManager.getTotalModaks();
    if (totalModaks < cost) {
      playErrorBuzzer();
      showToast('Not enough Modaks!', 2500, true);
      return;
    }

    const newModaks = totalModaks - cost;
    StorageManager.saveTotalModaks(newModaks);

    const currentBoards = StorageManager.getMooshikanBoards(3);
    const newBoards = currentBoards + quantity;
    StorageManager.saveMooshikanBoards(newBoards);
    boardsRemaining = newBoards;

    updateHUD();
    updateShopUI();
    playPurchaseSound();
    showToast(`🎉 Summoned ${quantity} Mooshikan Board${quantity > 1 ? 's' : ''}!`);
  }

  if (shopBtn) {
    shopBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openShop();
    });
  }

  if (pauseShopBtn) {
    pauseShopBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openShop();
    });
  }

  if (gameoverShopBtn) {
    gameoverShopBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      openShop();
    });
  }

  if (shopCloseBtn) {
    shopCloseBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      closeShop();
    });
  }

  if (shopOverlay) {
    shopOverlay.addEventListener('click', (e) => {
      if (e.target === shopOverlay) {
        closeShop();
      }
    });
  }

  if (buyBoard1) {
    buyBoard1.addEventListener('click', (e) => {
      e.stopPropagation();
      purchaseBoards(1, 30);
    });
  }

  if (buyBoard3) {
    buyBoard3.addEventListener('click', (e) => {
      e.stopPropagation();
      purchaseBoards(3, 75);
    });
  }

  if (buyBoard5) {
    buyBoard5.addEventListener('click', (e) => {
      e.stopPropagation();
      purchaseBoards(5, 110);
    });
  }

  function updateHUD() {
    if (modakScoreEl) modakScoreEl.textContent = `${StorageManager.getTotalModaks()}`;
    if (runModakScoreEl) runModakScoreEl.textContent = `${score}`;
    if (bestModakScoreEl) bestModakScoreEl.textContent = `${bestModakScore}`;
    if (ecoScoreEl) ecoScoreEl.textContent = `${Math.round(totalDistanceRun)}`;
    if (bestEcoScoreEl) bestEcoScoreEl.textContent = `${bestEcoScore}`;
    if (boardsCountEl) boardsCountEl.textContent = `${boardsRemaining}`;

    if (hudMultBadge) {
      hudMultBadge.classList.toggle('hidden', !isMultiplierActive);
    }

    if (hudJetpack) {
      const active = isJetpackActive && !isJetpackDescending;
      hudJetpack.classList.toggle('active', active);
      if (active) {
        if (jetpackTimeEl) jetpackTimeEl.textContent = `${jetpackTimer.toFixed(1)}s`;
        if (jetpackBar) jetpackBar.style.width = `${Math.max(0, (jetpackTimer / JETPACK_DURATION) * 100)}%`;
      }
    }

    if (hudSneakers) {
      hudSneakers.classList.toggle('active', isSneakersActive);
      if (isSneakersActive) {
        if (sneakersTimeEl) sneakersTimeEl.textContent = `${sneakersTimer.toFixed(1)}s`;
        if (sneakersBar) sneakersBar.style.width = `${Math.max(0, (sneakersTimer / SNEAKERS_DURATION) * 100)}%`;
      }
    }

    if (hudMagnet) {
      hudMagnet.classList.toggle('active', isMagnetActive);
      if (isMagnetActive) {
        if (magnetTimeEl) magnetTimeEl.textContent = `${magnetTimer.toFixed(1)}s`;
        if (magnetBar) magnetBar.style.width = `${Math.max(0, (magnetTimer / MAGNET_DURATION) * 100)}%`;
      }
    }

    if (hudMultiplier) {
      hudMultiplier.classList.toggle('active', isMultiplierActive);
      if (isMultiplierActive) {
        if (multiplierTimeEl) multiplierTimeEl.textContent = `${multiplierTimer.toFixed(1)}s`;
        if (multiplierBar) multiplierBar.style.width = `${Math.max(0, (multiplierTimer / MULTIPLIER_DURATION) * 100)}%`;
      }
    }

    if (hudGada) {
      hudGada.classList.toggle('active', isGadaActive);
      if (isGadaActive) {
        if (gadaTimeEl) gadaTimeEl.textContent = `${gadaTimer.toFixed(1)}s`;
        if (gadaBar) gadaBar.style.width = `${Math.max(0, (gadaTimer / GADA_DURATION) * 100)}%`;
      }
    }
  }

  // Populate HUD immediately on page startup with persisted stats
  updateHUD();

  function startDivineAscent() {
    gameState = STATE.DIVINE_ASCENT;
    gameSpeed = 0;
    divineAscentTimer = 0;

    playSacredTempleBell();

    removeMooshikanBoard();
    isJetpackActive = false;
    isJetpackDescending = false;
    isSneakersActive = false;
    isMagnetActive = false;
    isMultiplierActive = false;
    jetpackGroup.visible = false;
    sneakersGroup.visible = false;
    magnetAuraGroup.visible = false;

    playerGroup.rotation.set(0, 0, 0);

    const auraGeo = new THREE.TorusGeometry(1.6, 0.08, 16, 32);
    const auraMat = new THREE.MeshStandardMaterial({
      color: 0xf59e0b,
      emissive: 0xfbbf24,
      emissiveIntensity: 0.9,
      transparent: true,
      opacity: 0.95
    });
    divineAuraMesh = new THREE.Mesh(auraGeo, auraMat);
    divineAuraMesh.rotation.x = Math.PI / 2;
    divineAuraMesh.position.set(playerGroup.position.x, playerGroup.position.y + 0.8, playerGroup.position.z);
    scene.add(divineAuraMesh);

    const sphereGeo = new THREE.SphereGeometry(1.55, 24, 24);
    const sphereMat = new THREE.MeshStandardMaterial({
      color: 0xfef08a,
      emissive: 0xfde047,
      emissiveIntensity: 0.5,
      transparent: true,
      opacity: 0.45,
      depthWrite: false
    });
    divineSphereMesh = new THREE.Mesh(sphereGeo, sphereMat);
    divineSphereMesh.position.set(playerGroup.position.x, playerGroup.position.y + 0.8, playerGroup.position.z);
    scene.add(divineSphereMesh);

    createDivineSacredParticles(playerGroup.position, 55);
    createPopParticles(playerGroup.position, 0xfbbf24, 25, 4);

    const finalDist = Math.round(totalDistanceRun);
    const saveResult = StorageManager.recordGameOver(score, finalDist, boardsRemaining);
    bestModakScore = saveResult.bestModakScore;
    bestEcoScore = saveResult.bestEcoScore;

    updateHUD();
  }

  function finishDivineAscent() {
    gameState = STATE.GAMEOVER;

    if (divineAuraMesh) {
      scene.remove(divineAuraMesh);
      divineAuraMesh.geometry.dispose();
      divineAuraMesh.material.dispose();
      divineAuraMesh = null;
    }
    if (divineSphereMesh) {
      scene.remove(divineSphereMesh);
      divineSphereMesh.geometry.dispose();
      divineSphereMesh.material.dispose();
      divineSphereMesh = null;
    }

    // Populate and display glassmorphic AAA Game Over screen
    const finalDist = Math.round(totalDistanceRun);
    if (gameoverModaks) gameoverModaks.textContent = `${score}`;
    if (gameoverBestModaks) gameoverBestModaks.textContent = `Best: ${bestModakScore}`;
    if (gameoverEco) gameoverEco.textContent = `${Math.round(finalDist * 1.5 + score * 10)}`;
    if (gameoverDistance) gameoverDistance.textContent = `${finalDist} m`;
    if (gameoverBestDistance) gameoverBestDistance.textContent = `Best: ${bestEcoScore} m`;

    const stats = StorageManager.getAllStats();
    if (gameoverLifetimeModaks) gameoverLifetimeModaks.textContent = `${stats.totalModaksCollected}`;
    if (gameoverRunsPlayed) gameoverRunsPlayed.textContent = `${stats.gamesPlayed}`;

    if (gameoverOverlay) gameoverOverlay.classList.remove('hidden');
  }

  function startGame() {
    if (gameState === STATE.LOADING || !assetsLoaded) {
      console.log('Assets still loading, please wait...');
      return;
    }
    initAudio();
    resetGame();
    gameState = STATE.PLAYING;
    if (controlsHint) controlsHint.classList.remove('faded');
    updateHUD();
  }

  function resetGame() {
    score = 0;
    totalDistanceRun = 0;
    boardsRemaining = StorageManager.getMooshikanBoards(3);
    gameSpeed = BASE_SPEED;

    isJetpackActive = false;
    isJetpackDescending = false;
    jetpackTimer = 0;
    jetpackSkyLane = LANE_CENTER;
    isSneakersActive = false;
    sneakersTimer = 0;
    isMagnetActive = false;
    magnetTimer = 0;
    isMultiplierActive = false;
    multiplierTimer = 0;
    isBoardActive = false;
    boardTimer = 0;
    isGadaActive = false;
    gadaTimer = 0;
    if (activeGadaMesh) {
      playerGroup.remove(activeGadaMesh);
      activeGadaMesh = null;
    }
    lastPowerupSpawnDistance = -200.0;
    cameraShakeTimer = 0;
    isInvincible = false;
    invincibleTimer = 0;
    divineAscentTimer = 0;

    isSneakersFlipping = false;
    sneakersFlipAngle = 0;

    if (pauseOverlay) pauseOverlay.classList.add('hidden');
    if (gameoverOverlay) gameoverOverlay.classList.add('hidden');
    if (shopOverlay) shopOverlay.classList.add('hidden');

    currentSkyFactor = 0.0;
    camera.fov = 60.0;
    camera.updateProjectionMatrix();

    currentLane = LANE_CENTER;
    targetX = LANES[LANE_CENTER];
    playerY = 0;
    playerVelocityY = 0;
    currentBaseY = 0;
    isGrounded = true;
    isJumping = false;
    isSliding = false;
    slideTimer = 0;
    queuedSlide = false;
    spawnTimer = 0;
    overbridgeTimer = 0;
    scenerySpawnTimer = 0;

    playerPitchX = 0;
    playerRollZ = 0;
    playerBobY = 0;

    removeMooshikanBoard();
    jetpackGroup.visible = false;
    sneakersGroup.visible = false;
    magnetAuraGroup.visible = false;

    playerGroup.position.set(0, 0, 0);
    playerGroup.rotation.set(0, 0, 0);
    playerMesh.rotation.set(0, 0, 0);
    playerMesh.scale.set(1, 1, 1);
    crown.scale.set(1, 1, 1);
    crown.position.set(0, 1.45, 0);
    visor.position.set(0, 0.8, -0.6);
    playerMesh.material.opacity = 1.0;
    playerMesh.material.transparent = false;
    crown.material.opacity = 1.0;
    visor.material.opacity = 1.0;
    if (ganeshaModelInstance) {
      playerMesh.visible = false;
      crown.visible = false;
      visor.visible = false;
      ganeshaModelInstance.scale.set(1, 1, 1);
      ganeshaModelInstance.position.set(0, 0, 0);
      setGaneshaOpacity(1.0);
    }

    villainCurrentLane = LANE_CENTER;
    villainTargetX = 0;
    villainGroup.position.set(0, 0, -VILLAIN_LEAD_DISTANCE);

    for (let obs of activeObstacles) scene.remove(obs.mesh);
    activeObstacles.length = 0;

    for (let col of activeCollectibles) scene.remove(col.mesh);
    activeCollectibles.length = 0;

    for (let ob of activeOverbridges) scene.remove(ob.mesh);
    activeOverbridges.length = 0;

    for (let sc of activeScenery) scene.remove(sc.mesh);
    activeScenery.length = 0;

    for (let p of activeParticles) scene.remove(p.system);
    activeParticles.length = 0;

    if (divineAuraMesh) { scene.remove(divineAuraMesh); divineAuraMesh = null; }
    if (divineSphereMesh) { scene.remove(divineSphereMesh); divineSphereMesh = null; }

    updateHUD();
  }

  // ==========================================
  // MAIN ANIMATION LOOP & PHYSICS
  // ==========================================
  const clock = new THREE.Clock();

  function animate() {
    requestAnimationFrame(animate);

    // Freeze render frame when paused (AAA mobile pause feel)
    if (gameState === STATE.PAUSED) {
      renderer.render(scene, camera);
      return;
    }

    const delta = Math.min(clock.getDelta(), 0.1);
    const time = clock.getElapsedTime();
    updateSnow(delta);

    // Update in-canvas pulsating text overlay
    renderCanvasOverlay(time);

    // ------------------------------------------
    // STATE: RESPECTFUL DIVINE ASCENT (GAME OVER)
    // ------------------------------------------
    if (gameState === STATE.DIVINE_ASCENT) {
      divineAscentTimer += delta;

      playerGroup.position.y += 0.35 * delta;

      if (divineAuraMesh) {
        divineAuraMesh.rotation.z += 1.8 * delta;
        divineAuraMesh.position.y = playerGroup.position.y + 0.8;
      }
      if (divineSphereMesh) {
        divineSphereMesh.position.y = playerGroup.position.y + 0.8;
        const scalePulse = 1.0 + Math.sin(time * 5) * 0.08;
        divineSphereMesh.scale.set(scalePulse, scalePulse, scalePulse);
      }

      const fade = Math.max(0, 1.0 - divineAscentTimer / 1.6);
      playerMesh.material.transparent = true;
      playerMesh.material.opacity = fade;
      crown.material.opacity = fade;
      visor.material.opacity = fade;
      if (ganeshaModelInstance) {
        setGaneshaOpacity(fade);
      }

      if (divineAscentTimer >= 1.8) {
        finishDivineAscent();
      }

      updateParticles(delta);
      renderer.render(scene, camera);
      return;
    }

    // ------------------------------------------
    // STATE: ACTIVE PLAYING
    // ------------------------------------------
    if (gameState === STATE.PLAYING) {
      // Soft progressive difficulty curve: gentle, controllable acceleration over distance and Modaks
      gameSpeed = THREE.MathUtils.clamp(BASE_SPEED + (totalDistanceRun * 0.0020) + (score * 0.012), BASE_SPEED, MAX_SPEED);
      totalDistanceRun += gameSpeed * delta;

      const currentDist = Math.round(totalDistanceRun);
      if (currentDist > bestEcoScore) {
        bestEcoScore = currentDist;
        StorageManager.saveBestEcoScore(bestEcoScore);
      }

      if (totalDistanceRun > 50 && controlsHint && !controlsHint.classList.contains('faded')) {
        controlsHint.classList.add('faded');
      }

      // ----------------------------------------
      // POWER-UP TIMERS & SMOOTH JETPACK DESCENT
      // ----------------------------------------
      if (isJetpackActive) {
        if (!isJetpackDescending) {
          jetpackTimer -= delta;
          if (jetpackTimer <= 0) {
            isJetpackDescending = true;
            isInvincible = true;
            invincibleTimer = 2.5;
          } else {
            if (Math.random() < 0.6) {
              for (let side of [-0.35, 0.35]) {
                createPopParticles(
                  new THREE.Vector3(playerGroup.position.x + side, playerGroup.position.y + 0.2, playerGroup.position.z + 0.75),
                  0x00f5ff,
                  3,
                  2
                );
              }
            }
          }
        } else {
          // Descent handled smoothly in gravity / lerp block below
        }
      }

      if (isSneakersActive) {
        sneakersTimer -= delta;
        if (sneakersTimer <= 0) {
          isSneakersActive = false;
          sneakersGroup.visible = false;
        }
      }

      // The Magnet timer & character visual rotation
      if (isMagnetActive) {
        magnetTimer -= delta;
        if (magnetTimer <= 0) {
          isMagnetActive = false;
          magnetAuraGroup.visible = false;
        } else {
          magnetAuraGroup.visible = true;
          magnetAuraGroup.rotation.y += 3.5 * delta;
          magRing1.rotation.z += 2.0 * delta;
          magRing2.rotation.z -= 2.0 * delta;

          // Gentle magnetic spark
          if (Math.random() < 0.25) {
            createPopParticles(
              new THREE.Vector3(playerGroup.position.x + (Math.random() - 0.5) * 1.5, playerGroup.position.y + 0.6, playerGroup.position.z),
              0x38bdf8,
              2,
              1.2
            );
          }
        }
      }

      if (isMultiplierActive) {
        multiplierTimer -= delta;
        if (multiplierTimer <= 0) {
          isMultiplierActive = false;
        }
      }

      if (isBoardActive) {
        boardTimer -= delta;
        if (boardTimer <= 0) {
          removeMooshikanBoard();
        } else {
          for (let w of skateboardWheels) {
            w.rotation.x += gameSpeed * delta * 6;
          }
        }
      }

      if (isGadaActive) {
        gadaTimer -= delta;
        if (activeGadaMesh) {
          // Dynamic combat ready swing sway
          activeGadaMesh.rotation.z = -Math.PI / 4 + Math.sin(time * 10) * 0.15;
          activeGadaMesh.rotation.x = Math.PI / 8 + Math.sin(time * 6) * 0.12;
          // Golden sparkle trail behind Gada
          if (Math.random() < 0.3) {
            createPopParticles(
              new THREE.Vector3(playerGroup.position.x + 0.72, playerGroup.position.y + 0.95, playerGroup.position.z),
              0xfbbf24,
              2,
              1.2
            );
          }
        }
        if (gadaTimer <= 0) {
          isGadaActive = false;
          gadaTimer = 0;
          if (activeGadaMesh) {
            playerGroup.remove(activeGadaMesh);
            activeGadaMesh = null;
          }
        }
      }

      // Slide / Roll timer and particle effects
      if (isSliding) {
        slideTimer -= delta;
        if (slideTimer <= 0 || isJetpackActive) {
          isSliding = false;
          slideTimer = 0;
        } else {
          if (Math.random() < 0.45) {
            createPopParticles(
              new THREE.Vector3(playerGroup.position.x + (Math.random() - 0.5) * 0.5, currentBaseY + 0.08, playerGroup.position.z + 0.6),
              0xd1d5db,
              2,
              1.2
            );
          }
        }
      }

      if (isInvincible) {
        invincibleTimer -= delta;
        playerMesh.material.transparent = true;
        playerMesh.material.opacity = Math.sin(time * 30) > 0 ? 0.35 : 0.9;
        if (ganeshaModelInstance) {
          setGaneshaOpacity(Math.sin(time * 30) > 0 ? 0.4 : 1.0);
        }
        if (invincibleTimer <= 0) {
          isInvincible = false;
          playerMesh.material.transparent = false;
          playerMesh.material.opacity = 1.0;
          if (ganeshaModelInstance) {
            setGaneshaOpacity(1.0);
          }
        }
      }

      updateHUD();

      // ----------------------------------------
      // PLAYER LATERAL LERP & ROLL
      // ----------------------------------------
      playerGroup.position.x = THREE.MathUtils.lerp(playerGroup.position.x, targetX, 16.0 * delta);
      const laneDelta = targetX - playerGroup.position.x;
      playerRollZ = THREE.MathUtils.lerp(playerRollZ, -laneDelta * 0.08, 12.0 * delta);

      // ----------------------------------------
      // SNAPPY GRAVITY, JETPACK LERP & JUMP ARC PHYSICS
      // ----------------------------------------
      if (isJetpackActive) {
        if (!isJetpackDescending) {
          playerY = THREE.MathUtils.lerp(playerY, JETPACK_Y, 5.5 * delta);
          isGrounded = false;
          isJumping = false;
          isSneakersFlipping = false;
          sneakersFlipAngle = 0;
          playerVelocityY = 0;
          currentBaseY = 0;
        } else {
          // Buttery smooth Jetpack Landing LERP (Never snap or fall through floor!)
          playerY = THREE.MathUtils.lerp(playerY, currentBaseY, 3.5 * delta);
          if (playerY < currentBaseY) playerY = currentBaseY;

          if (Math.abs(playerY - currentBaseY) < 0.12) {
            playerY = currentBaseY;
            playerVelocityY = 0;
            isJetpackActive = false;
            isJetpackDescending = false;
            jetpackGroup.visible = false;
            isGrounded = true;
            isJumping = false;
            isSneakersFlipping = false;
            sneakersFlipAngle = 0;
            playLandingSound();
            createPopParticles(playerGroup.position, 0x00f5ff, 22, 5);
          }
        }
      } else {
        if (!isGrounded) {
          playerVelocityY -= GRAVITY * delta;
          playerY += playerVelocityY * delta;

          if (playerY <= currentBaseY) {
            playerY = currentBaseY;
            playerVelocityY = 0;
            isGrounded = true;
            isJumping = false;
            isSneakersFlipping = false;
            sneakersFlipAngle = 0;
            playLandingSound();

            if (queuedSlide) {
              startSlide();
              queuedSlide = false;
            }
          }
        } else {
          playerY = currentBaseY;
          playerVelocityY = 0;
          isJumping = false;
          isSneakersFlipping = false;
          sneakersFlipAngle = 0;
        }
      }

      playerGroup.position.y = playerY;

      // ----------------------------------------
      // PROCEDURAL POLISH & ANIMATION BLENDING
      // ----------------------------------------
      if (isJetpackActive) {
        playerPitchX = THREE.MathUtils.lerp(playerPitchX, 0.18 + Math.sin(time * 25) * 0.015, 8.0 * delta);
        playerBobY = THREE.MathUtils.lerp(playerBobY, 0.6, 8.0 * delta);
        playerMesh.scale.set(1, 1, 1);
        crown.position.set(0, 1.45, 0);
        crown.scale.set(1, 1, 1);
        visor.position.set(0, 0.8, -0.6);
        if (ganeshaModelInstance) {
          ganeshaModelInstance.scale.set(1, 1, 1);
        }
        if (jetpackGroup.visible) {
          jetpackGroup.scale.set(1, 1, 1);
          jetpackGroup.position.set(0, 0, 0);
        }
      } else if (isSliding) {
        // Belly slide / roll 90-degree forward tilt (Math.PI / 2) under high hurdles
        playerPitchX = THREE.MathUtils.lerp(playerPitchX, Math.PI / 2, 16.0 * delta);
        playerBobY = THREE.MathUtils.lerp(playerBobY, 0.22, 16.0 * delta);
        playerMesh.scale.set(1.22, 0.38, 1.35);
        crown.position.set(0, 0.52, 0.35);
        crown.scale.set(0.65, 0.35, 0.65);
        visor.position.set(0, 0.22, -0.8);
        if (ganeshaModelInstance) {
          ganeshaModelInstance.scale.set(1.15, 0.42, 1.25);
        }
        if (jetpackGroup.visible) {
          jetpackGroup.scale.set(0.8, 0.45, 0.8);
          jetpackGroup.position.set(0, -0.22, 0);
        }
      } else if (!isGrounded) {
        // 360-degree acrobatic front-flip when leaping with Super Sneakers
        if (isSneakersFlipping) {
          sneakersFlipAngle += 7.2 * delta;
          if (sneakersFlipAngle >= Math.PI * 2) {
            sneakersFlipAngle = Math.PI * 2;
          }
          playerPitchX = -sneakersFlipAngle;
        } else {
          const jumpTiltTarget = playerVelocityY > 2 ? 0.22 : (playerVelocityY < -2 ? -0.15 : 0.05);
          playerPitchX = THREE.MathUtils.lerp(playerPitchX, jumpTiltTarget, 10.0 * delta);
        }
        playerBobY = THREE.MathUtils.lerp(playerBobY, 0.6, 10.0 * delta);
        playerMesh.scale.set(1, 1, 1);
        crown.position.set(0, 1.45, 0);
        crown.scale.set(1, 1, 1);
        visor.position.set(0, 0.8, -0.6);
        if (ganeshaModelInstance) {
          ganeshaModelInstance.scale.set(1, 1, 1);
        }
        if (jetpackGroup.visible) {
          jetpackGroup.scale.set(1, 1, 1);
          jetpackGroup.position.set(0, 0, 0);
        }
      } else {
        playerPitchX = THREE.MathUtils.lerp(playerPitchX, 0.04, 10.0 * delta);
        const stepFreq = (gameSpeed / BASE_SPEED) * 16.0;
        if (isBoardActive) {
          playerBobY = 0.58 + Math.sin(time * 26) * 0.02;
        } else {
          // Velocity-scaled footsteps bobbing and gentle roll sway
          playerBobY = 0.58 + Math.abs(Math.sin(time * stepFreq)) * 0.12;
          playerRollZ += Math.sin(time * stepFreq * 0.5) * 0.035;
        }
        playerMesh.scale.set(1, 1, 1);
        crown.position.set(0, 1.45, 0);
        crown.scale.set(1, 1, 1);
        visor.position.set(0, 0.8, -0.6);
        if (ganeshaModelInstance) {
          ganeshaModelInstance.scale.set(1, 1, 1);
        }
        if (jetpackGroup.visible) {
          jetpackGroup.scale.set(1, 1, 1);
          jetpackGroup.position.set(0, 0, 0);
        }
      }

      playerMesh.position.y = playerBobY;
      if (ganeshaModelInstance) {
        ganeshaModelInstance.position.y = (playerBobY - 0.6) * 0.5;
      }
      playerGroup.rotation.x = playerPitchX;
      playerGroup.rotation.z = playerRollZ;
      playerGroup.rotation.y = laneDelta * 0.04;



      // ----------------------------------------
      // SCROLL TRACK SEGMENTS
      // ----------------------------------------
      for (let seg of trackSegments) {
        seg.position.z += gameSpeed * delta;
        if (seg.position.z > TRACK_SEGMENT_LENGTH) {
          seg.position.z -= TRACK_SEGMENT_COUNT * TRACK_SEGMENT_LENGTH;
        }
      }

      // ----------------------------------------
      // UPDATE VILLAIN (RUNNING AHEAD VISIBLY)
      // ----------------------------------------
      villainGroup.position.z = playerGroup.position.z - VILLAIN_LEAD_DISTANCE;

      villainLaneTimer += delta;
      if (villainLaneTimer > 3.0) {
        villainLaneTimer = 0;
        villainCurrentLane = Math.floor(Math.random() * 3);
        villainTargetX = LANES[villainCurrentLane];
      }
      villainGroup.position.x = THREE.MathUtils.lerp(villainGroup.position.x, villainTargetX, 4.0 * delta);

      // Velocity-scaled procedural running animation for Polluter Villain
      villainGroup.position.y = 0.68 + Math.abs(Math.sin(time * 14.0)) * 0.18;
      villainGroup.rotation.z = Math.sin(time * 6.5) * 0.07;

      if (Math.random() < 0.3) {
        createPopParticles(
          new THREE.Vector3(villainGroup.position.x, 1.8, villainGroup.position.z + 0.9),
          0x475569,
          2,
          1.2
        );
      }

      // ----------------------------------------
      // UPDATE OVERHEAD CEREMONIAL OVERBRIDGES
      // ----------------------------------------
      overbridgeTimer += delta;
      if (overbridgeTimer >= OVERBRIDGE_INTERVAL) {
        overbridgeTimer = 0;
        const bridge = createOverbridge();
        bridge.mesh.position.set(0, 0, -SPAWN_DISTANCE - 15);
        scene.add(bridge.mesh);
        activeOverbridges.push(bridge);
      }

      for (let i = activeOverbridges.length - 1; i >= 0; i--) {
        const b = activeOverbridges[i];
        b.mesh.position.z += gameSpeed * delta;
        if (b.mesh.position.z > DESPAWN_DISTANCE + 15) {
          scene.remove(b.mesh);
          activeOverbridges.splice(i, 1);
        }
      }

      // ----------------------------------------
      // UPDATE PLAYER COLLIDER BOX (THREE.Box3)
      // ----------------------------------------
      const px = playerGroup.position.x;
      const py = playerGroup.position.y;
      const pz = playerGroup.position.z;

      if (isSliding) {
        // Low sliding bounding box (Subway Surfers roll under hurdles)
        playerColliderBox.min.set(px - 0.44, py + 0.02, pz - 0.52);
        playerColliderBox.max.set(px + 0.44, py + 0.52, pz + 0.52);
      } else {
        // Standing / Running / Jumping bounding box (Full Ganesha with Mukut)
        playerColliderBox.min.set(px - 0.38, py + 0.02, pz - 0.36);
        playerColliderBox.max.set(px + 0.38, py + 1.72, pz + 0.36);
      }

      // ----------------------------------------
      // UPDATE CLIMBABLE OBSTACLES & TRAIN PHYSICS
      // ----------------------------------------
      let standingOnTruck = false;

      for (let i = activeObstacles.length - 1; i >= 0; i--) {
        const obs = activeObstacles[i];
        const moveSpeed = gameSpeed + (obs.extraSpeed || 0);
        obs.mesh.position.z += moveSpeed * delta;

        // Animate moving truck effects (wheels rotation, flashing amber beacons, diesel puff)
        if (obs.extraSpeed && obs.extraSpeed > 0) {
          if (obs.wheels) {
            for (let w of obs.wheels) {
              w.rotation.x += moveSpeed * delta * 2.6;
            }
          }
          if (obs.beacons) {
            const beaconOn = Math.sin(time * 24) > 0;
            for (let b of obs.beacons) {
              b.material.opacity = beaconOn ? 1.0 : 0.2;
            }
          }
          if (Math.random() < 0.2) {
            createPopParticles(
              new THREE.Vector3(obs.mesh.position.x, 3.2, obs.mesh.position.z + obs.length / 2),
              0x475569,
              2,
              1.2
            );
          }
        }

        const halfL = (obs.length || 2.0) / 2;
        const halfW = (obs.width || 2.4) / 2;
        const rearZ = obs.mesh.position.z - halfL;
        const frontZ = obs.mesh.position.z + halfL;
        const isInsideX = Math.abs(px - obs.mesh.position.x) <= halfW + 0.12;

        // ----------------------------------------------------
        // A. CLIMBABLE GARBAGE TRUCKS (STATIC, MOVING, RAMP)
        // ----------------------------------------------------
        if (obs.isClimbable) {
          if (obs.hasRamp) {
            // RAMP TRUCK: Incline at front allows running directly onto roof!
            const rampLength = obs.rampLength || 8.5;
            const roofZ = frontZ - rampLength;

            if (isInsideX) {
              // 1. Incline Ramp Zone: smoothly elevates player up to roof without jumping!
              if (pz <= frontZ + 0.25 && pz >= roofZ) {
                const t = THREE.MathUtils.clamp((frontZ - pz) / rampLength, 0, 1);
                const rampH = t * obs.roofY;
                currentBaseY = Math.max(currentBaseY, rampH);

                if (playerY <= rampH + 0.35) {
                  playerY = rampH;
                  playerVelocityY = 0;
                  isGrounded = true;
                  isJumping = false;
                  isSneakersFlipping = false;
                  sneakersFlipAngle = 0;
                }
                standingOnTruck = true;
              }
              // 2. Flat Roof Zone behind ramp
              else if (pz < roofZ && pz >= rearZ - 0.25) {
                if (playerY >= obs.roofY - 0.45) {
                  currentBaseY = obs.roofY;
                  if (playerY <= obs.roofY + 0.35 && playerVelocityY <= 0) {
                    playerY = obs.roofY;
                    playerVelocityY = 0;
                    isGrounded = true;
                    isJumping = false;
                    isSneakersFlipping = false;
                    sneakersFlipAngle = 0;
                  }
                  standingOnTruck = true;
                } else {
                  // Under/beside container body at ground level: solid collision!
                  truckBodyBox.min.set(obs.mesh.position.x - halfW * 0.95, 0.0, rearZ);
                  truckBodyBox.max.set(obs.mesh.position.x + halfW * 0.95, obs.roofY, roofZ);
                  if (playerColliderBox.intersectsBox(truckBodyBox)) {
                    if (!isGadaActive) {
                      playerGroup.position.z = Math.max(playerGroup.position.z, roofZ + 0.42);
                      gameSpeed = 0;
                    }
                    handleCollision(obs, i);
                    continue;
                  }
                }
              }
            }
          } else {
            // SOLID BLOCKAGE TRUCK (No Ramp: Static or Moving)
            truckBodyBox.min.set(obs.mesh.position.x - halfW * 0.95, 0.0, rearZ);
            truckBodyBox.max.set(obs.mesh.position.x + halfW * 0.95, obs.roofY, frontZ);

            // Can run on roof if already elevated (e.g. from super sneakers or dropping from sky)
            const isInsideZ = pz >= rearZ - 0.25 && pz <= frontZ + 0.25;
            if (isInsideX && isInsideZ && playerY >= obs.roofY - 0.40) {
              currentBaseY = obs.roofY;
              if (playerY <= obs.roofY + 0.35 && playerVelocityY <= 0) {
                playerY = obs.roofY;
                playerVelocityY = 0;
                isGrounded = true;
                isJumping = false;
                isSneakersFlipping = false;
                sneakersFlipAngle = 0;
              }
              standingOnTruck = true;
            } else if (playerColliderBox.intersectsBox(truckBodyBox)) {
              // FATAL SOLID IMPACT WITH TRUCK FRONT / SIDES!
              if (!isGadaActive) {
                playerGroup.position.z = Math.max(playerGroup.position.z, frontZ + 0.42);
                gameSpeed = 0;
              }
              handleCollision(obs, i);
              continue;
            }
          }
        }
        // ----------------------------------------------------
        // B. HIGH HURDLES (HANGING SIGNBOARD: MUST ROLL / SLIDE)
        // ----------------------------------------------------
        else if (obs.isHighHurdle) {
          obstacleColliderBox.min.set(obs.mesh.position.x - halfW * 0.95, 1.15, obs.mesh.position.z - 0.38);
          obstacleColliderBox.max.set(obs.mesh.position.x + halfW * 0.95, 2.75, obs.mesh.position.z + 0.38);

          if (playerColliderBox.intersectsBox(obstacleColliderBox)) {
            // Player standing up or jumping into hanging sign -> Crash!
            if (!isGadaActive) {
              playerGroup.position.z = Math.max(playerGroup.position.z, obstacleColliderBox.max.z + 0.42);
              gameSpeed = 0;
            }
            handleCollision(obs, i);
            continue;
          } else if (isInsideX && Math.abs(pz - obs.mesh.position.z) <= 0.65 && isSliding && playerY <= 0.25) {
            // Glided safely underneath with sparks!
            if (Math.random() < 0.25) {
              createPopParticles(new THREE.Vector3(px, 1.15, pz), 0xfacc15, 3, 1.5);
            }
          }
        }
        // ----------------------------------------------------
        // C. LOW BARRICADES & TOXIC GARBAGE JARS (MUST JUMP OVER)
        // ----------------------------------------------------
        else if (obs.isLowBarricade || obs.type === 'low_barricade') {
          const barRoof = obs.roofY || 1.15;
          const barHalfL = Math.max(halfL, 0.6);
          obstacleColliderBox.min.set(obs.mesh.position.x - halfW * 0.92, 0.0, obs.mesh.position.z - barHalfL);
          obstacleColliderBox.max.set(obs.mesh.position.x + halfW * 0.92, barRoof, obs.mesh.position.z + barHalfL);

          if (playerY >= barRoof - 0.05) {
            // Leaped over safely!
          } else if (playerColliderBox.intersectsBox(obstacleColliderBox)) {
            // Hit the toxic roadblock! Sliding does NOT clear ground barricades!
            if (!isGadaActive) {
              playerGroup.position.z = Math.max(playerGroup.position.z, obstacleColliderBox.max.z + 0.42);
              gameSpeed = 0;
            }
            handleCollision(obs, i);
            continue;
          }
        }
        // ----------------------------------------------------
        // D. OTHER GROUND OBSTACLES (BARRELS)
        // ----------------------------------------------------
        else {
          const obsRoof = obs.roofY || 1.25;
          const obsHalfL = Math.max(halfL, 0.6);
          obstacleColliderBox.min.set(obs.mesh.position.x - halfW * 0.92, 0.0, obs.mesh.position.z - obsHalfL);
          obstacleColliderBox.max.set(obs.mesh.position.x + halfW * 0.92, obsRoof, obs.mesh.position.z + obsHalfL);

          if (playerY >= obsRoof - 0.05) {
            // Leaped over safely!
          } else if (playerColliderBox.intersectsBox(obstacleColliderBox)) {
            if (!isGadaActive) {
              playerGroup.position.z = Math.max(playerGroup.position.z, obstacleColliderBox.max.z + 0.42);
              gameSpeed = 0;
            }
            handleCollision(obs, i);
            continue;
          }
        }

        if (obs.mesh.position.z > DESPAWN_DISTANCE) {
          scene.remove(obs.mesh);
          activeObstacles.splice(i, 1);
        }
      }

      if (!standingOnTruck && currentBaseY > 0 && !isJetpackActive) {
        currentBaseY = 0;
        isGrounded = false;
      }

      // ----------------------------------------------------
      // REFINEMENTS: JUMPING SHOES (VERTICAL) VS MAGNET (HORIZONTAL)
      // ----------------------------------------------------
      for (let i = activeCollectibles.length - 1; i >= 0; i--) {
        const col = activeCollectibles[i];
        col.mesh.position.z += gameSpeed * delta;

        col.mesh.rotation.y += 2.5 * delta;
        if (!col.isSkyItem) {
          col.mesh.position.y = col.baseY + Math.sin(time * 4 + col.hoverOffset) * 0.1;
        }

        const dx = Math.abs(col.mesh.position.x - playerGroup.position.x);
        const dz = Math.abs(col.mesh.position.z - playerGroup.position.z);
        const dy = Math.abs((col.mesh.position.y + 0.3) - (playerGroup.position.y + 0.6));

        // 1. Horizontal Bounding Box check (X-axis):
        // When Magnet is active: Expanded across all 3 lanes (dx < 7.5)!
        // When Magnet is NOT active: Strictly single-lane only (dx < 1.35)!
        const maxDx = isMagnetActive ? 7.5 : 1.35;

        // 2. Vertical Bounding Box check (Y-axis):
        // When Jumping Shoes are active: Expanded strictly vertically on Y-axis (dy < 8.5)!
        // When Jumping Shoes are NOT active: Standard vertical reach (dy < 1.85)!
        const maxDy = isSneakersActive ? 8.5 : 1.85;

        // 3. Depth check (Z-axis): Current horizontal row
        const maxDz = 1.65;

        // Visual magnetic suction: when Magnet is active, pull Modaks from other lanes horizontally
        if (isMagnetActive && col.type === 'modak' && dz < 6.5) {
          col.mesh.position.x = THREE.MathUtils.lerp(col.mesh.position.x, playerGroup.position.x, 14.0 * delta);
        }

        // Collision detection with professional collider rules
        if (dx < maxDx && dz < maxDz && dy < maxDy) {
          if (col.type === 'modak') {
            const points = isMultiplierActive ? 2 : 1;
            score += points;
            StorageManager.addModaks(points);
            if (score > bestModakScore) {
              bestModakScore = score;
              StorageManager.saveBestModakScore(bestModakScore);
            }
            // Gameplay reward: every 25 modaks collected awards +1 Mooshikan Shield!
            if (score > 0 && score % 25 === 0) {
              boardsRemaining++;
              StorageManager.saveMooshikanBoards(boardsRemaining);
              createPopParticles(playerGroup.position, 0xa855f7, 20, 5);
            }
            updateHUD();
            playModakSound();
            createPopParticles(col.mesh.position, 0xffb703, 14, 4);

            // Re-trigger gold scale pulse CSS animation
            if (modakScoreEl) {
              modakScoreEl.classList.remove('score-bump');
              void modakScoreEl.offsetWidth; // Force CSS reflow
              modakScoreEl.classList.add('score-bump');
            }
          } else if (col.type === 'jetpack') {
            playPowerupPickupSound();
            createPopParticles(col.mesh.position, 0x00f5ff, 25, 7);
            isJetpackActive = true;
            isJetpackDescending = false;
            jetpackTimer = JETPACK_DURATION;
            jetpackGroup.visible = true;
            jetpackSkyLane = currentLane;
          } else if (col.type === 'sneakers') {
            playPowerupPickupSound();
            createPopParticles(col.mesh.position, 0xf97316, 25, 7);
            isSneakersActive = true;
            sneakersTimer = SNEAKERS_DURATION;
            sneakersGroup.visible = true;
          } else if (col.type === 'magnet') {
            playPowerupPickupSound();
            createPopParticles(col.mesh.position, 0xef4444, 25, 7);
            createPopParticles(col.mesh.position, 0x38bdf8, 18, 5);
            isMagnetActive = true;
            magnetTimer = MAGNET_DURATION;
          } else if (col.type === 'multiplier') {
            playPowerupPickupSound();
            createPopParticles(col.mesh.position, 0xfacc15, 25, 7);
            isMultiplierActive = true;
            multiplierTimer = MULTIPLIER_DURATION;
          } else if (col.type === 'gada') {
            playPowerupPickupSound();
            createPopParticles(col.mesh.position, 0xf59e0b, 30, 8);
            createPopParticles(col.mesh.position, 0xfef08a, 20, 6);
            isGadaActive = true;
            gadaTimer = GADA_DURATION;
            if (!activeGadaMesh) {
              activeGadaMesh = createGadaHandheld();
              playerGroup.add(activeGadaMesh);
            }
            showToast('⚡ Wielding Divine Gada! Smash through obstacles!', 2400);
          }

          updateHUD();
          scene.remove(col.mesh);
          activeCollectibles.splice(i, 1);
          continue;
        }

        if (col.mesh.position.z > DESPAWN_DISTANCE) {
          scene.remove(col.mesh);
          activeCollectibles.splice(i, 1);
        }
      }

      // Dynamic obstacle spawn rate scaling with gameSpeed
      const currentSpawnInterval = Math.max(0.60, SPAWN_INTERVAL * (BASE_SPEED / gameSpeed));
      spawnTimer += delta;
      if (spawnTimer >= currentSpawnInterval) {
        spawnTimer = 0;
        spawnWave();
      }

      // ----------------------------------------
      // ENDLESS PARALLAX SCENERY (PERIPHERAL SPAWNER)
      // ----------------------------------------
      const currentSceneryInterval = Math.max(0.24, SCENERY_SPAWN_INTERVAL * (BASE_SPEED / gameSpeed));
      scenerySpawnTimer += delta;
      if (scenerySpawnTimer >= currentSceneryInterval) {
        scenerySpawnTimer = 0;
        spawnPeripheralScenery(-SPAWN_DISTANCE - 10);
      }

      for (let i = activeScenery.length - 1; i >= 0; i--) {
        const sc = activeScenery[i];
        sc.mesh.position.z += gameSpeed * delta;
        if (sc.mesh.position.z > DESPAWN_DISTANCE + 15) {
          scene.remove(sc.mesh);
          activeScenery.splice(i, 1);
        }
      }
    }

    updateParticles(delta);
    updateShockwaves(delta);

    // ----------------------------------------------------
    // CINEMATIC CAMERA TRANSITION FUNCTION
    // ----------------------------------------------------
    updateCameraTransition(delta);

    renderer.render(scene, camera);
  }

  // ==========================================
  // BUTTERY SMOOTH CAMERA TRANSITION FUNCTION
  // ==========================================
  function updateCameraTransition(delta) {
    let targetSkyRatio = 0.0;
    if (isJetpackActive) {
      if (!isJetpackDescending) {
        targetSkyRatio = 1.0;
      } else {
        targetSkyRatio = Math.max(0, Math.min(1, playerY / JETPACK_Y));
      }
    }

    currentSkyFactor = THREE.MathUtils.lerp(currentSkyFactor, targetSkyRatio, 4.0 * delta);

    const groundCamY = 5.0 + playerGroup.position.y * 0.35;
    const groundCamZ = 10.0;
    const groundFOV = 60.0;
    const groundLookY = 1.8 + playerGroup.position.y * 0.4;
    const groundLookZ = -18.0;

    const skyCamY = 16.0;
    const skyCamZ = 13.0;
    const skyFOV = 70.0;
    const skyLookY = 7.5;
    const skyLookZ = -28.0;

    const targetCamX = playerGroup.position.x * 0.38;
    const targetCamY = THREE.MathUtils.lerp(groundCamY, skyCamY, currentSkyFactor);
    const targetCamZ = THREE.MathUtils.lerp(groundCamZ, skyCamZ, currentSkyFactor);
    const targetFOV = THREE.MathUtils.lerp(groundFOV, skyFOV, currentSkyFactor);

    const targetLookY = THREE.MathUtils.lerp(groundLookY, skyLookY, currentSkyFactor);
    const targetLookZ = THREE.MathUtils.lerp(groundLookZ, skyLookZ, currentSkyFactor);

    camera.position.x = THREE.MathUtils.lerp(camera.position.x, targetCamX, 10.0 * delta);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, targetCamY, 5.5 * delta);
    camera.position.z = THREE.MathUtils.lerp(camera.position.z, targetCamZ, 5.5 * delta);

    if (cameraShakeTimer > 0) {
      cameraShakeTimer -= delta;
      const shakeMag = (cameraShakeTimer / 0.22) * 0.45;
      camera.position.x += (Math.random() - 0.5) * shakeMag;
      camera.position.y += (Math.random() - 0.5) * shakeMag;
    }

    if (Math.abs(camera.fov - targetFOV) > 0.05) {
      camera.fov = THREE.MathUtils.lerp(camera.fov, targetFOV, 4.5 * delta);
      camera.updateProjectionMatrix();
    }

    currentLookY = THREE.MathUtils.lerp(currentLookY, targetLookY, 6.0 * delta);
    currentLookZ = THREE.MathUtils.lerp(currentLookZ, targetLookZ, 6.0 * delta);

    camera.lookAt(playerGroup.position.x * 0.22, currentLookY, currentLookZ);
  }

  // ==========================================
  // COLLISION HANDLER (SHIELD SAVE VS DIVINE ASCENT)
  // ==========================================
  function handleCollision(obs, obsIndex) {
    if (isInvincible) return;

    if (isGadaActive) {
      // Lord Ganesha's Divine Mace smashes directly through incoming obstacles safely!
      playGadaSmashSound();
      createGoldenShockwave(obs.mesh.position);
      createPopParticles(obs.mesh.position, 0xf59e0b, 35, 12);
      createPopParticles(obs.mesh.position, 0xfef08a, 25, 9);
      scene.remove(obs.mesh);
      activeObstacles.splice(obsIndex, 1);

      cameraShakeTimer = 0.22;
      score += 5;
      StorageManager.addModaks(5);
      showToast('💥 Smashed with Divine Gada! +5 🟡', 1400);

      // Restore player Z to origin so run continues seamlessly without interruption
      playerGroup.position.z = 0;
      updateHUD();
      return;
    }

    if (isBoardActive) {
      removeMooshikanBoard();
      playShieldBreakSound();

      createPopParticles(playerGroup.position, 0xa855f7, 30, 8);
      createPopParticles(obs.mesh.position, 0xef4444, 30, 9);
      scene.remove(obs.mesh);
      activeObstacles.splice(obsIndex, 1);

      isInvincible = true;
      invincibleTimer = 2.0;

      // Restore player Z to origin so run continues seamlessly
      playerGroup.position.z = 0;

      updateHUD();
    } else {
      gameSpeed = 0; // Immediate full halt
      startDivineAscent();
    }
  }

  // Window resize handler
  window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    updateOverlaySpriteScale();
  });

  animate();
})();
