# Comparative Analysis of the real estate market between the richest and the poorest in the USA

## Project Overview

This project provides a complete pipeline for scraping, cleaning, analyzing, and visualizing house price data for Mississippi and Washington. It includes:

- **Web Scraping**: Automated scripts to collect house listings from Redfin.
- **Data Cleaning**: Jupyter notebook for preprocessing and cleaning raw data.
- **Exploratory Data Analysis (EDA)**: Jupyter notebook for statistical analysis and visualizations.
- **Interactive Dashboard**: Tableau dashboard for interactive exploration.

## Context & Key Outcomes

Mississippi is consistently ranked as one of the poorest states in the U.S., with some of the lowest median incomes and highest poverty rates, while Washington is one of the richest. This economic disparity is reflected in the housing market data analyzed in this project.

**Key Outcomes from the Analysis:**

- **Median House Prices:** Washington’s median house prices are significantly higher than Mississippi’s, both in absolute terms and per square foot.
- **Price per Square Foot:** Washington homes command a higher price per square foot, indicating greater demand and property value.
- **City-Level Insights:** The most expensive cities are predominantly in Washington, with Mississippi cities ranking much lower in terms of median price.
- **Property Types & Lot Sizes:** Washington offers a greater diversity of property types and generally larger lot sizes, while Mississippi’s market is more limited.
- **Parking & Amenities:** Homes in Washington tend to offer more amenities, such as parking spaces, which also correlate with higher prices.
- **Trends Over Time:** The price trend by year built shows steady growth in Washington, while Mississippi’s market remains relatively flat.

These findings highlight the strong correlation between state-level economic factors and housing market outcomes. For more detailed visualizations and interactive exploration, visit the [Tableau Dashboard](https://public.tableau.com/app/profile/md.tanjeelur.rahman.labib/viz/Book1_17571376236460/WvsMpriceAnalysis?publish=yes).

## Project Architecture

```
HousePriceAnalysis_and_Visualization/
│
├── data/
│   ├── house_listings.csv            # Raw scraped data
│   └── cleaned_house_listings.csv    # Cleaned dataset
│
├── scraper/
│   ├── mississippie_scrap.py         # Scraper for Mississippi listings
│   └── washington_scrap.py           # Scraper for Washington listings
│
├── data_cleaning.ipynb               # Data cleaning notebook
├── eda_analysis_washington_vs_mississippie.ipynb  # EDA & visualization notebook
├── requirements.txt                  # Python dependencies
└──README.md                         # Project documentation
                            
```

## Step-by-Step Guide

### 1. Clone the Repository

```powershell
git clone https://github.com/Tanjeelur/HousePriceAnalysis_and_Visualization.git
cd HousePriceAnalysis_and_Visualization
```

### 2. Set Up Python Environment

It is recommended to use a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate
```

### 3. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 4. Scrape House Listings

- **Mississippi**: Run `scraper/mississippie_scrap.py`
- **Washington**: Run `scraper/washington_scrap.py`

Both scripts use Selenium to scrape Redfin listings and save results to `data/house_listings.csv`.

### 5. Data Cleaning

Open and run `data_cleaning.ipynb` in Jupyter Notebook or VS Code. This notebook:

- Loads raw data
- Removes duplicates and nulls
- Cleans and transforms columns
- Outputs `data/cleaned_house_listings.csv`

### 6. Exploratory Data Analysis & Visualization

Open and run `eda_analysis_washington_vs_mississippie.ipynb`. This notebook provides:

- Statistical summaries
- Visualizations (bar plots, box plots, scatter plots)
- Comparative analysis between Mississippi and Washington

### 7. Interactive Tableau Dashboard

Explore the interactive dashboard for deeper insights:

[Tableau Dashboard: W vs M Price Analysis](https://public.tableau.com/app/profile/md.tanjeelur.rahman.labib/viz/Book1_17571376236460/WvsMpriceAnalysis?publish=yes)

## Notebooks

- **data_cleaning.ipynb**: Data preprocessing and cleaning steps.
- **eda_analysis_washington_vs_mississippie.ipynb**: EDA, visualizations, and state/city-level comparisons.

## Requirements

- Python 3.7+
- Google Chrome (for Selenium)
- [ChromeDriver](https://chromedriver.chromium.org/downloads) (ensure it's in your PATH)
- Python packages: `selenium`, `pandas`, `requests`, `matplotlib`, `seaborn`, `numpy`

## Additional Notes

- Scraping large datasets may take time and is subject to website restrictions.
- For Tableau dashboard, no login is required; just follow the link above.
- For any issues, refer to the [GitHub repository](https://github.com/Tanjeelur/HousePriceAnalysis_and_Visualization.git).
