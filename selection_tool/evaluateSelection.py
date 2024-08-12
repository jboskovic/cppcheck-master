import argparse
import sys
from helper_functions import *
from coverage_tool.storage import format_git_sha_date, coverage_location_jenkins_path_base


def parse_args(command_line_options):

    argparser = argparse.ArgumentParser(description='Arguments for Evaluation script')
    argparser.add_argument('--sha', dest='sha', type=str, action='store', help="Set sha for which we are running the PR evaluation")
    argparser.add_argument('--branch-name', dest='branch_name', type=str, action='store', help="Set branch name for which we are running the PR evaluation")

    return argparser.parse_args(command_line_options)

if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    file_with_changes = f"/var/jenkins_home/changes/changed_lines_{args.sha}.txt"
    file_with_selected_tests = f"/var/jenkins_home/selections/selected_tests_{args.sha}.txt"
    changed_lines = read_json(file_with_changes)
    selected_tests = read_file(file_with_selected_tests)

    date_of_sha = format_git_sha_date(args.sha)
    format_for_directory =  date_of_sha + '_sha_' + args.sha

    coverage_location_for_branch = coverage_location_jenkins_path_base + '/' + args.branch_name + '/' + format_for_directory
    print("Read from ", coverage_location_for_branch)
    lines_to_tests_file = read_json(coverage_location_for_branch + "/lines_to_tests.json")
    files_indexed_files = read_json(coverage_location_for_branch + "/files_indexed.json")
    tests_indexed_filles = read_json(coverage_location_for_branch + "/test_indexed.json")
    covered_tests = []
    for file, lines in changed_lines.items():
        file_indexed  = None
        if file not in files_indexed_files:
            print(f"File {file} doesnt have coverage")
            continue
        else:
            file_indexed = str(files_indexed_files[file])
        
        lines_to_tests = None
        if file_indexed not in lines_to_tests_file:
            print(f"File {file} is not covered by lines")
            continue
        else:
            lines_to_tests = lines_to_tests_file[file_indexed]

        covered_tests.extend(lines_to_tests)

    covered_tests_names = []
    for test, index in tests_indexed_filles.items():
        if index in covered_tests:
            covered_tests_names.append(test)

    print("Selected tests")
    print(test)



