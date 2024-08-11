from multiprocessing import Process
import time
import os
import json
from helper_functions import subprocess_call, exit_with_message


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
    
    def collect_data_from_test_file(self, test):
        # directory where .gcda files are stored for given test
        dir_name_with_tests_gcda_files = self.gcda_dir + '/' + test + '/'
        files_lines = {}
        files_functions = {}
        self.create_gcno_symlinks(dir_name_with_tests_gcda_files)
        command = "cd {} &&  find . -name '*.gcno' -print0 | xargs -0 -I{{}} gcov -tir {{}} 2>/dev/null".format(dir_name_with_tests_gcda_files)
        for json_string in os.popen(command):
            print("Json String ", json_string)
            output_functions, output_lines = self.parse_full_json_object(json_string)
            print("functions output ", output_functions)
            print("lines output ", output_lines)
            for file, list_of_lines in output_lines.items():
                if file not in files_lines:
                    files_lines[file] = list_of_lines
                else:
                    curent_lines = files_lines[file]
                    all_lines = list(set(curent_lines + list_of_lines))
                    files_lines[file] = all_lines

            for file, list_of_functions in output_functions.items():
                if file not in files_functions:
                    files_functions[file] = list_of_functions
                else:
                    curent_functions = files_functions[file]
                    all_functions = list(set(curent_functions + list_of_functions))
                    files_functions[file] = all_functions

        print("Functions ", files_functions)
        print("Lines ", files_functions)

        self._storage.set_functions_per_file_for_test(test, files_functions)
        self._storage.set_lines_per_file_for_test(test, files_lines)

        return True


    # parse the json object from the gcov output for one test and return a json of executed lines and functions per file
    def parse_full_json_object(self, json_object):
        new_json_object_lines = {}
        new_json_object_functions = {}

        executed_lines, functions = [], []
        json_object = json.loads(json_object)
        src_file_without_suffix = json_object['data_file'].strip('.gcno')
        for file_object in json_object['files']:
            file = file_object['file']
            print("File ", file)
            file_index = str(self._storage.insert_file_indexed(file))
            if file in  src_file_without_suffix:
                print("File in ", src_file_without_suffix)
                executed_lines = []
                functions = []

                for line_info in file_object['lines']:
                    if line_info['count'] > 0:
                        executed_lines.append(line_info['line_number'])

                for function_info in file_object['functions']:
                    if function_info['execution_count'] > 0:
                        function_name = function_info['demangled_name']
                        function_index = self._storage.insert_function_indexed(function_name)
                        functions.append(function_index)

                if executed_lines:
                    if file_index not in new_json_object_lines:
                        new_json_object_lines[file_index] = []
                    if file_index not in new_json_object_functions:
                        new_json_object_functions[file_index] = []
                    new_json_object_lines[file_index]= list(
                        set(executed_lines) | set(new_json_object_lines[file_index]))
                    new_json_object_functions[file_index] = list(
                        set(functions) | set(new_json_object_functions[file_index]))
                

        return new_json_object_functions, new_json_object_lines

    def create_gcno_symlinks(self, dir_name):
        command = f"cd {dir_name} && find . -name \"*.gcda\" -print0 | xargs -0 -I{{}} sh -c 'ln -sf /$(echo \"{{}}\" | sed 's/\.gcda$/.gcno/') $(echo \"{{}}\" | sed 's/\.gcda$/.gcno/')'"
        subprocess_call(command)


