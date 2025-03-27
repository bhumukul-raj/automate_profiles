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

## Project Structure
\`\`\`
${tree_output}
\`\`\`

## Getting Started
1. Clone this repository
2. Create conda environment: \`bash create_conda_env.sh\`
3. Activate environment: \`conda activate ${PROJECT_NAME}-env\`

## Contributing
See CONTRIBUTING.md for guidelines
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

  FILE_TEMPLATES[".gitignore"]="# Data
data/
models/

# Environments
.env
.venv/
env/

# IDE
.vscode/
.idea/
__pycache__/
*.py[cod]
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
      print_success "Directory: $path ${MAGENTA}${comment}${NC}"
    fi
  done
}

create_files() {
  generate_templates
  print_creating "essential project files"
  
  for file in "${!FILE_TEMPLATES[@]}"; do
    path="${PROJECT_NAME}/${file}"
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