import os
import sys
import csv
import json
import subprocess
from hashlib import sha3_256
import pandas as pd
from pathlib import Path
import re

def get_language_from_extension(extension: str) -> str:
    """
    Get the programming language based on a given file extension.
    """
    languages = {
        '.sol': 'Solidity',
        '.rs': 'Rust',
        '.py': 'Python',
        '.vy': 'Vyper',
        '.scilla': 'Scilla',
        '.tsol': 'Solidity',
    }
    language = languages.get(extension)
    if language is None:
        raise ValueError(f"Unsupported file extension: {extension}")
    return language

def remove_rust_tests(code: str) -> str:
    if re.match(r"^\s*#!\[cfg\(test\)\]", code):
        return ""
    
    test_block_indeces = [i.start() for i in re.finditer("#\[cfg\(test\)\]", code)]
    original_code = code

    for start in reversed(test_block_indeces):
        end = next_code_block_end(code[start:])
        if end == -1:
            return original_code
        code = code[:start] + code[start + end:]
    return code

def next_code_block_end(code: str) -> int:
    depth = 0
    for i, c in enumerate(code):
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0:
                return i + 1
            elif depth < 0:
                break
    return -1

def remove_rust_solidity_comments(code: str) -> str:
    return re.sub(r"/\*[\s\S]*?\*/|//.*", "", code)

def remove_python_comments(code: str) -> str:
    return re.sub(r"(?:#.*$|'''[\s\S]*?'''|\"\"\"[\s\S]*?\"\"\")", "", code, flags=re.MULTILINE)

def remove_vyper_comments(code: str) -> str:
    return re.sub(r"#[^\n]*", "", code)

def remove_scilla_comments(code: str) -> str:
    return re.sub(r"\(\*.*?\*\)", "", code)

def remove_non_code(language: str, code: str) -> str:
    if language == 'Rust':
        code = remove_rust_tests(code)
        return remove_rust_solidity_comments(code)
    elif language == 'Solidity':
        return remove_rust_solidity_comments(code)
    elif language == 'Python':
        return remove_python_comments(code)
    elif language == 'Vyper':
        return remove_vyper_comments(code)
    elif language == 'Scilla':
        return remove_scilla_comments(code)
    else:
        raise NotImplementedError(f"Unsupported language: {language}")

def count_lines_of_code(file_path: str) -> int:
    """Count non-empty lines of code, excluding comments."""
    try:
        extension = Path(file_path).suffix.lower()
        language = get_language_from_extension(extension)
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Remove comments and other non-code
        content_only_code = remove_non_code(language, content)
        
        # Count non-empty lines
        lines = content_only_code.splitlines()
        return len([line for line in lines if line.strip()])
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return 0

def process_files(scope_dir):
    results = []
    for root, _, files in os.walk(scope_dir):
        for file in files:
            if file == '.DS_Store':
                continue
            file_path = os.path.join(root, file)
            with open(file_path, 'rb') as f:
                content = f.read()
            
            sha3 = sha3_256(content).hexdigest()
            loc = count_lines_of_code(file_path)
            
            results.append({
                'file': os.path.relpath(file_path, scope_dir),
                'sha3': sha3,
                'loc': loc
            })
    
    return results

def main():
    if len(sys.argv) != 4:
        print("Usage: python3 estimation_reporter.py <project_name> <repository_url> <commit>")
        sys.exit(1)

    project_name = sys.argv[1]
    repository_url = sys.argv[2]
    commit = sys.argv[3]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    scope_dir = os.path.join(script_dir, 'scope')
    
    if not os.path.exists(scope_dir):
        print(f"Error: The 'scope' directory does not exist at {scope_dir}")
        print("Please create a 'scope' directory and place your files in it.")
        return

    files = os.listdir(scope_dir)
    if not files:
        print(f"Error: The 'scope' directory at {scope_dir} is empty.")
        print("Please add some files to analyze.")
        return

    print(f"Processing files in {scope_dir}")
    results = process_files(scope_dir)
    
    if not results:
        print("No files were processed. Make sure the 'scope' directory contains valid files.")
        return

    # Create project directory
    project_dir = os.path.join(script_dir, project_name)
    os.makedirs(project_dir, exist_ok=True)

    # Separate contracts and interfaces
    contracts = []
    interfaces = []
    for result in results:
        entry = {
            'File Path & SHA3 Hash': f"File: {result['file']}\nSHA3: {result['sha3']}",
            'LoC': result['loc']
        }
        if 'interface' in result['file'].lower() or 'interfaces' in result['file'].lower():
            interfaces.append(entry)
        else:
            contracts.append(entry)

    # Write combined contract data
    contract_output_file = os.path.join(project_dir, 'combined_contracts_data.csv')
    write_csv(contract_output_file, contracts)

    # Write combined interface data
    interface_output_file = os.path.join(project_dir, 'combined_interfaces_data.csv')
    write_csv(interface_output_file, interfaces)

    # Create Cyver portal CSV file
    # cyver_data = []
    # for result in results:
    #     file_path = result['file']
    #     title = os.path.basename(file_path)
    #     loc = result['loc']
    #     sha3 = result['sha3']
    #     cyver_data.append({
    #         'Title': title,
    #         'Description': '',
    #         'Type': 'SmartContract',
    #         'Repository': repository_url,
    #         'Lines of Code': loc,
    #         'Commit': commit,
    #         'Technology': sha3
    #     })

    cyver_data = []
    for result in results:
        file_path = result['file']  # This is already the relative path
        # Use the full relative path instead of just the basename
        title = file_path  # Changed from os.path.basename(file_path)
        loc = result['loc']
        sha3 = result['sha3']
        cyver_data.append({
            'Title': title,
            'Description': '',
            'Type': 'SmartContract',
            'Repository': repository_url,
            'Lines of Code': loc,
            'Commit': commit,
            'Technology': sha3
        })

    cyver_output_file = os.path.join(project_dir, 'cyver_portal_data.csv')
    cyver_df = pd.DataFrame(cyver_data)
    cyver_df.to_csv(cyver_output_file, index=False)

    print(f"Files generated successfully in the '{project_name}' folder:")
    print(os.path.relpath(contract_output_file, script_dir))
    print(os.path.relpath(interface_output_file, script_dir))
    print(os.path.relpath(cyver_output_file, script_dir))

def write_csv(filename, data):
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['File Path & SHA3 Hash', 'LoC']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for entry in data:
            writer.writerow(entry)

if __name__ == "__main__":
    main()
