#!/bin/bash

# =============================
# Data Science Project Scaffolder
# Version: 2.2
# Author: bhumukulraj
# =============================

# Colors and formatting
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Symbols
CHECK="✓"
ARROW="➜"
FOLDER="📁"
FILE="📄"
CROSS="✗"

# Project Configuration
PROJECT_NAME="project"
FORCE_OVERWRITE=false
DEFAULT_STRUCTURE=(
  "data/raw           # Raw immutable data"
  "data/processed     # Cleaned data sets"
  "data/external      # Third-party data sources"
  "notebooks          # Jupyter notebooks"
  "src/__init__.py    # Make src a Python module"
  "src/data           # Data loading/processing"
  "src/features       # Feature engineering"
  "src/models         # Model building/training"
  "src/visualization  # Visualization utilities"
  "models             # Trained model binaries"
  "reports/figures    # Final report graphics"
  "tests              # Test cases"
  "scripts            # Utility scripts"
  "config             # Configuration files"
)

# File Templates (declare globally)
declare -A FILE_TEMPLATES

# =============================
# Functions
# =============================

print_usage() {
    echo -e "${BOLD}Usage:${NC}"
    echo -e "  $0 [options] [project_name]"
    echo -e "\n${BOLD}Options:${NC}"
    echo -e "  -f, --force           Force overwrite if project directory exists"
    echo -e "  -h, --help            Display this help message and exit"
    echo -e "\n${BOLD}Example:${NC}"
    echo -e "  $0 my-awesome-project"
}

check_dependencies() {
    print_section "Checking Dependencies"
    
    local missing_deps=false
    
    if ! command -v tree &> /dev/null; then
        echo -e "${YELLOW}${CROSS} 'tree' command not found${NC}"
        echo -e "  ${BLUE}${ARROW} README.md will not include directory tree visualization${NC}"
        echo -e "  ${BLUE}${ARROW} Install with: sudo apt-get install tree (Ubuntu/Debian)${NC}"
        TREE_AVAILABLE=false
    else
        echo -e "${GREEN}${CHECK} 'tree' command found${NC}"
        TREE_AVAILABLE=true
    fi
}

print_header() {
  echo -e "${BOLD}${CYAN}"
  echo "=============================================="
  echo "   Data Science Project Scaffolder v2.2       "
  echo "=============================================="
  echo -e "${NC}"
}

print_section() {
  echo -e "\n${BOLD}${YELLOW}$1${NC}"
}

print_success() {
  echo -e "${GREEN}${CHECK} $1${NC}"
}

print_error() {
  echo -e "${RED}${CROSS} $1${NC}"
}

print_creating() {
  echo -e "${BLUE}${ARROW} ${FOLDER} Creating $1...${NC}"
}

check_existing_project() {
  if [ -d "$PROJECT_NAME" ]; then
    if [ "$FORCE_OVERWRITE" = true ]; then
      print_section "Warning: Overwriting Existing Project"
      echo -e "${YELLOW}${CROSS} Project directory already exists: ${PROJECT_NAME}${NC}"
      echo -e "${YELLOW}${ARROW} Overwriting due to --force option${NC}"
      return 0
    else
      print_error "Project directory already exists: ${PROJECT_NAME}"
      echo -e "${YELLOW}${ARROW} Use --force to overwrite or choose a different name${NC}"
      exit 1
    fi
  fi
  return 0
}

