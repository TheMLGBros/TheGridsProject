# The Grids Project

This repository contains a small arcade-based prototype. Automated tests have been added under the `tests/` directory.

The project requires the real [`arcade`](https://api.arcade.academy/) package. Install it along with `pytest` to run the game or the unit tests.

Unit, item and UI images are stored under the `sprites/` directory. Each type has its own subfolder to keep assets organized.

## Running the Game

To start the game, run the `grids.py` script:

```bash
python grids.py
```

This launches a window where you can move units, play spell cards and end your turn using the on-screen buttons.
There are separate buttons for drawing spells and units into your hand.


## Running Tests

Install dependencies (e.g. `arcade` and `pytest`) and run:

```bash
pytest
```

This will execute all unit tests.
