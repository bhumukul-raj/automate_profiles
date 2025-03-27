# Data Science Toolkit for Project Management

![Version](https://img.shields.io/badge/Version-2.2-blue)
![License](https://img.shields.io/badge/License-MIT-green)

A suite of powerful bash utilities designed to streamline data science workflows, maintain consistent project structures, and improve productivity.

## 📦 What's Included

This toolkit includes two main utilities:

1. **`ds-project-structure.sh`** - A sophisticated project scaffolder that creates standardized data science project structures
2. **`dataScience-shortcuts.sh`** - A desktop shortcut manager for quick access to your data science projects

## ✨ Key Features

### Project Structure Generator

- **Standardized Directory Structure** - Creates a consistent, best-practice folder organization
- **Built-in Documentation** - Generates README and project checklist files
- **Development Environment** - Configures local conda environments with essential data science packages
- **Visualization** - Includes matplotlib, seaborn, and plotly for all visualization needs
- **Interactive Apps** - Streamlit integration for creating data dashboards
- **Customizable** - Easy to adapt for project-specific needs

### Desktop Shortcuts Manager

- **Centralized Access** - Creates desktop shortcuts to all your data science projects
- **Intelligent Updates** - Safely replaces outdated shortcuts
- **Dry Run Mode** - Test changes before applying them
- **Custom Paths** - Configurable source and target directories

## 🚀 Getting Started

### Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/data-science-toolkit.git
```

2. Make the scripts executable:

```bash
chmod +x ds-project-structure.sh dataScience-shortcuts.sh
```

3. (Optional) Add to your PATH for system-wide access:

```bash
export PATH=$PATH:/path/to/data-science-toolkit
```

### Creating a New Project

```bash
./ds-project-structure.sh my-new-project
```

This creates a comprehensive project structure:

```
my-new-project/
├── config/                # Configuration files
├── data/
│   ├── external/          # Third-party data sources
│   ├── processed/         # Cleaned data sets
│   └── raw/               # Raw immutable data
├── models/                # Trained model binaries
├── notebooks/             # Jupyter notebooks
├── reports/
│   └── figures/           # Final report graphics
├── scripts/               # Utility scripts
├── src/
│   ├── data/              # Data loading/processing
│   ├── features/          # Feature engineering
│   ├── models/            # Model building/training
│   └── visualization/     # Visualization utilities
├── tests/                 # Test cases
├── .gitignore             # Git ignore file
├── create_conda_env.sh    # Environment setup script
├── environment.yml        # Conda environment specification
└── PROJECT_CHECKLIST.md   # Project task tracker
```

## 📁 What Files Go Where

Below is a guide to what types of files should be placed in each folder of your data science project structure:

### 1. **data/raw** - Raw immutable data
- Original data files (CSV, Excel, JSON, etc.)
- Should be treated as read-only and never modified
- Example files: `raw_sales_data.csv`, `survey_responses.json`, `raw_sensor_readings.parquet`

### 2. **data/processed** - Cleaned data sets
- Cleaned and preprocessed versions of raw data
- Intermediate data that has been transformed
- Example files: `cleaned_sales_data.csv`, `normalized_survey_data.pickle`, `feature_matrix.parquet`

### 3. **data/external** - Third-party data sources
- Data from external sources that supplement your primary data
- Reference datasets (e.g., census data, weather data)
- Example files: `city_population.csv`, `exchange_rates.json`, `industry_benchmarks.xlsx`

### 4. **notebooks** - Jupyter notebooks
- Exploratory data analysis (EDA) notebooks
- Experiment notebooks
- Result visualization notebooks
- Example files: `01_data_exploration.ipynb`, `02_feature_engineering.ipynb`, `03_model_evaluation.ipynb`

### 5. **src** - Python package for project code
- **src/__init__.py** - Makes the src directory a proper Python package
- Organized code modules by functionality

### 6. **src/data** - Data loading/processing
- Scripts for acquiring and processing data
- Data pipeline code
- Example files: 
  - `data_loader.py` - Functions to load data from various sources
  - `preprocessing.py` - Functions for cleaning and preprocessing
  - `validation.py` - Data validation utilities

### 7. **src/features** - Feature engineering
- Code for creating and transforming features
- Feature selection utilities
- Example files:
  - `build_features.py` - Functions to generate features
  - `encoders.py` - Custom encoding functionality
  - `feature_selection.py` - Methods for selecting important features

### 8. **src/models** - Model building/training
- Model implementation
- Training scripts
- Evaluation utilities
- Example files:
  - `train_model.py` - Model training scripts
  - `predict_model.py` - Prediction functions
  - `evaluate_model.py` - Model evaluation functions
  - `model_factory.py` - Factory pattern for model creation

### 9. **src/visualization** - Visualization utilities
- Visualization functions and classes
- Plotting utilities
- Example files:
  - `visualize.py` - Functions for creating standard visualizations
  - `plotting.py` - Custom plotting functions
  - `dashboards.py` - Dashboard components

### 10. **models** - Trained model binaries
- Saved model files
- Model checkpoints
- Example files: `random_forest_v1.pkl`, `neural_net_20230615.h5`, `xgboost_final.json`

### 11. **reports/figures** - Final report graphics
- Visualizations for reports/presentations
- Charts, graphs, and plots
- Example files: `sales_forecast_chart.png`, `feature_importance.pdf`, `confusion_matrix.svg`

### 12. **tests** - Test cases
- Unit tests for your code
- Integration tests
- Example files:
  - `test_data_loader.py`
  - `test_preprocessing.py`
  - `test_model.py`
  - `conftest.py` - Pytest configurations and fixtures

### 13. **scripts** - Utility scripts
- Standalone scripts for various tasks
- Automation scripts
- Example files:
  - `update_data.py` - Script to refresh data
  - `batch_predict.py` - Script for batch predictions
  - `export_results.py` - Script to export results

### 14. **config** - Configuration files
- Configuration files for different environments
- Parameter settings for models
- Example files:
  - `config.yaml` - Main configuration
  - `model_params.json` - Model hyperparameters
  - `logging.conf` - Logging configuration

### Setting Up the Environment

After creating a project:

```bash
cd my-new-project
bash create_conda_env.sh
```

This creates a local conda environment with key packages:
- Core data science: numpy, pandas, scipy, scikit-learn
- Visualization: matplotlib, seaborn, plotly
- Web apps: streamlit
- Development: jupyter, black, flake8
- And more!

### Creating Desktop Shortcuts

```bash
./dataScience-shortcuts.sh --source /path/to/projects
```

Options:
- `-s, --source <dir>` - Source directory containing projects
- `-d, --desktop <dir>` - Target directory for shortcuts (default: ~/Desktop)
- `-n, --dry-run` - Simulate without making changes
- `-h, --help` - Display help message

## 📋 Project Management

The generated `PROJECT_CHECKLIST.md` helps track progress through your data science workflow:

- **Project Setup** - Environment, git, documentation
- **Data Collection** - Sources, acquisition, versioning
- **Data Exploration** - Distributions, missing values, visualizations
- **Data Preprocessing** - Cleaning, outliers, transformations
- **Feature Engineering** - Transformations, selection
- **Model Development** - Baseline, tuning, cross-validation
- **Model Evaluation** - Testing, error analysis, fairness
- **Model Deployment** - Pipelines, packaging, monitoring
- **Project Documentation** - Problem statement, methodology, insights

## 🔧 Customization

### Modifying the Project Structure

Edit the `DEFAULT_STRUCTURE` array in `ds-project-structure.sh` to add, remove, or modify directories.

### Customizing the Environment

Edit the `environment.yml` template in `generate_templates()` function to add or remove packages.

### Changing Shortcut Behavior

Modify the `create_shortcuts()` function in `dataScience-shortcuts.sh` to change how shortcuts are generated.

## 💡 Tips

- Use `--force` with the project generator to overwrite existing directories
- Run `dataScience-shortcuts.sh` with `--dry-run` to see what changes would be made
- Install the tree command for better README visualization: `sudo apt-get install tree`
- Add custom sections to your project checklist as needed

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👤 Author

Created by Bhumukulraj 