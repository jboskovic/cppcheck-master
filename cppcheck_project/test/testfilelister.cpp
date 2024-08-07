/*
 * Cppcheck - A tool for static C/C++ code analysis
 * Copyright (C) 2007-2024 Cppcheck team.
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

#include "filelister.h"
#include "filesettings.h"
#include "path.h"
#include "pathmatch.h"
#include "fixture.h"
#include "testmacros.h"

#include <algorithm>
#include <cstddef>
#include <list>
#include <stdexcept>
#include <string>
#include <vector>
#include <utility>

class TestFileLister : public TestFixture {
public:
    TestFileLister() : TestFixture("TestFileLister") {}

private:
    void run() override {
        TEST_CASE(recursiveAddFiles);
        TEST_CASE(recursiveAddFilesEmptyPath);
        TEST_CASE(excludeFile1);
        TEST_CASE(excludeFile2);
    }

    // TODO: generate file list instead
    static std::string findBaseDir() {
        std::string basedir;
        while (!Path::isDirectory(Path::join(basedir, ".github"))) {
            const std::string abspath = Path::getAbsoluteFilePath(basedir);
            basedir += "../";
            // no more going up
            if (Path::getAbsoluteFilePath(basedir) == abspath)
                throw std::runtime_error("could not find repository root directory");
        }
        return basedir;
    }

    void recursiveAddFiles() const {
        const std::string adddir = findBaseDir() + ".";

        // Recursively add add files..
        std::list<FileWithDetails> files;
        std::vector<std::string> masks;
        PathMatch matcher(std::move(masks));
        std::string err = FileLister::recursiveAddFiles(files, adddir, matcher);
        ASSERT_EQUALS("", err);

        ASSERT(!files.empty());

#ifdef _WIN32
        std::string dirprefix;
        if (adddir != ".")
            dirprefix = adddir + "/";
#else
        const std::string dirprefix = adddir + "/";
#endif

        const auto find_file = [&](const std::string& name) {
            return std::find_if(files.cbegin(), files.cend(), [&name](const FileWithDetails& entry) {
                return entry.path() == name;
            });
        };

        // Make sure source files are added..
        ASSERT(find_file(dirprefix + "cli/main.cpp") != files.end());
        ASSERT(find_file(dirprefix + "lib/token.cpp") != files.end());
        ASSERT(find_file(dirprefix + "lib/tokenize.cpp") != files.end());
        ASSERT(find_file(dirprefix + "gui/main.cpp") != files.end());
        ASSERT(find_file(dirprefix + "test/testfilelister.cpp") != files.end());

        // Make sure headers are not added..
        ASSERT(find_file(dirprefix + "lib/tokenize.h") == files.end());
    }

    void recursiveAddFilesEmptyPath() const {
        std::list<FileWithDetails> files;
        const std::string err = FileLister::recursiveAddFiles(files, "", PathMatch({}));
        ASSERT_EQUALS("no path specified", err);
    }

    void excludeFile1() const {
        const std::string basedir = findBaseDir();

        std::list<FileWithDetails> files;
        std::vector<std::string> ignored{"lib/token.cpp"};
        PathMatch matcher(ignored);
        std::string err = FileLister::recursiveAddFiles(files, basedir + "lib/token.cpp", matcher);
        ASSERT_EQUALS("", err);
        ASSERT(files.empty());
    }

    void excludeFile2() const {
        const std::string basedir = findBaseDir();

        std::list<FileWithDetails> files;
        std::vector<std::string> ignored;
        PathMatch matcher(ignored);
        std::string err = FileLister::recursiveAddFiles(files, basedir + "lib/token.cpp", matcher);
        ASSERT_EQUALS("", err);
        ASSERT_EQUALS(1, files.size());
        ASSERT_EQUALS(basedir + "lib/token.cpp", files.begin()->path());
    }

    // TODO: test errors
};

REGISTER_TEST(TestFileLister)
REGISTER_TEST_CLASS(TestFileLister)
