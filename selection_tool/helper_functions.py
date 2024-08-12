import sys
import subprocess as sp
import json

project_name = "cppcheck_project"

def subprocess_call(command):
    try:
        proc = sp.run(command, shell=True, stderr=sp.PIPE, stdout=sp.PIPE, encoding="UTF-8")
        if proc.stderr != '':
            print(proc.stderr)
    except Exception as e:
        raise e
    return proc

def exit_with_message(message):
    print(message)
    sys.exit(1)

def write_json(nfile, data):
    with open(nfile, "w") as f:
        json.dump(data, f)

def read_json(nfile):
    try:
        with open(nfile, "r") as read_content:
            return json.loads(read_content.read())
    except FileNotFoundError:
        print("Failed while reading file ", nfile)
        return {}
    
def read_file(nfile):
    try:
        with open(nfile, "r") as read_content:
            return read_content.read()
    except FileNotFoundError as e:
        print("Failed while reading file", nfile)
        print(e)
        return ""
    except Exception as e:
        print(f"An error occurred while reading file {nfile}: {e}")
        return ""