# The Grids Project

This repository contains a small arcade-based prototype. Automated tests have been added under the `tests/` directory.

The directory `arcade/` includes a very small stub of the real `arcade` library so the code and tests can run without extra dependencies. It exposes only a few placeholders and is **not** the full game framework.

## Running the Game

To start the game, run the `grids.py` script:

```bash
python grids.py
```

This launches a window where you can move units, play spell cards and end your turn using the on-screen buttons.

## Using the Real Arcade Library

The stub in `arcade/` is only for testing. To play the game with the actual framework, install the real package and ensure the stub no longer shadows it:

```bash
pip install arcade
# remove or rename the local stub directory, or adjust PYTHONPATH
python grids.py
```

Removing (or renaming) the `arcade/` directory allows Python to import the library from your environment. You can then launch the game as normal.

## Running Tests

Install dependencies (e.g. `arcade` and `pytest`) and run:

```bash
pytest
```

This will execute all unit tests.
