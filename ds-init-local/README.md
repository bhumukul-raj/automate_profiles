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