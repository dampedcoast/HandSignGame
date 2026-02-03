# Ninja Duel - Cloud9 x JetBrains Booth Mini-Game

## Setup
1. Install dependencies:
   ```bash
   pip install opencv-python ultralytics pygame numpy
   ```
2. Place your custom YOLO model in the `model` directory and name it `best.pt`.
3. Ensure you have a camera connected.

## How to Play
- **Start Game**: Press `SPACE`
- **Player 1 (Left ROI)**: Perform hand signs or use keys `1`, `2`, `3`, `4`
- **Player 2 (Right ROI)**: Perform hand signs or use keys `8`, `9`, `0`, `-`
- **Restart**: Press `R` after Game Over
- **Exit**: Press `ESC`

## Abilities
- **Fireball**: Sequence `tiger` -> `ox` -> `snake` (or key `1`/`8`)
- **Wall**: Sequence `hare` -> `snake` -> `boar` (or key `2`/`9`)
- **Heavy Attack**: Sequence `dragon` -> `tiger` -> `monky` (or key `3`/`0`)
- **Water Ball**: Sequence `hare` -> `horse` -> `ram` (or key `4`/`-`)

## Note
- **Countering**: Fireball and Water Ball block each other if they collide!
- The game uses a time-based stabilizer for hand signs (200ms) and a 1.5s window for combos.
If the custom model is not found, it will download a standard YOLOv8n model for testing.
