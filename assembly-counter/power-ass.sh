#!/bin/bash

# Check if a folder path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <folder_path>"
    exit 1
fi

folder_path=$1

# Function to process a single file
process_file() {
    local filename=$1
    local count=0
    local inside_asm=0
    local inside_block=0

    while IFS= read -r line; do
        # Remove leading/trailing whitespace
        line=$(echo "$line" | sed -e 's/^[[:space:]]*//' -e 's/[[:space:]]*$//')
        
        if [[ $line =~ ^.*{.*$ ]] && [ $inside_asm -eq 1 ]; then
            inside_block=$((inside_block + 1))
        fi
        if [[ $line =~ ^assembly[[:space:]]*{[[:space:]]*$ ]]; then
            inside_asm=1
            count=$((count - 1))
        fi
        if [[ $line =~ ^.*}.*$ ]]; then
            if [ $inside_block -gt 0 ]; then
                inside_block=$((inside_block - 1))
            else
                inside_asm=0
            fi
        fi
        # Only count non-empty and non-comment lines inside assembly blocks
        if [ $inside_asm -eq 1 ] && [ -n "$line" ] && [[ ! $line =~ ^// ]]; then
            count=$((count + 1))
        fi
    done < "$filename"

    echo "$filename|$count"
}

# Create temporary files
files_list=$(mktemp)
results=$(mktemp)
sorted_results=$(mktemp)

# Find all .sol files in the given folder and its subfolders, excluding specified directories
find "$folder_path" -type d \( -name interfaces -o -name mock -o -name test \) -prune -o -name "*.sol" -print > "$files_list"

# Process each file
while IFS= read -r file; do
    process_file "$file" >> "$results"
done < "$files_list"

# Sort the results alphabetically
sort "$results" > "$sorted_results"

# Display the sorted results and calculate the total
total_count=0
while IFS='|' read -r filename count; do
    echo "File: $filename - $count lines of assembly code"
    total_count=$((total_count + count))
done < "$sorted_results"

# Remove temporary files
rm "$files_list" "$results" "$sorted_results"

echo "Total assembly lines across all .sol files (excluding interfaces, mock, and test directories): $total_count"