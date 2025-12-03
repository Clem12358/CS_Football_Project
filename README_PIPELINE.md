# Football Attendance Prediction - Pipeline Guide

This guide explains how to run the complete data pipeline in VS Code using Jupyter notebooks.

## 📁 Project Structure

```
CS_Football_Project/
├── src/
│   ├── 1.Webscrapping.ipynb       # Data collection (already done)
│   ├── 2.DataCleaning.ipynb       # Data cleaning & feature engineering
│   ├── 3.DB                        # Database creation
│   └── 4.ML_dev&save.ipynb        # Model training & saving
├── Data/
│   ├── RawDataB_weather.csv       # Input (raw data)
│   ├── CleanedData.csv            # Output from step 2
│   └── football.db                # Output from step 3
├── Models/
│   ├── finalized_model_with_weather (3).sav
│   └── finalized_model_without_weather (3).sav
└── App/
    └── app_football.py            # Streamlit app
```

## 🚀 Running the Pipeline

### Prerequisites

Make sure you have installed:
```bash
pip install pandas numpy sqlite3 scikit-learn streamlit requests openpyxl
```

### Step 1: Data Cleaning (Required if data changed)

Open `src/2.DataCleaning.ipynb` in VS Code and run all cells.

**What it does:**
- Loads `Data/RawDataB_weather.csv`
- Cleans and processes the data
- Filters to **Jupiler Pro League only**
- Adds features (rolling stats, economic data, categorizations)
- Outputs `Data/CleanedData.csv`

**Key filters applied:**
- Only Belgian Pro League teams (16 teams)
- Only "Jupiler Pro League" competition
- Removes COVID period (March 2020 - August 2021)
- Removes games not yet played

### Step 2: Database Creation (Required if CleanedData.csv changed)

Open `src/3.DB` in VS Code and run all cells.

**What it does:**
- Loads `Data/CleanedData.csv`
- Creates normalized database schema
- Outputs `Data/football.db`

**Database tables:**
- `Team` - Team dimension (16 JPL teams)
- `Stadium` - Stadium dimension (15 stadiums)
- `EconomicContext` - Quarterly economic indicators
- `Match` - Match fact table (~944 JPL matches)
- `MatchParticipation` - Match participation (home/away stats)

### Step 3: Model Training (Required if football.db changed or improving models)

Open `src/4.ML_dev&save.ipynb` in VS Code and run all cells.

**What it does:**
- Loads data from `Data/football.db`
- Trains two models:
  - With weather features
  - Without weather features
- Saves models to `Models/` folder

### Step 4: Run the App

```bash
cd App
streamlit run app_football.py
```

## 🔄 When to Rerun Each Step

| Step | Rerun When... |
|------|--------------|
| **2. DataCleaning** | Raw data updated, need to adjust features, or fixing data issues |
| **3. DB** | CleanedData.csv changed |
| **4. ML** | Database changed, want to retrain models, or adjust hyperparameters |
| **App** | Never needs rerunning - just restart if models updated |

## ✅ Current Status

After the recent fixes:
- ✅ Notebooks converted from Google Colab to VS Code
- ✅ All paths updated to local relative paths
- ✅ DataCleaning filters correctly to JPL only
- ✅ Rolling stats initialization fixed
- ✅ Time slot logic consistent between notebook and app

## 🎯 Next Steps to Get Clean JPL-Only Database

1. Run `src/2.DataCleaning.ipynb` from start to finish
2. Run `src/3.DB` from start to finish
3. Verify the database only contains JPL matches:
   ```bash
   sqlite3 Data/football.db "SELECT COUNT(*), competition FROM Match GROUP BY competition;"
   ```
   Should show only "Jupiler Pro League" with ~944 matches

## 📝 Important Notes

### Path Structure
All notebooks use **relative paths** that work when run from VS Code:
- When you open a notebook in VS Code, the working directory is automatically the notebook's directory (`src/`)
- `../Data/` resolves to `/Users/clementdurix/Code/CS_Football_Project/Data/`
- `../Models/` resolves to `/Users/clementdurix/Code/CS_Football_Project/Models/`

### All Output Files Go to Data/
Every intermediate and final CSV is saved to the `Data/` folder:
- `Cleaned_RawDataB.csv` (intermediate)
- `Updated_Cleaned_RawDataB_weather.csv` (intermediate)
- `football_results.csv` (intermediate)
- `CleanedData.csv` (final - used by DB)
- `football.db` (database)

### Pipeline Notes
- The pipeline is linear: each step depends on the previous one
- Models are already trained and saved, no need to retrain unless improving
- All Colab-specific code (drive mounting, file downloads) has been removed
