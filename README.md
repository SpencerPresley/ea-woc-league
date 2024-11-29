# nhl-club-stats

Python package for parsing and analyzing NHL EASHL club statistics.

## Features

- Pydantic models for NHL EASHL club data structures
- Club and player statistics parsing
- Match history analysis
- Data validation and cleaning

## Installation

### Option 1: Install from PyPI (not yet published)

```bash
pip install nhl-club-stats
```

### Option 2: Install for Development

1. Install PDM if you haven't already:

```bash
pip install pdm
```

2. Clone the repository:****

```bash
git clone https://github.com/spencerpresley/nhl-club-stats.git
cd nhl-club-stats
```

3. Initialize PDM and install dependencies:

```bash
pdm install            # install all dependencies
pdm install -G test    # install just test dependencies
```

## Usage

### Game Data Models

The package provides several models for working with NHL EASHL game data:

```python
from nhl_club_stats.models.game import Match, Club, PlayerStats

# Load match data
match = Match.model_validate(match_data)

# Access club information
for club_id, club in match.clubs.items():
    print(f"Club: {club.details.name}")
    print(f"Score: {club.score}")
    print(f"Shots: {club.shots}")

# Access player statistics
for club_id, players in match.players.items():
    for player_id, player in players.items():
        print(f"Player: {player.player_name}")
        print(f"Goals: {player.sk_goals}")
        print(f"Assists: {player.sk_assists}")
```

### Club Data Models

The package also provides models for working with club data:

```python
from nhl_club_stats.models.club import ClubInfo, ClubData

# Load club data
club = ClubData.model_validate(club_data)

# Access club information
print(f"Club: {club.name}")
print(f"Division: {club.division}")
print(f"Record: {club.wins}-{club.losses}-{club.ties}")
```

## Development

### Running Tests

With PDM installed, you can run tests using:

```bash
pdm run pytest                 # run all tests
pdm run pytest -v             # verbose output
pdm run pytest -s             # show print statements
pdm run pytest tests/models/  # test specific directory
```

The test configuration in pyproject.toml includes coverage reporting by default.

### Project Structure

```tree
nhl-club-stats/
├── src/
│   └── nhl_club_stats/
│       ├── models/
│       │   ├── game/        # Game-related models
│       │   └── club.py      # Club-related models
│       └── utils/           # Utility functions
├── tests/
│   ├── models/             # Model tests
│   └── utils/              # Utility tests
├── pyproject.toml          # Project configuration
└── README.md
```

### Adding Dependencies

```bash
pdm add package-name        # add new dependency
pdm add -G test package-name  # add new test dependency
```

## Test Graph

[![codecov](https://codecov.io/github/SpencerPresley/ea-woc-league/branch/master/graph/badge.svg?token=QDEI2JRTTM)](https://codecov.io/github/SpencerPresley/ea-woc-league)

## License

MIT License
