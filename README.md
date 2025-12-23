# Premier League Match Predictor

A machine learning project that predicts English Premier League football match outcomes using historical data and advanced statistics.

## Overview

This project implements a complete data science pipeline for predicting Premier League match results (Win/Draw/Loss). It scrapes historical match data from FBref, engineers relevant features, and trains a Random Forest classifier to make predictions.

## Features

- **Automated Data Collection**: Web scraping of match statistics and season standings from FBref
- **Comprehensive Feature Engineering**: Rolling averages, team rankings, venue effects, and temporal features
- **Machine Learning Prediction**: Random Forest classifier for multi-class outcome prediction
- **Anti-Detection Scraping**: Uses undetected ChromeDriver to bypass Cloudflare protection
- **Historical Analysis**: 10 seasons of Premier League data (2014-2024)

## Project Structure

```
prem/
├── scraper.py                  # Scrapes match data and statistics
├── standings_scraper.py        # Collects season standings/rankings
├── predictor.py                # ML model training and prediction
├── test.ipynb                  # Interactive testing notebook
├── matches.csv                 # Historical match data
├── matches2324.csv            # 2023-24 season data
└── standings_2014_15_to_2023_24.csv  # Team rankings by season
```

## Installation

### Requirements

- Python 3.8+
- Chrome browser

### Dependencies

```bash
pip install pandas scikit-learn beautifulsoup4 selenium undetected-chromedriver jupyter
```

## Usage

### 1. Collect Data

First, scrape the season standings:

```bash
python standings_scraper.py
```

Then, scrape match data:

```bash
python scraper.py
```

Note: Scraping includes polite delays (3-6 seconds between requests) and may take some time.

### 2. Train Model and Predict

Run the prediction model:

```bash
python predictor.py
```

This will:
- Load historical match and standings data
- Engineer features (rolling averages, rankings, etc.)
- Train a Random Forest classifier on pre-2024 data
- Evaluate on 2024+ matches
- Output prediction accuracy metrics

### 3. Interactive Analysis

Explore the data interactively:

```bash
jupyter notebook test.ipynb
```

## Features Used for Prediction

The model uses the following engineered features:

- **Team Strength**: Previous season rankings for both teams
- **Recent Form**: 5-game rolling averages for:
  - Goals for/against
  - Shots and shots on target
  - Shot distance
  - Free kicks and penalties
- **Match Context**: Venue (home/away), opponent, day of week, match time
- **Promotion Status**: Indicator for newly promoted teams
- **Rank Differential**: Difference in previous season rankings

## Model Details

- **Algorithm**: Random Forest Classifier
- **Parameters**: 40 estimators, minimum 10 samples per split
- **Train/Test Split**: Training on pre-2024 data, testing on 2024+ matches
- **Evaluation Metric**: Macro precision score
- **Output Classes**:
  - Win (W=2)
  - Loss (L=1)
  - Draw (D=0)

## Data Sources

All data is scraped from [FBref.com](https://fbref.com), which provides comprehensive football statistics including:
- Match results and scores
- Expected goals (xG)
- Shooting statistics
- Possession data
- Season standings

## Notes

- The scrapers use undetected ChromeDriver to avoid Cloudflare anti-bot detection
- Random delays are implemented for ethical scraping practices
- The model is trained on historical data and may not account for recent team changes, injuries, or other real-time factors
- Prediction accuracy varies as football matches have inherent unpredictability

## Future Improvements

Potential enhancements could include:
- Player-level statistics and squad depth
- Head-to-head historical records
- Injury and suspension data
- Transfer window impact analysis
- Weather conditions
- Referee statistics
- More advanced models (Gradient Boosting, Neural Networks)

## License

This project is for educational and research purposes only. Please respect FBref's terms of service when scraping data.
