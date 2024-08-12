from parsePR import ParsePR
from useCoverageData import CoverageData
from helper_functions import *
import argparse

def parse_args(command_line_options):

    argparser = argparse.ArgumentParser(description='Arguments for Select Relevant Tests script')
    argparser.add_argument('--sha', dest='sha', type=str, action='store', help="Set sha for which we are running the PR selection")
    return argparser.parse_args(command_line_options)


class SelectRelevantTests:
    def __init__(self, sha):
        self.sha = sha
        print('Starting PR Parsing...')
        self.parser = ParsePR()
        print('PR Parsing finished successfully!')
        self.call_coverage_decision_tool()

    def call_coverage_decision_tool(self):
        input_for_coverage_tool = self.parser.collected_changes
        print('\n###################################')
        print('Coverage decision tool run start...')
        print('###################################\n')
        self.coverage_tool = CoverageData(input_for_coverage_tool, self.parser.baseline)
        print("Coverage decision tool run finished successfully!\n")
        print('###################################')
        print("Selecteed tests")
        print(self.coverage_tool.output)
        print('###################################')
        self.write_selected_test_to_file()
        self.write_to_files_evaluation_data()
    
    def write_selected_test_to_file(self):
        if self.coverage_tool.output != ["all"]:
            file_name = project_name + "/selected_tests.txt"
            print("Write selected tests to a file {}".format(file_name))
            try:
                with open(file_name, 'w') as file:
                    for test in self.coverage_tool.output:
                        file.write(f"{test}\n")
                    print("Successfully wrote {} tests to {}".format(len(self.coverage_tool.output), file_name))
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Tool for Selecting Relevant Tests selected all tests")
        print('###################################')

    def write_to_files_evaluation_data(self):
        file_for_evaluation = f"/var/jenkins_home/selections/selected_tests_{self.sha}.txt"
        print("Write selected tests to a file {}".format(file_for_evaluation))
        try:
            with open(file_for_evaluation, 'w') as file:
                for test in self.coverage_tool.output:
                    file.write(f"{test}\n")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        print("Write changed files and lines to a file {}".format(file_for_evaluation))
        file_with_changes = f"/var/jenkins_home/changes/changed_lines_{self.sha}.txt"
        write_json(file_with_changes, self.parser.changed_lines)
        print('###################################')


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    stage = SelectRelevantTests(args.sha)
