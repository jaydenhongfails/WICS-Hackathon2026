# Yoga Pose Analyzer 🧘

A real-time yoga coach that uses your webcam to analyze your poses and give you instant feedback on your form.

---

## What It Does

1. Pick a yoga pose from the menu
2. Strike the pose in front of your camera
3. Get an accuracy score and personalized feedback on what to fix

---

## Before You Start

You'll need to install a couple of things:

**Ollama** — runs the AI locally on your machine
- Download at [ollama.com](https://ollama.com/download) and install it like any app
- Then open your terminal and run:
```bash
ollama pull llava
```

**The Yoga Dataset** — reference images the app compares you against
- Download from [Kaggle](https://www.kaggle.com/datasets/niharika41298/yoga-poses-dataset) (free account required)
- Unzip it and place the `yoga_poses_dataset` folder inside the project folder

---

## Setup

```bash
pip3 install -r requirements.txt
python3 main.py
```

---

## How to Use It

- A camera window will open with a green alignment guide
- Press **SPACE** to start a 3-second countdown, then hold your pose
- Your score and feedback will print in the terminal
- Press **Y** to try again, **N** to pick a new pose, **Q** to quit

---

## Available Poses

| # | Pose         |
|---|--------------|
| 0 | Downward Dog |
| 1 | Goddess Pose |
| 2 | Plank Pose   |
| 3 | Tree Pose    |
| 4 | Warrior II   |

---

## Tips for a Better Score

- Stand **4–6 feet** back so your full body is visible
- Use a **plain wall** as your background
- Make sure you're in a **well-lit** area
- The camera is **mirror-flipped** so it feels natural to position yourself
