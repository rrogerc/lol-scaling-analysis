# LoL Scaling Analysis

This project aggregates and analyzes League of Legends champion win rates over specific game time intervals (e.g., 0-15 min, 30-35 min) to identify scaling patterns. It scrapes data from Lolalytics and provides a ranked list of champions based on their performance at different stages of the game.

## Features

- **Smart Scraper**: Fetches champion win rate data by game time for specified patches and tiers. It automatically skips re-scraping historical patches if the data already exists, only updating the latest patch.
- **Scaling Analysis**: Aggregates data across multiple patches to smooth out variance and ranks champions by win rate in 5-minute intervals.
- **Configurable**: Easily adjust which patches and rank tiers to analyze via a JSON configuration file.

## Prerequisites

- Python 3.7+
- `aiohttp` library for asynchronous scraping.

## Setup

1.  **Install Dependencies:**
    ```bash
    pip install aiohttp
    ```

2.  **Configuration (`config.json`):**
    Ensure a `config.json` file exists in the root directory. It controls which data is fetched and analyzed.

    ```json
    {
      "patches": ["15.24", "15.23", "15.22"],
      "tiers": ["diamond"],
      "concurrency": 5
    }
    ```
    *   `patches`: List of patch numbers to process.
    *   `tiers`: Rank tiers to filter by (e.g., "diamond", "emerald", "master").
    *   `concurrency`: Number of simultaneous requests (default: 5).

## Usage

### 1. Scrape Data
Run the scraper to download data from Lolalytics.
```bash
python3 scraper.py
```
*   **Note:** The scraper will automatically detect the latest patch in your config. It will always re-scrape the latest patch to ensure data is fresh but will skip older patches if the data files already exist locally.

### 2. Analyze Data
Run the analysis script to generate rankings.
```bash
python3 analyze_data.py
```

**Options:**
- `-n` or `--top`: Specify the number of top champions to display per time bucket (default: 10).
  ```bash
  python3 analyze_data.py --top 20
  ```

## Output
The analysis script prints the results to the console, organized by time intervals (e.g., "0 - 15 min", "40+ min").

Example output:
```text
=== 30 - 35 min (Top 10, min 100 games) ===
Rank  Champion             Win Rate   Games
--------------------------------------------------
1     kayle                56.66%    111880
2     quinn                55.10%     70193
...
```
