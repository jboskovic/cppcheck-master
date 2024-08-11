from helper_functions import *
import os
import re


class ParsePR:
    def __init__(self):
        self.baseline = self.get_baseline_of_PR()
        self.collected_changes = self.get_changes_from_PR((".cpp", ".h", ".c"))
        self.changed_files = self.get_changed_files_from_PR()
        self.changed_lines = self.get_changed_lines_from_PR((".cpp", ".h", ".c"))

    def get_baseline_of_PR(self):
        try:
            git_baseline_call = subprocess_call(
                'git log -n 1 `git merge-base origin/main HEAD`  --format=format:%H')
        except Exception as e:
            exit_with_message(f'Getting baseline of the PR failed with {e}')
        return git_baseline_call.stdout

    def get_changed_files(self):
        try:
            changed_files_call = subprocess_call(
                'git --no-pager diff --name-only `git merge-base origin/main HEAD`')
        except Exception as e:
            exit_with_message(f'Getting changed files with diff failed with {e}')

        changed_files = changed_files_call.stdout.strip().split('\n')
        if changed_files == []:
            print("List of changed files is empty")
            return []
        updated_changed_files = []
        for f in changed_files:
            if os.path.exists(f):
                updated_changed_files.append(f)
        return updated_changed_files

    def check_if_ext(self, file_path_string, extensions):
        if file_path_string.endswith(extensions):
            return True
        return False

    # removes files that are .cpp and .npl
    def get_changed_files_filtered(self, changed_files):
        changed_files_filtered = []
        for file in changed_files:
            if self.check_if_ext(file, ('.h', '.cpp')):
                # this type of files are already given CoverageTool
                continue
            changed_files_filtered.append(file)
        return changed_files_filtered

    def get_changed_files_from_PR(self):
        changed_files = self.get_changed_files()
        return self.get_changed_files_filtered(changed_files)

    def get_changes_from_PR(self, coverage_extensions):
        git_diff_output_file = 'git_diff_output.txt'
        try:
            subprocess_call(
                'git --no-pager diff --ignore-space-change --ignore-blank-lines --unified=0 `git merge-base origin/main HEAD` -- \'*.cpp\' \'*.h\' \'*.c\' > {}'.format(git_diff_output_file))
        except Exception as e:
            exit_with_message(f"Getting chagned files from PR failed {e}")

        file_name = ''
        file_is_covered_with_coverage = False
        # for each type of change map files to changed stuff in it
        collected_changes = {
            "functions": {},
            "others": {},
            "has_h_changes_without_cpp_changes": None}

        with open(git_diff_output_file, 'r') as changes:
            for line in changes:
                line = line.strip()
                if line.startswith('+++ '):
                    file_name = line.split('+++ ')[1][2:].strip()
                    if not self.check_if_ext(file_name, coverage_extensions):
                        file_is_covered_with_coverage = False
                    else:
                        file_is_covered_with_coverage = True
                elif ' @@ ' in line and file_is_covered_with_coverage:
                    change = line.split(' @@ ')[1].strip()

                    index_of_curly_bracket = change.find('{')
                    if index_of_curly_bracket != -1:
                        # skip namespace change
                        if 'namespace {' in change:
                            print("Parser collected change in the namespace. Continue")
                            continue
                        # remove curly bracket
                        change = change[:index_of_curly_bracket]

                    change = change.strip()
     
                    if file_name.endswith('.cpp') or file_name.endswith('.c'):
                        collected_changes['has_h_changes_without_cpp_changes'] = False
                        if '(' in change:
                            change = change.split('(')[0]
                    else:
                        if collected_changes['has_h_changes_without_cpp_changes'] is None:
                            collected_changes['has_h_changes_without_cpp_changes'] = True
                        if '(' in change:
                            change = change.split('(')[0]
                    if file_name not in collected_changes['functions']:
                        collected_changes['functions'][file_name] = [change]
                    else:
                        collected_changes['functions'][file_name].append(change)
                    

        self.remove_duplicates_from_collected_changes(collected_changes)
        if collected_changes['has_h_changes_without_cpp_changes'] is None or collected_changes['functions'] != {}:
            collected_changes['has_h_changes_without_cpp_changes'] = False

        return collected_changes

    def get_changed_lines_from_PR(self, coverage_extensions):
        try:
            output = subprocess_call(
                'git --no-pager diff --ignore-space-change --ignore-blank-lines --unified=0 `git merge-base origin/main HEAD` -- \'*.cpp\' \'*.h\' \'*.c\'')
        except Exception as e:
            exit_with_message(f"Getting chagned files from PR failed {e}")


        # Regex patterns to match file headers and hunks
        file_header_pattern = re.compile(r"^diff --git a/(.*) b/(.*)")
        hunk_header_pattern = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")

        current_file = None
        changed_lines = defaultdict(list)

        # Parse the git diff output
        for line in output.stdout.splitlines():
            file_match = file_header_pattern.match(line)
            if file_match:
                current_file = file_match.group(2)
                continue

            hunk_match = hunk_header_pattern.match(line)
            if hunk_match and current_file:
                start_line = int(hunk_match.group(1))
                num_lines = int(hunk_match.group(2) or 1)
                for i in range(start_line, start_line + num_lines):
                    changed_lines[current_file].append(i)

        print("Changed lines ", changed_lines)
        return changed_lines

    def remove_duplicates_from_collected_changes(self, collected_changes):
        for type_of_change in ['functions', 'others']:
            for file_name in collected_changes[type_of_change].keys():
                collected_changes[type_of_change][file_name] = list(set(collected_changes[type_of_change][file_name]))

