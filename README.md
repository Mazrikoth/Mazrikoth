# DragonZMind CYOA Desktop App

A downloadable, DnD-inspired choose-your-own-adventure (CYOA) desktop app with a built-in creator mode. The app supports a one-time playthrough by default, with optional save/load unlocked via custom codes that you generate and distribute to subscribers.

## What this MVP includes

- **Player mode** to play a branching CYOA story.
- **Creator mode** to edit the data tables that power the world (classes, races, items, story text, and images).
- **Manual save code system** that unlocks save/load functionality.
- **Image trigger tokens** in story text (e.g., `[image1.png]`) to display artwork at specific story points.

## Project layout

```
.
├── app.py
├── assets
│   └── images
│       └── README.md
└── data
    ├── armor.json
    ├── classes.json
    ├── images.json
    ├── items.json
    ├── races.json
    ├── save_codes.json
    ├── story.json
    ├── story_guidelines.json
    ├── story_intros.json
    └── weapons.json
```

## Getting started

1. Ensure you have Python 3.10+ installed.
2. Run the app:

```bash
python app.py
```

## How images work

- Add your image files to `assets/images/`.
- Reference them in story text with tokens like `[image1.png]`.
- The app displays the image when it encounters that token.

## Save codes

- Add custom save codes to `data/save_codes.json`.
- Players without a valid code can play once, but cannot save.
- Players with a valid code can save and reload their progress.
