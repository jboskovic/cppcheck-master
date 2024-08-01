#!/bin/bash

# Check if a file name is provided as an argument
if [ $# -eq 0 ]; then
    echo "Usage: $0 <file_with_test_names>"
    exit 1
fi

# File containing the list of test names
test_file=$1

# Check if the file exists
if [ ! -f "$test_file" ]; then
    echo "File not found: $test_file"
    exit 1
fi

# Initialize COVERAGE and CXX with default values
COVERAGE=0
CXX=g++

# Set COVERAGE and CXX based on provided arguments
if [ $# -ge 2 ]; then
  if [ "$2" == "coverage" ]; then
    COVERAGE=1
    if [ $# -ge 3 ]; then
      CXX=$3
    fi
  else
    CXX=$2
  fi
fi

# Read the file and call make test for each test name
while IFS= read -r test_name; do
    if [ -n "$test_name" ]; then
        echo "Running test: $test_name"
        make test COVERAGE="$COVERAGE" CXX="$CXX" TESTNAME="$test_name"
    fi
done < "$test_file"