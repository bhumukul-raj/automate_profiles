# Project Environment Dependencies

This directory contains files for managing additional Python package dependencies for your project environment.

## Files Overview

### 1. `additional_requirements.txt`
This file is used to specify additional Python packages that you want to install in your project environment. 

- Format: One package per line with optional version constraints
- Example:
  ```
  tensorflow>=2.0.0
  pytorch>=2.0.0
  transformers>=4.0.0
  ```

### 2. `install_additional_packages.py`
A Python script that handles the installation of packages specified in `additional_requirements.txt`.

## Usage Instructions

### Step 1: Specify Additional Packages
1. Open `additional_requirements.txt`
2. Add your required packages, one per line
3. Optionally specify version constraints using `>=`, `==`, or `<=`
4. Remove the comment symbols (`#`) from example packages or add your own

Example `additional_requirements.txt`:
```
tensorflow>=2.0.0
pytorch>=2.0.0
transformers>=4.0.0
```

### Step 2: Install Additional Packages
1. Make sure your project environment is activated. You can activate it using either:
   ```bash
   # Method 1: Using the full path (recommended)
   conda activate /path/to/your/project/.dsi/environments/your_project_name
   
   # Example:
   conda activate /home/username/path/to/project/.dsi/environments/telecom_churn_analysis
   ```

2. Run the installation script from your project root directory:
   ```bash
   python3 project_env-dependencies/install_additional_packages.py
   ```

## Important Notes

- The `install_additional_packages.py` script will:
  - Automatically detect your project environment name from your project directory
  - Verify that your environment exists in the `.dsi/environments` directory
  - Check that `additional_requirements.txt` exists and is properly formatted
  - Ensure you're in an activated conda environment
  - Install all specified packages using pip

- If you encounter any errors:
  - Make sure you're in the project root directory when running the script
  - Verify your conda environment is properly activated
  - Check that package names and versions are correct
  - Look for any conflicting dependencies

## Error Messages and Solutions

1. "Project environment not found":
   - Ensure you're running the script from the project root directory
   - Verify that your environment exists in `.dsi/environments/`
   - If needed, run `cd dsi-config && python setup_project.py your_project_name`

2. "No conda environment is activated":
   - Activate your environment using the full path:
     ```bash
     conda activate /path/to/your/project/.dsi/environments/your_project_name
     ```

3. "additional_requirements.txt not found":
   - Make sure the file exists in the `project_env-dependencies` directory
   - Create the file if needed and add your required packages
