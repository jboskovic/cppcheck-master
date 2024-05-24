import argparse
import time
import sys
import os

from storage import Storage
from collector import Collector

coverage_dir = 'coverage_per_test'

def parse_args(command_line_options):

    argparser = argparse.ArgumentParser(description='For executed test files run gcov')
    argparser.add_argument('--sha', dest='sha', type=str, action='store', help="Set sha for which we are running the collection")
    argparser.add_argument(
        '--branch-name',
        dest='branch_name',
        type=str,
        action='store',
        help="Define branch name, master or some lts branch")
    argparser.add_argument('-j', dest='j', type=int, default=1, action='store',
                           help="Define parallelization number")
    argparser.add_argument('--dont-delete-gcda-files', dest='dont_delete_gcda', action='store_true', default=False,
                           help="Don't delete gcda files after collection is finished")
    return argparser.parse_args(command_line_options)

def from_gcda_dir_path_collect_test_names():
    test_names = []

    for name in os.listdir(coverage_dir):
        if os.path.isdir(os.path.join(coverage_dir, name)):
            test_names.append(name.strip())

    return test_names


if __name__ == '__main__':
    time_for_collection_started = time.time()

    args = parse_args(sys.argv[1:])

    # get all executed test files
    tests = from_gcda_dir_path_collect_test_names()
    # object Storage is multiprocess safe and is used for storing collected data
    storage = Storage(tests, args.sha, args.branch_name)

    # object Collector is used for collecting the data in parallel
    collector = Collector(storage, args.dont_delete_gcda, coverage_dir)
    collector.run(args.j)

    # save collected data to json files in a directory that's named using sha and date of sha
    storage.save_data()

    time_for_collection_ended = time.time()
    end_time_for_collection = time_for_collection_ended - time_for_collection_started
    print("Collection completed. Took time {}".format(end_time_for_collection))
