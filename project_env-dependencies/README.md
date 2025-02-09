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
1. Make sure your project environment is activated:
   ```bash
   conda activate your_project_env_name
   ```

2. Run the installation script:
   ```bash
   python install_additional_packages.py
   ```

## Important Notes

- The `install_additional_packages.py` script will:
  - Check if your project environment exists
  - Verify that `additional_requirements.txt` exists
  - Ensure you're in an activated conda environment
  - Install all specified packages using pip

- If you encounter any errors:
  - Check that your environment is properly activated
  - Verify package names and versions are correct
  - Look for any conflicting dependencies

## Error Messages and Solutions

If you see these messages:

1. "Project environment not found":
   - Run `cd dsi-config && python setup_project.py your_project_name` first

2. "No conda environment is activated":
   - Activate your environment with `conda activate your_project_env_name`

3. "additional_requirements.txt not found":
   - Create the file and add your required packages
