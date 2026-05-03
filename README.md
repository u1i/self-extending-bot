# Self-Extending Bot

A minimal LLM-powered bot that teaches itself new abilities on the fly.

You just talk to it. If it can't do something, it figures out how — writes code, calls APIs, learns new tricks — and remembers them for next time. No setup, no plugins, no config files to edit.

## What it does

- Answers questions it already knows how to handle
- When it can't do something, it teaches itself by writing a small Python program
- Reuses what it learned in future sessions
- Asks you for help when it needs an API key or a package installed

## Example

```
Ready. What do you need?

You: what's the weather in tokyo?
  [learn_ability] ...

Here's the current weather in Tokyo:
- Condition: Mainly clear
- Temperature: 23.4°C (feels like 23.2°C)
- Humidity: 52%

You: how about london?
  [use_ability] ...

London, United Kingdom:
- Overcast
- 13°C (feels like 11.6°C)
- Humidity: 79%
```

First time: it figured out how to get weather data. Second time: it just used what it already knew.

## Setup

```bash
# Install dependency
pip install openai

# Set your API credentials
export ANTHROPIC_COMPATIBLE_ENDPOINT="https://your-api-endpoint/v1"
export API_KEY="your-api-key"
export MODEL="your-model-name"

# Run
python3 bot.py
```

Or edit and run `./run.sh`.

## How it works

The bot has two hidden tools:

1. **use_ability** — run something it already knows how to do
2. **learn_ability** — write a new Python program and save it as a permanent ability

Abilities are just Python files in the `skills/` directory. Each one has a `run(params)` function that takes a dict and returns a string. The bot loads them all on startup and decides which to use (or whether to create a new one) based on what you ask.

You never need to touch the `skills/` directory — the bot manages it.

## Requirements

- Python 3.10+
- An OpenAI-compatible API endpoint (Xiaomi MiMo, OpenAI, etc.)
