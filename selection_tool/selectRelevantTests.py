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
        print("INPUT FOR coverage ", input_for_coverage_tool)
        print("CHanged files ", self.parser.changed_files)
        print('\n###################################')
        print('Coverage decision tool run start...')
        print('###################################\n')
        self.coverage_tool = CoverageData(input_for_coverage_tool, self.parser.baseline)
        print("Coverage decision tool run finished successfully!\n")
        print('###################################')
        print("Selecteed tests")
        print(self.coverage_tool.output)
        print('###################################')


if __name__ == '__main__':
    stage = SelectRelevantTests()
