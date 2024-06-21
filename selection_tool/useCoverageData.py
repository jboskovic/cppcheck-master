from ..coverage_tool.helper_functions import *
import os
from pathlib import Path
from ..coverage_tool.storage import format_git_sha_date, coverage_location_jenkins_path_base
from datetime import datetime, timedelta

def convert_string_to_datetime(date_string):
    # format of the string 2022-12-20-20:15:03
    datetime_object = datetime.strptime(date_string, '%Y-%m-%d-%H:%M:%S')
    return datetime_object

def get_name_of_directories_in_directory(directory):
    directories_names = []

    for name in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, name)):
            directories_names.append(name.strip())

    return directories_names


def get_all_directories_on_jenksins_for_branch(branch_name):
    coverage_location_for_branch = coverage_location_jenkins_path_base + '/' + branch_name
    isExist = os.path.exists(coverage_location_for_branch)
    if isExist:
        shas_from_directory = get_name_of_directories_in_directory(coverage_location_for_branch)
        return shas_from_directory
    else:
        print("Directory for branch {} doesn't exit".format(branch_name))
        return None

def is_date_older_then_limit(collection_date, pr_date, limit):
    if (pr_date - collection_date) >= timedelta(limit):
        return True
    else:
        return False


class CoverageData:
    def __init__(self, changes_map, baseline, branch_name):
        self.changes_map = changes_map
        self.branch_name = branch_name
        self.baseline = baseline

        self.supported_branches = ['master']
        # limitation is in days
        self.LIMIT_FOR_AGE_OF_COLLECTION = 14

        self.changed_files_with_coverage_output = []

        self.default_empty_output = []

        self.default_output = ["type" : "all"]

        self.representative_tests = 'representative tests'

        self.output = self.get_relevant_tests()
        self.update_changed_files_without_coverage_output()

    def get_relevant_tests(self):
        if self.branch_name not in self.supported_branches:
            print(
                "Target branch {} is not supported branch {}. Run everything.".format(
                    self.branch_name,
                    self.supported_branches))
            return self.default_output
        if not self.has_list_of_changes():
            print("No changes in relevant covered files. Nothing to be run using Coverage Data")
            return self.default_empty_output
        elif self.changes_map["has_h_changes_without_cpp_changes"]:
            print("PR has changes in .h and no changes in .cpp. Run everything")
            return self.default_output
        else:
            self.path_to_collection_dir = self.get_path_to_collection()
            print("Path to collection directory {}".format(self.path_to_collection_dir))
            # PR has changes in files that are covered with coverage
            return self.get_relevant_tests_using_coverage_collection()

    def update_changed_files_without_coverage_output(self):
        covered_files = list(set(self.changed_files_with_coverage_output))
        changed_files_in_PR = []
        file_to_changes_group = self.changes_map.values()
        for group in file_to_changes_group:
            if isinstance(group, dict):
                files = group.keys()
                changed_files_in_PR.extend(files)

        # remove residuals
        changed_files_in_PR = list(set(changed_files_in_PR))

        self.changed_files_without_coverage_output = []
        for changed_file in changed_files_in_PR:
            if changed_file not in covered_files:
                self.changed_files_without_coverage_output.append(changed_file)

    def has_list_of_changes(self):
        for type_name in ['functions', 'others']:
            if self.changes_map[type_name] != {}:
                return True
        return False

    # returns a mapping device to path_to_collection
    def get_path_to_collection(self):
        date_of_baseline_sha_string = format_git_sha_date(self.baseline)
        date_of_baseline_sha = convert_string_to_datetime(date_of_baseline_sha_string)
        print("Date {} for baseline {}".format(date_of_baseline_sha, self.baseline))

        directories_from_jenkins = get_all_directories_on_jenksins_for_branch(self.branch_name)
        if directories_from_jenkins is None:
            return None

        # sort directories by the date
        directories_with_collections_sorted = sorted(directories_from_jenkins, reverse=True)
        path_to_collections_dir = ''

        # find most recent date of the collection for each device
        for directory_for_collection_sha in directories_with_collections_sorted:
            date_of_collection_sha_string = directory_for_collection_sha.split('_sha_')[0]
            date_of_collection_sha = convert_string_to_datetime(date_of_collection_sha_string)

            if date_of_collection_sha <= date_of_baseline_sha:
                # collection should not be older then 2 weeks then PR
                if is_date_older_then_limit(
                        date_of_collection_sha,
                        date_of_baseline_sha,
                        self.LIMIT_FOR_AGE_OF_COLLECTION):
                    print(
                        "You reached searching for the collection to date that is older then {} days.".format(
                            self.LIMIT_FOR_AGE_OF_COLLECTION))
                    break
                directory_for_collection = coverage_location_jenkins_path_base + \
                    '/' + self.branch_name + '/' + directory_for_collection_sha


                if 'tmp_' in directory_for_collection:
                    print("Collection {} still not finished, search for next".format(directory_for_collection))
                    continue
            

        return path_to_collections_dir

    def read_json_collection_to_map(self):

        collection_mapped = {}
        for type_name in ['test', 'functions', 'files']:
            file_name = self.path_to_collection_dir + '/' + type_name + '_indexed.json'
            collection_indexed = read_json(file_name)
            if collection_indexed == {}:
                print("Collection has problem. File {} is empty.".format(file_name))
                return None
            if type_name != 'test' and type_name != 'files':
                file_name = self.path_to_collection_dir + '/' + type_name + '_to_tests.json'
                collection_mapping = read_json(file_name)
                if collection_mapping == {}:
                    print("Collection has problem. File {} is empty.".format(file_name))
                    return None
            else:
                collection_mapping = None

            collection_mapped[type_name] = {"index": collection_indexed, "mapping": collection_mapping}

        return collection_mapped

    def get_relevant_tests_using_coverage_collection(self):
        print("Implement getting relevant tests using coverage. Go through functions changed and select tests")
        return ''

    def make_test_paths(self, list_of_tests):
        list_of_test_paths = []
        for test in list_of_tests:
            list_of_test_paths.append({'type': 'test_path', 'data': test})
        return list_of_test_paths

    def get_relevant_tests_for_type(self, type_name):
        list_of_tests_need_for_run = []
        run_default = False
        for file_name, functions in self.changes_map[type_name].items():
            rel_file_name = self.relative_file_path(file_name, type_name)
            if rel_file_name is None:
                continue  # file is another device's specific file

            file_has_cov_output = False
            for func in functions:
                if type_name == 'functions' and 'enum ' in func or 'struct ' in func:
                    print("Change is in a structure or enum ", func)
                    file_has_cov_output = True
                    run_default = True
                    list_of_tests_need_for_run = [self.default_for_device]
                else:
                    func_indices = self.get_index_from_change_name(type_name, func)
                    if func_indices is None:
                        self.print_debug("Change {} of type {} is not indexed".format(func, type_name))
                        self.print_debug("For {} tests are not gonna be selected.".format(func))
                        continue
                    tests_to_run = self.get_list_of_tests_functions_from_file(type_name, func_indices, rel_file_name)
                    if len(tests_to_run) != 0:
                        file_has_cov_output = True
                    self.print_debug("Selected tests for this change {}".format(tests_to_run))
                    if not run_default:
                        list_of_tests_need_for_run += tests_to_run

            if file_has_cov_output:
                self.changed_files_with_coverage_output.append(file_name)

        return list_of_tests_need_for_run

    def get_list_of_tests_functions_from_file(self, type_of_collection, func_indices, file_name):
        # load map of file indices to function/control/table indices to list of indices of tests
        type_to_test_indexed_per_file = self.collection_map[type_of_collection]['mapping']
        selected_tests = []
        file_indices = self.get_index_from_change_name('files', file_name)
        file_index = None
        if file_indices is None:
            self.print_debug("File {} is not indexed".format(file_name))
            type_to_test_indexed = None
        else:
            if len(file_indices) != 1:
                print("File {} has more then one index found. List of found indices {}. Investigate.".format(file_name, file_indices))
            file_index = file_indices[0]

            if str(file_index) not in type_to_test_indexed_per_file:
                print("File {} is indexed but there isn't mapping from that file to functions and tests.".format(file_name))
                type_to_test_indexed = None
            else:
                type_to_test_indexed = type_to_test_indexed_per_file[str(file_index)]

        for index in func_indices:
            type_name = self.convert_index_to_name(type_of_collection, index)
            name_without_args = type_name
            if '(' in name_without_args:
                name_without_args = type_name.split('(')[0]

            if type_to_test_indexed is None:
                self.print_debug(
                    "Try searching by function index")
                tests_indexed = self.search_by_function_index(type_to_test_indexed_per_file, index)
            else:
                tests_indexed = type_to_test_indexed[str(index)]

            test_names = self.convert_test_indexed_to_test_name(tests_indexed)
            self.print_debug("Type {} with the name {} and index {} selected tests {}".format(
                type_of_collection, name_without_args, index, test_names))
            selected_tests += test_names

        # with the set remove duplicates of indices and return the list of it
        selected_tests = list(set(selected_tests))

        return selected_tests

    def search_by_function_index(self, type_to_test_indexed_per_file, index):
        tests_indexed = []
        for file_index, functions_to_test in type_to_test_indexed_per_file.items():
            if str(index) in functions_to_test:
                tests_indexed += functions_to_test[str(index)]

        return list(set(tests_indexed))

    # given a function/table/control change get index from a mapping
    # if name is not in the collection return None other return list of indices
    # we are looking for a substring in the colleciton
    def get_index_from_change_name(self, type_of_collection, change_name):
        # load map of function/control/table names to index for specific device
        type_to_index = self.collection_map[type_of_collection]['index']
        indices = []
        # collect indices which whole name of the function/table/control is similar to given name
        for whole_name, index in type_to_index.items():
            if type_of_collection == 'files':
                change_name = change_name.split('.')[0]
                if change_name == whole_name:
                    indices.append(index)
            # functions can be generic
            elif type_of_collection == 'functions':
                if change_name + '(' in whole_name or change_name + '<' in whole_name:
                    indices.append(index)
            else:
                # controls and tables
                if change_name in whole_name:
                    indices.append(index)

        if indices == []:
            return None

        return indices

    def convert_test_indexed_to_test_name(self, tests_indexed):
        test_names = []
        for test_index in tests_indexed:
            test_name = self.convert_index_to_name('test', test_index)
            if test_name == '':
                print('No test name for index ', test_index)
            else:
                if self.test_exist(test_name):
                    test_names.append(test_name)
                else:
                    print("Test with the name {} doesn't exist ".format(test_name))
        return test_names

    def convert_index_to_name(self, type_of_collection, index):
        # mapping of the function name to it's index
        type_to_index = self.collection_map[type_of_collection]['index']
        name = ''
        for type_name, type_index in type_to_index.items():
            if type_index == index:
                if name != '':
                    print("More {} with the index {}".format(type_of_collection, index))
                    print("Error with Jenkins Job collection. Bad multiprocessing operation.")
                name = type_name

        return name

    def print_debug(self, msg):
        if self.debug:
            print(msg)

    def test_exist(self, test_path):
        return os.path.isfile(test_path)