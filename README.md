#  Bow Busters

## 🎮 Introduction
**Bow Busters** is a fast-paced, strategic action game built using **Python** and **Pygame**.  
Your goal is to survive as long as possible by placing defensive structures, activating abilities, and reacting to intelligent enemy behavior.

This project was developed for **NUST SEECS — Data Structures & Algorithms (CS-250)** and demonstrates:

- Multi-module software engineering  
- Use of advanced data structures  
- Integration of algorithms in a real-time environment  
- Clean, scalable architecture  

Enemies navigate using intelligent pathfinding, dynamically rerouting when the player blocks tiles. The project includes menus, abilities, undo mechanics, animations, collision handling, and a persistent local leaderboard.

---

## 🚀 How to Run the Project

### 1. Install Python  
Requires **Python 3.10+**

### 2. Navigate to project folder  
Where `main.py` is located:
cd Bow-Busters

### 3. Install Pygame  
pip install pygame

### 4. Run the game 
python main.py


The game window will launch automatically.

---

## 🔗 GitHub Profile

 **Jump to GitHub:** https://github.com/Maham-Codes/Bow-Busters

---

## 📘 Detailed Project Description

Bow Busters consists of multiple interacting modules, each representing a major game subsystem. Together they fulfill CS-250 requirements for modularity, algorithmic depth, and DSA application.

---

# 1. Functional Modules


## ⚙️ Game Engine & Main Loop
**Module:** `game`

Handles all per-frame operations:

- Player input  
- Defence placement  
- Undo actions  
- Abilities  
- Wave spawning  
- Updating bullets, explosions, enemies  
- Score, money, and life tracking  
- Rendering all subsystems  

Acts as the central orchestrator connecting all modules.

---

## 🗺️ Level System
**Module:** `level`

- Loads `.level` files  
- Places initial environment prefabs  
- Initializes collision map  
- Precomputes paths for smooth gameplay  
- Stores level metadata (time, money, lives)

---

## 🧭 Pathfinding Engine (A*)
**Module:** `pathfinding`

A key component of the game.

Features:

- Custom incremental **A\*** algorithm  
- Runs pathfinding across multiple frames (performance-friendly)  
- Uses open/closed sets, dynamic scoring, neighbor processing  
- Auto-repairs paths when player blocks tiles  
- Generates partial paths for stuck enemies  
- Avoids congestion using adaptive tile costs  

Enables enemies to always find valid and efficient movement paths.

---

## 👾 Enemy AI System
**Module:** `enemy`

Enemy capabilities:

- Follow assigned A* paths  
- Recalculate if blocked  
- Scale speed & health by wave  
- Deduct player lives if escaping  
- Reward money on death  

---

## 🛡️ Defence System
**Module:** `defence`

Defence structures:

- Auto-target nearest viable enemy  
- Fire bullets or trigger explosions  
- Rotate toward targets  
- Block tiles (affecting pathfinding)  
- Include one-time-use structures (e.g., mines)

---

## 🧱 Prefab System (Config-Based Object Loader)
**Module:** `prefab`

- Loads object configurations from `.prefab` files  
- Dynamically applies attributes to enemies, defences, abilities, bullets, effects, UI elements  
- Uses caching to avoid repeated disk reads  
- Supports animations, rotations, fonts, image loading  
- Enables reusable, data-driven object creation

---

## 🎯 Projectile & Explosion System
**Modules:** `bullet`, `explosion`

System provides:

- Bullet movement with normalized velocity  
- Lifetime tracking  
- Collision with walls/enemies  
- Explosion damage falloff  
- Animated explosion effects  

---

## ⚡ Ability System
**Module:** `abilities`

Example: **Crystal Spike**

- Temporarily blocks multiple tiles  
- Adds spike visuals  
- Forces path recalculation  
- Uses cooldown timers  
- Stores active effects in structured lists  

---

## 🧱 Collision System
**Module:** `collision`

- Tile-based grid representation  
- O(1) blocked tile lookup  
- Handles block/unblock mechanics  
- Notifies the pathfinder when tiles change  
- Ensures bullets & enemies follow physical constraints  

---

## 🌊 Wave System
**Module:** `wave`

- Spawns enemies of varying size  
- Uses nonlinear difficulty progression  
- Tracks wave completion  
- Manages spawn timing  

---

