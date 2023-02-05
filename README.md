# Infinite Seinfeld Clips

This script fetches [infinite seinfeld's](https://www.twitch.tv/watchmeforever) top clips from the past 24 hours and concatenates them into a single video.

## Requirements

- ImageMagick and FFmpeg
- Python 3.7+

## Usage

```
pipenv install
```

Enter twitch client ID and secret in .env file

```
cp .sample.env .env
```

Run the script

```
pipenv run python main.py
```

## TODO:

- [ ] Get clip popularity based on reactions in the discord
- [ ] Add metadata into video (takes longer to render)
