# 6-Nimmt-Game 🎴🐮

A complete implementation of the **6 Nimmt! card game** developed in **Python using Pygame**.  
The game includes full gameplay logic, AI players, scoring based on bull heads, and multiple interactive UI screens.

---

## 📌 About the Game
6 Nimmt! is a strategic card game where players try to avoid collecting **bull head penalty points**.  
Each round, all players secretly select a card, which are then revealed and placed on the table according to the game rules.

The player who reaches **64 penalty points** first loses the game.

---

## ✨ Features
- Full implementation of official 6 Nimmt! rules  
- Single-player mode with **AI opponents**
- Card selection timer for human player
- Intelligent card placement logic
- Penalty calculation using bull heads
- Interactive menu system:
  - Main Menu
  - Player Selection
  - How to Play screen
  - Game Over screen with **Play Again** option
- Graphical UI using Pygame

---

## 🛠 Technologies Used
- **Python 3**
- **Pygame**

---

## 📂 Project Structure
```
6-Nimmt-Game/
├── assets/
│   ├── background.png.jpg
│   └── bull.png
├── 6nimmt.py
└── README.md

```
---

## ▶️ How to Run the Game

### 1️⃣ Install Python
```bash
python --version
```

### 2️⃣ Install Pygame
```bash
pip install pygame
```

### 3️⃣ Run the Game
```bash
python 6nimmt.py
```

---

## 🎮 Gameplay Overview
- Each player starts with **10 cards**
- Four rows are placed on the table
- Players select one card per round
- Cards are revealed together and placed in ascending order
- If a card cannot be placed, the player must take a row
- Penalty points are calculated using bull heads
- The game ends when any player reaches **64 points**

---

## 🤖 AI Logic
- AI players automatically select cards from their hand
- When forced to take a row, AI chooses the row with **minimum penalty**
- Card placement follows closest valid row logic



---

## 👩‍💻 Author
**Susmitha P**

---

## 📜 License
This project is created for **educational and academic purposes**.