## 🧩 Menu & UI System
**Module:** `menu`

Includes:

- Main menu  
- Pause menu  
- How-to-play  
- Defence & ability bar  
- Score, wave counters  
- Lose screen  
- Mouse interactions and rendering  

---

## 🏆 Local Leaderboard System
**Module:** `leaderboard`

- Stores data in JSON  
- Maintains top 20 scores  
- Tracks current player  
- Displays trophy icons  

---

# 2. Data Structures Used (Strong DSA Integration)

Bow Busters uses **far more** than the required three DSA structures.  

## ✔ Lists
Used for:
- Paths  
- Enemies  
- Prefabs  
- Active abilities  
- Level tile data  
- Wave spawning queues  

## ✔ Dictionaries (Hash Maps)
Used for:
- Prefab configuration  
- Ability cooldowns  
- A* g-scores, f-scores, came_from  
- UI attributes  
- Leaderboard entries  

## ✔ Sets
Used for:
- A* open/closed sets  
- Blocked tiles  
- Unique crystal spike locations  

## ✔ Stacks
Undo system via **LIFO purchase_history**

## ✔ Grid / Tile Map
Collision system:

- Constant-time tile checks  
- Multi-tile blocking  

## ✔ Priority-like Logic
A* uses scoring logic similar to a priority queue.

## ✔ Caches
Prefab cache prevents redundant file loads.

## ✔ JSON Data Structures
Leaderboard stores list of dict entries.

## ✔ Sprite Groups (Pygame)
Efficient rendering & update system for all moving objects.

---

# 3. Algorithms Used

## 🧠 A* Pathfinding
- Dynamic + incremental  
- Auto-repairing  
- Partial path support  
- Multi-frame calculation  

## 🎯 Greedy Target Selection
- Defences target nearest enemy in range (O(n))

## 💥 Damage Falloff
- Explosion damage ∝ inverse squared distance

## 🔁 Undo Operation (Stack)
- Latest defence placement removed first

## 🧩 Collision Detection
- O(1) tile lookup  
- Rect overlap checks across tile grid  

---
---

# 🧪 Running Test Cases & Performance Analysis

To validate correctness and analyze algorithm performance, the project includes **runtime test cases and performance measurements** executed through Python scripts.

## ▶ Running Test Cases

1. Open a terminal in the project root directory:
cd Bow-Busters


2. Run the test cases script (provided separately) or execute the game with debug output enabled:
python main.py


3. Test cases validate:
- Enemy pathfinding correctness  
- Defence targeting logic  
- Undo stack behavior  
- Ability cooldown handling  
- Collision detection accuracy  

Each test confirms expected behavior through console output and in-game results.

---

## 📈 Big-O Performance Evaluation

Algorithm efficiency was measured by varying input sizes and observing execution time:

### Tested Scenarios
- Pathfinding with increasing grid sizes  
- Target selection with increasing enemy count  
- Stack operations with large undo histories  

### Input Sizes Used
- N = 10  
- N = 100  
- N = 1000+ (where applicable)

### Observations
- **A\*** pathfinding scales efficiently due to incremental execution and caching  
- Collision lookups remain constant-time **O(1)**  
- Stack-based undo operations execute in **O(1)**  
- Target selection scales linearly **O(n)** with number of enemies  

Average execution times were taken over multiple runs to ensure consistency.

This confirms that the implemented data structures and algorithms meet real-time performance requirements.

---

# 4. Big-O Efficiency Analysis

| Component                    | Complexity                              |
|-----------------------------|------------------------------------------|
| A* Pathfinding              | ~O(V log V) (optimized, incremental)     |
| Collision Tile Lookup       | O(1)                                     |
| Defence Target Selection    | O(n) where n = enemies                   |
| Bullet Collision Checks     | O(n)                                     |
| Undo Operation              | O(1)                                     |
| Spike Ability Allocation    | O(k) where k = spike count               |


---


# 6. Future Improvements
- More abilities  
- Procedural level generation  
- New enemy types  
- Cloud leaderboard  
- ML-based adaptive AI  

---

## 👥 Team Members
 
- **Arham Fatima**
- **Maham Mansoor** 
- **Mehak Chaudhry** 
- **Sumayya Emaan**

---

## ✅ Conclusion
A game that proves DSA can do more than pass exams — it can run worlds.

Project wrapped. Algorithms behaved. THE END.


