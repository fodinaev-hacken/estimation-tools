## Estimation Reporter Tool

The Estimation Reporter tool analyzes smart contracts to generate line-of-code (LoC) counts and hash information, helping with project estimation and tracking.

### Prerequisites

- Python 3.x
- Virtual Environment (recommended)

### Setup

1. Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Unix or MacOS:
source venv/bin/activate
```

2. Install required dependencies:
```bash
pip install pandas
```

### Usage

1. The `scope` folder in the same directory as the script
2. Place your formatted contracts into the `scope` folder
3. Run the script with the following arguments:
```bash
python estimation-cloc.py <project_name> <repository_url> <commit_hash>   # with spaces separating them
```

Example:
```bash
python estimation-cloc.py MyProject https://github.com/user/project abc123def
```

### Output

The script generates three files in a new directory named after your project:

1. `combined_contracts_data.csv` - Contains all contracts with their hash and LoC
2. `combined_interfaces_data.csv` - Contains all interfaces with their hash and LoC
3. `cyver_portal_data.csv` - Formatted data for Cyver portal import

Example output:
<img width="1714" alt="image" src="https://github.com/user-attachments/assets/b3e32061-5a3b-4aa6-a8c4-e3f61b233905" />

### Important Notes

- The script automatically identifies interfaces by looking for files in folders named "interface" or "interfaces"
- If you have interface contracts outside of interface folders, you'll need to manually adjust the generated CSV files (e.g., using Google Sheets)

