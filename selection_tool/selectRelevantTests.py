from parsePR import ParsePR
from useCoverageData import CoverageData
from helper_functions import *

class SelectRelevantTests:
    def __init__(self):
        print('Starting PR Parsing...')
        self.parser = ParsePR()
        print('PR Parsing finished successfully!')
        self.call_coverage_decision_tool()

    def call_coverage_decision_tool(self):
        input_for_coverage_tool = self.parser.collected_changes
        print("Changed files ", self.parser.changed_files)
        print("Collected changes relevant for Code Coverage Tool")
        print(input_for_coverage_tool)
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
            print("Write selected tests to a file {}".format(file_name))
            try:
                with open(file_name, 'w') as file:
                    for test in list_of_tests:
                        file.write(f"{test}\n")
                    print("Successfully wrote {} tests to {}".format(len(list_of_tests), file_name))
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Tool for Selecting Relevant Tests selected all tests")
        print('###################################')


if __name__ == '__main__':
    stage = SelectRelevantTests()