# File Templates - Populate the templates
generate_templates() {
  local tree_output=""
  if [ "$TREE_AVAILABLE" = true ]; then
    tree_output=$(cd "${PROJECT_NAME}" && tree --noreport -d)
  else
    tree_output="Project directories (tree command not available)"
  fi

  # Clear and repopulate the templates
  FILE_TEMPLATES=()
  
  FILE_TEMPLATES["README.md"]="# ${PROJECT_NAME}

<div align=\"center\">

![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Last Updated](https://img.shields.io/badge/Last%20Updated-$(date +%B%20%Y)-brightgreen)

</div>

## 📋 Project Overview

<!-- Replace this with a brief description of your project -->
This project aims to [describe the main goal and purpose of your data science project].

### 🎯 Objectives

- [Objective 1]
- [Objective 2]
- [Objective 3]

### 📊 Key Results

<!-- Once you have results, summarize them here -->
- [Key Result/Finding 1]
- [Key Result/Finding 2]
- [Key Result/Finding 3]

## 🔢 Data Sources

<!-- Describe your data sources -->
- **Primary data**: [Description of main dataset]
- **Additional data**: [Any supplementary datasets]

## 🏗️ Project Structure

\`\`\`
${tree_output}
\`\`\`

## 🧮 Methodology

<!-- Briefly describe your approach -->
1. **Data Collection**: [Brief description]
2. **Data Preprocessing**: [Brief description]
3. **Feature Engineering**: [Brief description]
4. **Model Development**: [Brief description]
5. **Evaluation**: [Brief description]

## 📈 Key Insights

<!-- Add visual highlights or key takeaways once available -->
- [Insight 1]
- [Insight 2]
- [Insight 3]

## 🚀 Getting Started

### Prerequisites

- Python 3.9+
- Conda or Miniconda

### Installation

1. Clone this repository:
   \`\`\`bash
   git clone [repository-url]
   cd ${PROJECT_NAME}
   \`\`\`

2. Create and activate the conda environment:
   \`\`\`bash
   bash create_conda_env.sh
   conda activate ${PROJECT_NAME}-env
   \`\`\`

## 📝 Usage

<!-- Instructions on how to use your project, with examples -->
\`\`\`python
# Example code showing how to use your project
from src.data import data_loader

# Load data
data = data_loader.load_dataset('example_dataset')

# Process data
# ...
\`\`\`

## 📊 Results and Visualization

<!-- Add examples of your results and visualizations once available -->
[Include examples, charts, or links to interactive dashboards]

## 🔄 Workflow

<!-- Describe your typical workflow for reproducibility -->
1. Run data processing scripts: \`python src/data/process_data.py\`
2. Run feature engineering: \`python src/features/build_features.py\`
3. Train models: \`python src/models/train_model.py\`
4. Evaluate models: \`python src/models/evaluate_model.py\`

## 👥 Contributors

- [Your Name/Username]

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Credit any data sources, papers, or tools that inspired or supported your work]
"

  FILE_TEMPLATES["environment.yml"]="name: ${PROJECT_NAME}-env
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  # Core data science
  - numpy
  - pandas
  - scipy
  - scikit-learn
  
  # Visualization
  - matplotlib
  - seaborn
  - plotly
  
  # Web apps & dashboards
  - streamlit
  
  # Development tools
  - jupyter
  - jupyterlab
  - notebook
  - ipywidgets
  
  # Statistics
  - statsmodels
  
  # Code quality
  - black
  - flake8
  
  # Utilities
  - tqdm
  - pytest
  - pyyaml
  
  # Add pip packages
  - pip
  - pip:
    - pandas-profiling
    - dataprep  # lightweight EDA tool
"

  FILE_TEMPLATES[".gitignore"]="# Data files
# Uncomment these if you want to ignore your data (recommended for large datasets)
# data/raw/
# data/processed/
# data/external/

# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Distribution / packaging
dist/
build/
*.egg-info/

# Model files (uncommnet if your models are large)
# models/*.pkl
# models/*.h5
# models/*.joblib
# models/*.sav

# Jupyter Notebook
.ipynb_checkpoints
*/.ipynb_checkpoints/*
profile_default/
ipython_config.py

# IPython
.ipython/

# Environment / IDE
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/
.idea/
.vscode/
*.swp
*.swo

# Testing
.coverage
htmlcov/
.pytest_cache/
.coverage.*
nosetests.xml
coverage.xml
*.cover

# Logs
logs/
*.log

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
tmp/
temp/

# Local configuration
.env.local
.env.development.local
.env.test.local
.env.production.local
"

  FILE_TEMPLATES["PROJECT_CHECKLIST.md"]="# 🔬 Data Science Project Checklist

> **Project**: ${PROJECT_NAME}  
> **Created**: $(date +%Y-%m-%d)  
> **Status**: In Progress 🚧

---

## 🚀 Project Setup

- [ ] **Create project structure**
  <!-- Notes about project structure decisions -->

- [ ] **Set up conda environment**
  <!-- Notes about package decisions and dependencies -->

- [ ] **Initialize git repository**
  <!-- Notes about repository setup, remote links -->

- [ ] **Create comprehensive README**
  <!-- Notes about README content -->

- [ ] **Set up project documentation**
  <!-- Notes about documentation approach -->

---

## 📊 Data Collection

- [ ] **Identify data sources**
  <!-- Notes about potential data sources and their qualities -->

- [ ] **Create data acquisition scripts**
  <!-- Notes about acquisition approach -->

- [ ] **Document data sources and licenses**
  <!-- Notes about data origins and usage rights -->

- [ ] **Set up data versioning**
  <!-- Notes about versioning strategy -->

- [ ] **Establish data storage strategy**
  <!-- Notes about storage decisions -->

---

## 🔍 Data Exploration

- [ ] **Examine data distributions**
  <!-- Notes about distribution findings -->

- [ ] **Identify missing values and patterns**
  <!-- Notes about missingness patterns -->

- [ ] **Perform statistical analysis**
  <!-- Notes about statistical findings -->

- [ ] **Create exploratory visualizations**
  <!-- Notes about key visualizations -->

- [ ] **Document key insights**
  <!-- Notes about initial findings -->

---

## 🧹 Data Preprocessing

- [ ] **Create data cleaning pipeline**
  <!-- Notes about cleaning approach -->

- [ ] **Handle missing values**
  <!-- Notes about missing value strategies -->

- [ ] **Address outliers**
  <!-- Notes about outlier detection and handling -->

- [ ] **Transform features as needed**
  <!-- Notes about transformations applied -->

- [ ] **Split data into train/validation/test sets**
  <!-- Notes about splitting strategy and ratios -->

---

## ⚙️ Feature Engineering

- [ ] **Create feature transformations**
  <!-- Notes about transformation approaches -->

- [ ] **Extract relevant features**
  <!-- Notes about feature creation -->

- [ ] **Create feature selection pipeline**
  <!-- Notes about selection methodology -->

- [ ] **Evaluate feature importance**
  <!-- Notes about importance metrics -->

- [ ] **Document feature engineering steps**
  <!-- Notes about engineering decisions -->

---

## 🤖 Model Development

- [ ] **Define evaluation metrics**
  <!-- Notes about metric selection and justification -->

- [ ] **Create baseline model**
  <!-- Notes about baseline approach -->

- [ ] **Train multiple model candidates**
  <!-- Notes about models tried -->

- [ ] **Perform hyperparameter tuning**
  <!-- Notes about tuning strategy -->

- [ ] **Implement cross-validation**
  <!-- Notes about validation approach -->

- [ ] **Compare model performance**
  <!-- Notes about comparison results -->

---

## 📏 Model Evaluation

- [ ] **Evaluate on test set**
  <!-- Notes about test performance -->

- [ ] **Analyze prediction errors**
  <!-- Notes about error patterns -->

- [ ] **Assess model fairness**
  <!-- Notes about fairness metrics -->

- [ ] **Create performance visualizations**
  <!-- Notes about visualization approaches -->

- [ ] **Document model strengths and weaknesses**
  <!-- Notes about model characteristics -->

---

## 🚢 Model Deployment

- [ ] **Create reproducible pipeline**
  <!-- Notes about pipeline architecture -->

- [ ] **Package model for deployment**
  <!-- Notes about packaging approach -->

- [ ] **Set up API/service**
  <!-- Notes about service design -->

- [ ] **Create deployment documentation**
  <!-- Notes about deployment process -->

- [ ] **Implement monitoring**
  <!-- Notes about monitoring strategy -->

---

## 📝 Project Documentation

- [ ] **Document problem statement**
  <!-- Notes about problem definition -->

- [ ] **Document methodology**
  <!-- Notes about methodological decisions -->

- [ ] **Document results and insights**
  <!-- Notes about key findings -->

- [ ] **Create presentation/report**
  <!-- Notes about presentation approach -->

- [ ] **Document future improvements**
  <!-- Notes about potential next steps -->

---

## ⏭️ Next Steps

<!-- List immediate next actions and priorities -->

1. 
2. 
3. 

---

## 📌 Additional Notes

<!-- Any other project-specific notes, decisions, or reference links -->

"

  FILE_TEMPLATES["create_conda_env.sh"]="#!/bin/bash

# Check if conda command is available
if ! command -v conda &> /dev/null; then
    echo \"Conda is not installed or not in your PATH. Please install Conda first.\"
    exit 1
fi

# Source conda shell integration (adjust the path if necessary)
source \"\$(conda info --base)/etc/profile.d/conda.sh\"

# Get current directory name
CURRENT_DIR=\$(basename \"\$(pwd)\")

# Check if environment.yml exists
if [ -f environment.yml ]; then
    echo \"Creating Conda environment from environment.yml in current directory...\"
    # Create environment in the current directory
    conda env create -f environment.yml --prefix ./env
    ENV_PATH=\"./env\"
else
    echo \"environment.yml not found. Creating default environment in current directory...\"
    ENV_PATH=\"./env\"
    conda create --prefix \"\$ENV_PATH\" python=3.9 -y
fi

# Activate the local environment
conda activate \"\$ENV_PATH\"

# Create a .envrc file for direnv (if installed)
echo \"export CONDA_PREFIX=\\\"\$(pwd)/env\\\"\" > .envrc
echo \"conda activate \\\"\$(pwd)/env\\\"\" >> .envrc

echo \"Conda environment created at '\$ENV_PATH' and activated!\"
echo \"Note: To reactivate this environment later, use: conda activate \$ENV_PATH\"
"

  # Add basic Python file templates for key directories
  FILE_TEMPLATES["src/data/data_loader.py"]="# -*- coding: utf-8 -*-
\"\"\"
Data loading functionality.

This module contains functions for loading and retrieving data from various sources.
\"\"\"
import os
import pandas as pd


def get_data_path(subfolder='raw'):
    \"\"\"
    Get the path to the data directory.
    
    Parameters
    ----------
    subfolder : str, optional
        Subdirectory within the data directory, by default 'raw'
    
    Returns
    -------
    str
        Path to the data directory
    \"\"\"
    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the data directory (2 levels up from src/data)
    data_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'data', subfolder)
    
    return data_dir


def load_dataset(filename, subfolder='raw'):
    \"\"\"
    Load a dataset from the data directory.
    
    Parameters
    ----------
    filename : str
        Name of the file to load
    subfolder : str, optional
        Subdirectory within the data directory, by default 'raw'
    
    Returns
    -------
    pandas.DataFrame
        Loaded dataset
    
    Example
    -------
    >>> df = load_dataset('example.csv')
    >>> print(df.head())
    \"\"\"
    # Construct the full path to the file
    file_path = os.path.join(get_data_path(subfolder), filename)
    
    # Determine the file type and load accordingly
    if filename.endswith('.csv'):
        return pd.read_csv(file_path)
    elif filename.endswith('.parquet'):
        return pd.read_parquet(file_path)
    elif filename.endswith(('.xls', '.xlsx')):
        return pd.read_excel(file_path)
    elif filename.endswith('.json'):
        return pd.read_json(file_path)
    else:
        raise ValueError(f\"Unsupported file format: {filename}\")


def save_dataset(df, filename, subfolder='processed'):
    \"\"\"
    Save a dataset to the data directory.
    
    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to save
    filename : str
        Name of the file to save
    subfolder : str, optional
        Subdirectory within the data directory, by default 'processed'
        
    Example
    -------
    >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    >>> save_dataset(df, 'example_processed.csv')
    \"\"\"
    # Construct the full path to the file
    file_path = os.path.join(get_data_path(subfolder), filename)
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Determine the file type and save accordingly
    if filename.endswith('.csv'):
        df.to_csv(file_path, index=False)
    elif filename.endswith('.parquet'):
        df.to_parquet(file_path, index=False)
    elif filename.endswith(('.xls', '.xlsx')):
        df.to_excel(file_path, index=False)
    elif filename.endswith('.json'):
        df.to_json(file_path, orient='records')
    else:
        raise ValueError(f\"Unsupported file format: {filename}\")
"

  FILE_TEMPLATES["src/visualization/visualize.py"]="# -*- coding: utf-8 -*-
\"\"\"
Visualization utilities.

This module contains functions for creating visualizations.
\"\"\"
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import os


def save_figure(fig, filename, dpi=300):
    \"\"\"
    Save a matplotlib figure to the reports/figures directory.
    
    Parameters
    ----------
    fig : matplotlib.figure.Figure
        Figure to save
    filename : str
        Name of the file to save
    dpi : int, optional
        Resolution of the figure, by default 300
    \"\"\"
    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the reports/figures directory (2 levels up from src/visualization)
    figures_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'reports', 'figures')
    
    # Ensure the directory exists
    os.makedirs(figures_dir, exist_ok=True)
    
    # Save the figure
    fig.savefig(os.path.join(figures_dir, filename), dpi=dpi, bbox_inches='tight')
    print(f\"Figure saved to {os.path.join(figures_dir, filename)}\")


def plot_distribution(data, column, title=None, bins=30, figsize=(10, 6)):
    \"\"\"
    Plot the distribution of a column in a dataframe.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the column to plot
    column : str
        Name of the column to plot
    title : str, optional
        Title of the plot, by default None
    bins : int, optional
        Number of bins for the histogram, by default 30
    figsize : tuple, optional
        Size of the figure, by default (10, 6)
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
        
    Example
    -------
    >>> import pandas as pd
    >>> df = pd.DataFrame({'values': np.random.normal(0, 1, 1000)})
    >>> fig = plot_distribution(df, 'values', title='Normal Distribution')
    >>> save_figure(fig, 'normal_distribution.png')
    \"\"\"
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot the histogram
    sns.histplot(data[column], bins=bins, kde=True, ax=ax)
    
    # Set the title and labels
    if title:
        ax.set_title(title)
    ax.set_xlabel(column)
    ax.set_ylabel('Frequency')
    
    plt.tight_layout()
    return fig


def plot_correlation_matrix(data, method='pearson', figsize=(12, 10), title=None):
    \"\"\"
    Plot a correlation matrix for the numeric columns in a dataframe.
    
    Parameters
    ----------
    data : pandas.DataFrame
        Dataframe containing the columns to correlate
    method : str, optional
        Method of correlation, by default 'pearson'
    figsize : tuple, optional
        Size of the figure, by default (12, 10)
    title : str, optional
        Title of the plot, by default None
        
    Returns
    -------
    matplotlib.figure.Figure
        The created figure
        
    Example
    -------
    >>> import pandas as pd
    >>> import numpy as np
    >>> df = pd.DataFrame({
    ...     'A': np.random.normal(0, 1, 100),
    ...     'B': np.random.normal(0, 1, 100),
    ...     'C': np.random.normal(0, 1, 100)
    ... })
    >>> fig = plot_correlation_matrix(df, title='Correlation Matrix')
    >>> save_figure(fig, 'correlation_matrix.png')
    \"\"\"
    # Calculate the correlation matrix
    corr = data.select_dtypes(include=[np.number]).corr(method=method)
    
    # Create the figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Create a mask for the upper triangle
    mask = np.triu(np.ones_like(corr, dtype=bool))
    
    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(230, 20, as_cmap=True)
    
    # Draw the heatmap
    sns.heatmap(
        corr, 
        mask=mask, 
        cmap=cmap, 
        vmax=1, 
        vmin=-1, 
        center=0,
        square=True, 
        linewidths=.5, 
        cbar_kws={\"shrink\": .5},
        annot=True,
        fmt='.2f',
        ax=ax
    )
    
    # Set the title
    if title:
        ax.set_title(title)
    
    plt.tight_layout()
    return fig
"

  FILE_TEMPLATES["src/models/train_model.py"]="# -*- coding: utf-8 -*-
\"\"\"
Model training functionality.

This module contains functions for training and saving models.
\"\"\"
import os
import pickle
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


def get_models_path():
    \"\"\"
    Get the path to the models directory.
    
    Returns
    -------
    str
        Path to the models directory
    \"\"\"
    # Get the absolute path of the current file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Navigate to the models directory (2 levels up from src/models)
    models_dir = os.path.join(os.path.dirname(os.path.dirname(current_dir)), 'models')
    
    # Ensure the directory exists
    os.makedirs(models_dir, exist_ok=True)
    
    return models_dir


def save_model(model, model_name, method='pickle'):
    \"\"\"
    Save a trained model to the models directory.
    
    Parameters
    ----------
    model : object
        Trained model object
    model_name : str
        Name to use for the saved model file
    method : str, optional
        Method to use for saving the model, by default 'pickle'
        Valid options: 'pickle', 'joblib'
        
    Returns
    -------
    str
        Path to the saved model
        
    Example
    -------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.datasets import make_classification
    >>> X, y = make_classification(n_samples=1000, n_features=20, n_classes=2)
    >>> model = RandomForestClassifier().fit(X, y)
    >>> save_model(model, 'random_forest_classifier')
    \"\"\"
    # Get the path to the models directory
    models_dir = get_models_path()
    
    # Construct the full path for the model
    if not model_name.endswith(('.pkl', '.joblib')):
        if method == 'pickle':
            model_name += '.pkl'
        elif method == 'joblib':
            model_name += '.joblib'
    
    model_path = os.path.join(models_dir, model_name)
    
    # Save the model using the specified method
    if method == 'pickle':
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
    elif method == 'joblib':
        joblib.dump(model, model_path)
    else:
        raise ValueError(f\"Unsupported method: {method}. Use 'pickle' or 'joblib'.\")
    
    print(f\"Model saved to {model_path}\")
    return model_path


def load_model(model_name, method=None):
    \"\"\"
    Load a model from the models directory.
    
    Parameters
    ----------
    model_name : str
        Name of the model file to load
    method : str, optional
        Method to use for loading the model, by default None (auto-detect)
        Valid options: None, 'pickle', 'joblib'
        
    Returns
    -------
    object
        Loaded model object
        
    Example
    -------
    >>> model = load_model('random_forest_classifier.pkl')
    >>> predictions = model.predict(X_test)
    \"\"\"
    # Get the path to the models directory
    models_dir = get_models_path()
    
    # Ensure the model name has the correct extension
    if not (model_name.endswith('.pkl') or model_name.endswith('.joblib')):
        if method == 'pickle':
            model_name += '.pkl'
        elif method == 'joblib':
            model_name += '.joblib'
        else:
            # Try to find the model with either extension
            if os.path.exists(os.path.join(models_dir, model_name + '.pkl')):
                model_name += '.pkl'
                method = 'pickle'
            elif os.path.exists(os.path.join(models_dir, model_name + '.joblib')):
                model_name += '.joblib'
                method = 'joblib'
            else:
                raise FileNotFoundError(f\"Model not found: {model_name}\")
    
    model_path = os.path.join(models_dir, model_name)
    
    # Auto-detect the method if not specified
    if method is None:
        if model_name.endswith('.pkl'):
            method = 'pickle'
        elif model_name.endswith('.joblib'):
            method = 'joblib'
        else:
            raise ValueError(\"Could not determine the loading method from the filename.\")
    
    # Load the model using the specified method
    if method == 'pickle':
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    elif method == 'joblib':
        model = joblib.load(model_path)
    else:
        raise ValueError(f\"Unsupported method: {method}. Use 'pickle' or 'joblib'.\")
    
    print(f\"Model loaded from {model_path}\")
    return model


def evaluate_model(model, X_test, y_test, average='weighted'):
    \"\"\"
    Evaluate a model on test data.
    
    Parameters
    ----------
    model : object
        Trained model object with a predict method
    X_test : array-like
        Test features
    y_test : array-like
        True test labels
    average : str, optional
        Averaging method for precision, recall, and f1 score, by default 'weighted'
        
    Returns
    -------
    dict
        Dictionary of evaluation metrics
        
    Example
    -------
    >>> from sklearn.ensemble import RandomForestClassifier
    >>> from sklearn.datasets import make_classification
    >>> from sklearn.model_selection import train_test_split
    >>> X, y = make_classification(n_samples=1000, n_features=20, n_classes=2)
    >>> X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
    >>> model = RandomForestClassifier().fit(X_train, y_train)
    >>> metrics = evaluate_model(model, X_test, y_test)
    >>> print(metrics)
    \"\"\"
    # Make predictions
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average=average, zero_division=0),
        'recall': recall_score(y_test, y_pred, average=average, zero_division=0),
        'f1': f1_score(y_test, y_pred, average=average, zero_division=0)
    }
    
    # Print metrics
    print(\"Model Evaluation Metrics:\")
    for metric, value in metrics.items():
        print(f\"{metric.capitalize()}: {value:.4f}\")
    
    return metrics
"

  FILE_TEMPLATES["notebooks/JUPYTER_NOTEBOOK_GUIDELINES.md"]="# Jupyter Notebook Guidelines for Data Science Projects

## 📋 Notebook Naming Convention

- Use a consistent, meaningful naming scheme with numbering:
  - \`01_data_exploration.ipynb\`
  - \`02_feature_engineering.ipynb\`
  - \`03_model_training.ipynb\`
  - \`04_model_evaluation.ipynb\`

## 🏗️ Professional Notebook Structure

1. **Header Section**
   - Title (project name, notebook purpose)
   - Author(s)
   - Date created/last updated
   - Project overview and objectives
   - Table of contents (if extensive)

2. **Setup Section**
   - All import statements grouped at the beginning
   - Path handling and environment setup
   - Global constants and configuration
   - Helper functions

3. **Data Loading Section**
   - Clear documentation of data sources
   - Initial preview of data
   - Explanation of key fields/features

4. **Analysis Sections** (topic by topic)
   - Each major analysis in its own section with markdown headers
   - Clear questions/hypotheses addressed in each section
   - Code alongside explanatory text
   - Visualizations with descriptive titles and labels

5. **Conclusion Section**
   - Summary of key findings
   - Next steps or recommendations

## 💼 Professional Best Practices

### Code Quality
- Keep code cells concise and focused
- Use descriptive variable names
- Include comments for complex operations
- Avoid unnecessary code repetition
- Use functions for repeated operations

### Markdown Usage
- Use markdown headers (# for main sections, ## for subsections, etc.)
- Include explanations before and after code cells
- Document your thought process and decisions
- Format key points with **bold** or *italics* for emphasis
- Use bullet points and numbered lists for clarity

### Visualizations
- Always include titles, axis labels, and legends
- Use appropriate chart types for your data
- Apply a consistent color scheme
- Include brief interpretation of each visualization
- Consider colorblind-friendly palettes

### Performance Considerations
- Use \\\`%%time\\\` or \\\`%%timeit\\\` magic commands to measure performance
- Avoid running heavy computations unnecessarily
- Consider using sampling for initial exploration
- Store intermediate results when appropriate

### Reproducibility
- Set random seeds for reproducible results:
  \\\`\\\`\\\`python
  import numpy as np
  import random
  import tensorflow as tf
  
  # Set seeds
  np.random.seed(42)
  random.seed(42)
  tf.random.set_seed(42)
  \\\`\\\`\\\`
- Document data preprocessing steps thoroughly
- Use relative paths and environment variables

## 📊 Notebook Template

When creating a new notebook, start with this basic structure:

\\\`\\\`\\\`
# Title: [Project Name] - [Notebook Purpose]
# Author: [Your Name]
# Date: [Date]

## Overview
[Brief description of notebook purpose and goals]

## Setup
[Import libraries and configure environment]

## Data Loading
[Load and preview the datasets]

## Exploratory Data Analysis
[Explore the data with statistics and visualizations]

## [Analysis Section 1]
[Specific analysis or modeling step]

## [Analysis Section 2]
[Next analysis or modeling step]

## Conclusions
[Summary of findings]

## Next Steps
[What should be done next]
\\\`\\\`\\\`

## 🚀 Interactive Features to Consider

- Use interactive visualizations (Plotly, ipywidgets)
- Create collapsible code cells for technical details
- Add progress bars for long-running operations
- Include interactive tables for data exploration

## 📝 Before Sharing/Committing

- Run all cells to ensure they execute properly
- Clear all outputs if notebook size is large
- Review for sensitive information
- Check for quality of explanations and insights
- Ensure visualizations are properly labeled
"
}

create_structure() {
  print_creating "project directory structure"
  
  for entry in "${DEFAULT_STRUCTURE[@]}"; do
    path="${PROJECT_NAME}/$(echo "$entry" | cut -d'#' -f1 | xargs)"
    comment=$(echo "$entry" | cut -d'#' -f2-)
    
    if [[ "$path" == *"__init__.py" ]]; then
      mkdir -p "$(dirname "$path")"
      touch "$path"
      print_success "Python module: $path"
    elif [[ "$path" == *.* ]]; then
      touch "$path"
      print_success "File: $path"
    else
      mkdir -p "$path"
      # Add .gitkeep file to ensure empty directories are tracked by Git
      touch "${path}/.gitkeep"
      print_success "Directory: $path ${MAGENTA}${comment}${NC}"
    fi
  done
}

create_files() {
  generate_templates
  print_creating "essential project files"
  
  for file in "${!FILE_TEMPLATES[@]}"; do
    path="${PROJECT_NAME}/${file}"
    # Create directory if it doesn't exist
    mkdir -p "$(dirname "$path")"
    
    echo -e "${FILE_TEMPLATES[$file]}" > "$path"
    
    print_success "Template: $path"
    
    # Make conda script executable
    if [[ "$file" == "create_conda_env.sh" ]]; then
      chmod +x "$path"
    fi
  done
}

show_summary() {
  echo -e "\n${BOLD}${GREEN}Project created successfully!${NC}"
  echo -e "${BOLD}${CYAN}Project Name:${NC} ${PROJECT_NAME}"
  echo -e "${BOLD}${CYAN}Location:${NC} $(pwd)/${PROJECT_NAME}"
  
  echo -e "\n${BOLD}Next steps:${NC}"
  echo -e "${ARROW} ${YELLOW}cd ${PROJECT_NAME}${NC}"
  echo -e "${ARROW} ${YELLOW}bash create_conda_env.sh${NC} (to create conda environment)"
  echo -e "${ARROW} ${YELLOW}conda activate ${PROJECT_NAME}-env${NC}"
}

# =============================
# Parse Command-Line Arguments
# =============================

while [[ "$#" -gt 0 ]]; do
    case $1 in
        -f|--force) FORCE_OVERWRITE=true ;;
        -h|--help) print_usage; exit 0 ;;
        -*) echo "Unknown parameter: $1"; print_usage; exit 1 ;;
        *) PROJECT_NAME="$1"; break ;;
    esac
    shift
done

# =============================
# Main Execution
# =============================

print_header
check_dependencies
echo -e "${BOLD}${MAGENTA}Building project structure: ${PROJECT_NAME}${NC}"

check_existing_project
mkdir -p "${PROJECT_NAME}"
print_success "Root directory created"

create_structure
create_files

echo -e "\n${BOLD}${GREEN}${CHECK} Project scaffolding complete!${NC}"
show_summary