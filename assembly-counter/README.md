
# Power-ASS (Power Audit Scope Script)

A bash script to help prepare audit scope directories for smart contract security reviews.

## Installation

1. Download the script and place it in your home directory:
```bash
cd ~
curl -O https://raw.githubusercontent.com/your-repo/power-ass.sh
# or manually copy the power-ass.sh script to ~/ (home directory)
```

2. Make the script executable:
```bash
chmod +x ~/power-ass.sh
```

## Usage

Call the script by providing the full path to your scope directory:

```bash
sh ~/power-ass.sh /full/path/to/scope/directory
```

Example:
```bash
sh ~/power-ass.sh /Users/macbookpro/Documents/hacken/SilexoDeFi___renatus-protocol-contracts/scope
```

### Notes
- For ease of use the script should be located in your home directory (`~`)
- Always use absolute paths when specifying the scope directory
- The scope directory should contain the smart contracts to be analyzed

### Troubleshooting
If you get a "Permission denied" error, ensure the script is executable:
```bash
chmod +x ~/power-ass.sh
```

