# Game Hand Signs 🖐️🔥

A real-time interactive game that uses hand sign recognition to trigger magical abilities in a combat setting. Players use specific hand gestures (Naruto-style hand seals) captured via webcam to cast fireball, water ball, heavy attacks, and defensive walls.

## 🚀 Overview
The project leverages computer vision to detect hand signs within specific Regions of Interest (ROIs). By performing sequences of hand signs (combos), players can battle each other or interact with game elements. The game features visual effects (VFX) and sound effects (SFX) for an immersive experience.

## 📋 Requirements
- *Python*: 3.8 or higher
- *Hardware*: Webcam
- *Dependencies*:
  - opencv-python
  - pygame
  - ultralytics (YOLOv8)
  - numpy
  - pillow (PIL)

## 🛠️ Setup & Installation

1. *Clone the repository:*
   bash
   git clone <repository-url>
   cd game_hand_signs-main
   

2. *Install dependencies:*
   bash
   pip install opencv-python pygame ultralytics numpy pillow
   

3. *Model Weights (Required):*
   - Create a directory named model in the root folder.
   - Download the YOLO weights (best.pt) from the following link:
     [Download Model Weights](https://drive.google.com/drive/folders/1XozvkdLwteOkKV_1Y4hpOJdC2un-EHQZ?usp=share_link)
   - Place the best.pt file inside the model/ directory.
   
   *Note:* The game will not start without model/best.pt.

## 🎮 How to Play

1. *Run the game:*
   bash
   python main.py
   
2. *Game Mechanics:*
   - The screen is divided into two ROIs (Player 1 on the left, Player 2 on the right).
   - Perform hand signs within your ROI to build up combos.
   - Once a combo is recognized, the corresponding ability is triggered.

### ✨ Ability Combos
| Ability | Combo Sequence |
| :--- | :--- |
| *Fireball* 🔥 | snake ➔ horse |
| *Water Ball* 💧 | hare ➔ ram |
| *Heavy Attack* 💥 | dragon ➔ dog |
| *Skeleton Wall* 🛡️ | hare ➔ snake |

### 🛠️ Customizing Moves
To change the sequence of moves or their cooldowns, you need to modify the logic/abilities.py file.

1.  *Open logic/abilities.py*.
2.  *Modify the COMBOS dictionary*:
    Update the list of signs for each AbilityType. For example, to change the Fireball combo:
    python
    COMBOS = {
        AbilityType.FIREBALL: ["snake", "horse"],  # Change signs here
        ...
    }
    
3.  *Modify the COOLDOWNS dictionary*:
    Update the float value (in seconds) to change how often an ability can be used:
    python
    COOLDOWNS = {
        AbilityType.FIREBALL: 1.0,  # Change cooldown duration
        ...
    }
    
    
*Available Signs* (as per model training):

| Dog | Dragon | Hare | Horse | Ram | Snake |
| :---: | :---: | :---: | :---: | :---: | :---: |
| ![dog](midea%20/dog.jpeg) | ![dragon](midea%20/dragon.jpeg) | ![hare](midea%20/hare.jpeg) | ![horse](midea%20/hours.jpeg) | ![ram](midea%20/ram.jpeg) | ![snake](midea%20/snake.jpeg) |

snake, horse, hare, ram, dragon, dog. (Check your model's class names if using a custom model).

## 📂 Project Structure
text
.
├── assets/             # Visual effects (PNG/GIF)
├── core/               # Game state and player logic
├── cv/                 # Camera handling and YOLO detection
├── logic/              # Abilities, combos, and input stabilization
├── sound_Effects/      # Audio files for music and SFX
├── ui/                 # Rendering and overlay logic
├── main.py             # Main entry point
└── model/              # (To be created) Place best.pt here


## 📜 Scripts
- main.py: The primary entry point to launch the game.

## 🌐 Environment Variables
No specific environment variables are required. Configuration is handled within the code or via model paths.

## 🧪 Tests
- Currently, there are no automated tests included in the repository. 
- TODO: Add unit tests for combo logic and stabilizer.
