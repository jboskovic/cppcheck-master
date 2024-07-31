from multiprocessing import Manager, Queue, Lock
from queue import Empty
from datetime import datetime
import os
from selection_tool.helper_functions import subprocess_call, exit_with_message, write_json



coverage_location_jenkins_path_base = '/var/jenkins_home/collections/'

def format_git_sha_date(sha):
    try:
        date_of_sha_output = subprocess_call(
            'TZ=UTC git show --quiet --date=\'format-local:%Y-%m-%d %H:%M:%S\'  --format=\"%cd\" {}'.format(sha)).stdout.strip()
        date_of_sha = date_of_sha_output.replace(' ', '-')
        return date_of_sha
    except Exception as e:
        exit_with_message(f"Formating git sha and date failed with {e}")

class Storage:

    def __init__(self, tests, sha):
        self._sha = sha
        self._manager = Manager()

        self._tests_indexed = self._manager.dict()
        self.set_indices_for_tests(tests)
        self._list_of_tests_to_collect = Queue()
        [self._list_of_tests_to_collect.put(line) for line in tests]

        self.init_dict_for_collection()
        self.init_dict_for_names()
        self.init_indices()
        self.init_locks()

    # multiprocessing safe dictionaries  that store test to type of data (function, control, table) per file
    def init_dict_for_collection(self):
        self._test_to_functions_per_file = self._manager.dict()

    # multiprocessing safe dictionaries that store names indexed
    def init_dict_for_names(self):
        self._functions_indexed = self._manager.dict()
        self._files_indexed = self._manager.dict()

    def init_indices(self):
        self._last_index_for_function = self._manager.Value('i', 0)
        self._last_index_for_file = self._manager.Value('i', 0)

    # locks for indexing functions/controls/tables and files
    def init_locks(self):
        self.lock_function = Lock()
        self.lock_file = Lock()

    # function is used for getting the test from the queue that is next for collecting data from
    def get_test(self):
        try:
            test = self._list_of_tests_to_collect.get(timeout=15)
            return test
        except Empty:
            return "empty"

    # creates directory where to store collected data
    # "branch_name"/yy-mm-dd-hh:mm:ss_sha_sha_name/tmp_"device_name"/
    # after collection is completed rename to be without tmp_
    # example master/2022-12-11-12:33:43_sha_1483ddbi33290u/gibraltar
    # if to_jenkins is set created directory is saved on Jenkins path
    # else saved locally
    def make_directory_for_this_run_date_form(self):
        # format yy-mm-dd-hh:mm:ss
        date_of_sha = format_git_sha_date(self._sha)
        format_for_directory =  date_of_sha + '_sha_' + self._sha

        print(coverage_location_jenkins_path_base)
        print(format_for_directory)
        self.dir_name_tmp = "{}/main/tmp_{}/".format(coverage_location_jenkins_path_base,
                                                    format_for_directory)
        self.dir_name = "{}/main/{}".format(coverage_location_jenkins_path_base,
                                            format_for_directory)

        print("Name of the directory {} where to store collection for the sha {} ".format(self.dir_name_tmp, self._sha))
        os.makedirs(self.dir_name_tmp, exist_ok=True)

    def set_indices_for_tests(self, tests):
        index = 0
        for test in tests:
            index += 1
            self._tests_indexed[test] = index

    def get_functions_for_test(self, test):
        if test not in self._tests_indexed:
            print("Test is not in the mapping ", test)
            return None

        index = self._tests_indexed[test]
        if index not in self._test_to_functions_per_file:
            print("No data for test ", test, " with index ", index)
            return None

        return self._test_to_functions_per_file[index]

    def insert_function_indexed(self, functions):
        list_of_indexes = []
        for fun in functions:
            if fun not in self._functions_indexed:
                with self.lock_function:
                    self._last_index_for_function.value += 1
                    self._functions_indexed[fun] = self._last_index_for_function.value
                list_of_indexes.append(self._last_index_for_function.value)
            else:
                list_of_indexes.append(self._functions_indexed[fun])

        return list_of_indexes

    def insert_file_indexed(self, file):
        if file not in self._files_indexed:
            with self.lock_file:
                self._last_index_for_file.value += 1
                self._files_indexed[file] = self._last_index_for_file.value

        return self._files_indexed[file]

    # for test insert dict that maps file to list of functions used in it
    def set_functions_per_file_for_test(self, test, file, functions):
        if test not in self._tests_indexed:
            print('Test is not in the mapping ', test)
            return None

        if functions == []:
            return

        fun_indices = self.insert_function_indexed(functions)
        file_index = self.insert_file_indexed(file)

        if fun_indices == []:
            return

        index_test = self._tests_indexed[test]
        if index_test not in self._test_to_functions_per_file:
            self._test_to_functions_per_file[index_test] = dict()

        copy_of_dict = self._test_to_functions_per_file[index_test]
        if file_index not in copy_of_dict:
            copy_of_dict[file_index] = fun_indices
        else:
            copy_of_dict[file_index] = copy_of_dict[file_index] + fun_indices

        self._test_to_functions_per_file[index_test] = copy_of_dict

    # from mapping test to files to functions revert it to be a mapping file to functions to tests (same for controls and tables)
    def revert_map(self, map_test_to_data):
        map_data_to_tests = dict()
        map_test_to_data = dict(map_test_to_data)
        for test, files_to_functions in map_test_to_data.items():
            for file_name, functions in files_to_functions.items():
                if file_name not in map_data_to_tests:
                    map_data_to_tests[file_name] = dict()
                    for fun in functions:
                        map_data_to_tests[file_name][fun] = [test]
                else:
                    for fun in functions:
                        if fun not in map_data_to_tests[file_name]:
                            map_data_to_tests[file_name][fun] = [test]
                        else:
                            map_data_to_tests[file_name][fun].append(test)

        return map_data_to_tests

    # save dictionaries to a separate json files on local and jenkins location
    def save_data(self):
        # create a direcotry where to store the collection
        self.make_directory_for_this_run_date_form()

        test_indexed = dict(self._tests_indexed)
        files_indexed = dict(self._files_indexed)
        write_json('{}/test_indexed.json'.format(self.dir_name_tmp), test_indexed)
        write_json('{}/files_indexed.json'.format(self.dir_name_tmp), files_indexed)

 
        data_index = dict(self._functions_indexed)
        data_reverted = self.revert_map(self._test_to_functions_per_file)


        write_json('{}/functions_indexed.json'.format(self.dir_name_tmp), data_index)
        write_json('{}/functions_to_tests.json'.format(self.dir_name_tmp), data_reverted)

        print("Saving data is finished. Rename dir {} to {}".format(self.dir_name_tmp, self.dir_name))
        try:
            subprocess_call('mv {} {}'.format(self.dir_name_tmp, self.dir_name))
        except Exception as e:
            exit_with_message(f'Renaming data base from {self.dir_name_tmp} to {self.dir_name} failed with {e}')
