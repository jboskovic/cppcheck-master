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
        self.write_selected_test_to_file(self.coverage_tool.output)
    
    def write_selected_test_to_file(self, list_of_tests):
        if list_of_tests != ["all"]:
            file_name = project_name + "/selected_tests.txt"
            file_for_evaluation = f"/var/jenkins_home/selections/selected_tests_{self.sha}.txt"
            print("Write selected tests to a file {}".format(file_name))
            try:
                with open(file_name, 'w') as file:
                    for test in list_of_tests:
                        file.write(f"{test}\n")
                    print("Successfully wrote {} tests to {}".format(len(list_of_tests), file_name))
                with open(file_for_evaluation, 'w') as file:
                    for test in list_of_tests:
                        file.write(f"{test}\n")
                    print("Successfully wrote {} tests to {}".format(len(list_of_tests), file_for_evaluation))
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Tool for Selecting Relevant Tests selected all tests")
        print('###################################')


if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    stage = SelectRelevantTests(args.sha)
