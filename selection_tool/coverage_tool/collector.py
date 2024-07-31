from multiprocessing import Process
import re
import queue
import time
import os
from ..helper_functions import subprocess_call, exit_with_message


class Collector:
    def __init__(self, storage, dont_delete_gcda, coverage_dir):
        self.delete_files_after_collecting = not dont_delete_gcda
        self._storage = storage
        self.gcda_dir = coverage_dir

    def run(self, number_of_processes):
        self.processes = []
        for i in range(0, number_of_processes):
            p = Process(target = self.collect_tests_parallel, daemon=True, args = [i])
            self.processes.append(p)
            p.start()
        self.wait_all_processes_to_finish()

    def wait_all_processes_to_finish(self):
        for p in self.processes:
            p.join()

        return True

    def collect_tests_parallel(self, process_id):
        self.process_id = process_id
        while True:
            test = self._storage.get_test()

            if test is None:
                print("Queue returned None. Process {} finished".format(self.process_id))
                return True
            if test == 'empty':
                print("Queue empty. Process {} finished".format(self.process_id))
                return True

            print('Process {} took test {}'.format(self.process_id, test))

            start_time = time.time()
            return_status = self.collect_data_from_test_file(test)

            if return_status is None:
                print("Error with the test ", test)

            end_time = time.time()
            print('Process ', self.process_id, 'time ', end_time - start_time)
    
    def get_relative_path_of_file(self, gcno_file_name):
        gcno_relative = gcno_file_name.split('cppcheck_project')[1]
        return gcno_relative

    def collect_data_from_test_file(self, test):
        # directory where .gcda files are stored for given test
        dir_name_with_tests_gcda_files = self.gcda_dir + '/' + test + '/'
        # for each .gcda file get directory where it's located and it's name
        gcno_files_list = self.get_gcno_files_path_list(dir_name_with_tests_gcda_files)

        if gcno_files_list is None:
            print("Skip calling gcov for test {}. Investigate why getting the .gcda file locaitons failed.".format(test))
            return None

        # for each file collect covered functions
        for gcno_file in gcno_files_list:
            gcno_file_name = gcno_file[0]

            file_name = self.get_relative_path_of_file(gcno_file_name)
            gcov_args = gcno_file[1]
            # call gcov per gcda file
            # -n no output file -f function summaries
            try:
                # TODO set gcov 
                output_from_gcda_file = subprocess_call(
                    "gcov -n -f {}".format(gcov_args))
            except Exception as e:
                exit_with_message(f'Running gcov for {gcov_args} failed with {e}')

            covered_functions = self.parse_output_from_gcda_file(output_from_gcda_file.stdout)

            self._storage.set_functions_per_file_for_test(test, file_name, covered_functions)

        # if self.delete_files_after_collecting:
        #     subprocess_call('rm -rf {}'.format(dir_name_with_tests_gcda_files))

        return True

    def parse_output_from_gcda_file(self, output_from_gcda_file):
        used_functions = []

        collect_string_after_Function_regex = re.compile('Function \'(.+)\n?\'\nLines executed:(?!0\.00%)')
        string_after_Function = collect_string_after_Function_regex.findall(output_from_gcda_file)

        for name in string_after_Function:
            name = name.strip()
            # functions are mangled in gcov -> demangle it with c++flit
            function_name = subprocess_call('c++filt {}'.format(name)).stdout.strip()
            used_functions.append(function_name)

        return used_functions

    # for all .gcda files inside the directory get absolute file name and it's dir location
    def get_gcno_files_path_list(self, dir_name_with_tests_gcda_files):
        try:
            subprocess_call(
                'find {} -iname "*.gcda\" | awk \'{{ system(\"dirname \" $1); print $1}}\' > gcda_{}.list '.format(
                    dir_name_with_tests_gcda_files, self.process_id))
        except Exception as e:
            exit_with_message(f"Creating arguments for gcov failed with {e}")

        file = open("gcda_{}.list".format(self.process_id), "r")
        gcda_file_path_and_dir = [line.strip() for line in file.readlines()]

        # pairs of lines [dir_path, absolurte_path]
        gcda_file_path_and_dir_pair = [gcda_file_path_and_dir[n:n + 2] for n in range(0, len(gcda_file_path_and_dir), 2)]

        # make symlink to representative .gcno files
        for line in gcda_file_path_and_dir_pair:
            # replace extention
            line[1] = line[1].replace('.gcda', '.gcno')
            # from path get location of the file in out directory
            gcno_file_path = self.get_relative_path_of_file(line[1])
            # make symbolic link to the .gcno file
            try:
                subprocess_call('ln -s {} {}'.format(os.getcwd() + '/' + gcno_file_path, line[0]))
            except Exception as e:
                exit_with_message(f'Creating symbolic link ln -s failed with {e}')

        # -o specific parent dir
        gcno_files_path_list = [[line[1][:-5], " -o " + line[0]  + " "  + line[1]] for line in gcda_file_path_and_dir_pair]
        return gcno_files_path_list
