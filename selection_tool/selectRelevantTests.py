from parsePR import ParsePR
from useCoverageData import CoverageData
from ..coverage_tool.helper_functions import *
import argparse
import sys

def parse_args(command_line_options):

    argparser = argparse.ArgumentParser(description='Run select relevant tests for branch')
    argparser.add_argument(
        '--branch-name',
        dest='branch_name',
        type=str,
        default="master",
        action='store',
        help="Define branch name")
    argparser.add_argument(
        '--root-dir',
        dest='root_dir',
        type=str,
        action='store',
        help="Insert the root directory for saving stage results.")
    argparser.add_argument(
        '--title',
        dest='title',
        type=str,
        action='store',
        help="Insert the current PR title.")

    return argparser.parse_args(command_line_options)

class SelectRelevantTests:
    def __init__(self, branch_name, root_dir, title):
        self.branch_name = branch_name
        print('Starting PR Parsing...')
        self.parser = ParsePR(self.branch_name)
        print('PR Parsing finished successfully!')
        self.call_coverage_decision_tool()

    def call_coverage_decision_tool(self):
        input_for_coverage_tool = self.parser.collected_changes
        print('\n###################################')
        print('Coverage decision tool run start...')
        print('###################################\n')
        self.coverage_tool = CoverageData(input_for_coverage_tool, self.parser.baseline, self.branch_name, False)
        print("Coverage decision tool run finished successfully!\n")
        print('###################################')



if __name__ == '__main__':
    args = parse_args(sys.argv[1:])
    stage = SelectRelevantTests(args.branch_name, args.root_dir, args.title)
