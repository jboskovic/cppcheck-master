/*
 * Cppcheck - A tool for static C/C++ code analysis
 * Copyright (C) 2007-2023 Cppcheck team.
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

#include "color.h"
#include "options.h"
#include "preprocessor.h"
#include "fixture.h"
#include "testregistry.h"

#include <cstdlib>
#include <iostream>


// Function to list all unique class names
void listAllClassNames() {
    const auto& classNames = TestRegistry::instance().getTestClasses();
    for (const auto& className : classNames) {
        std::cout << className << std::endl;
    }
}

int main(int argc, char *argv[])
{
    // MS Visual C++ memory leak debug tracing
#if defined(_MSC_VER) && defined(_DEBUG)
    _CrtSetDbgFlag(_CrtSetDbgFlag(_CRTDBG_REPORT_FLAG) | _CRTDBG_LEAK_CHECK_DF);
#endif

    Preprocessor::macroChar = '$';     // While macroChar is char(1) per default outside test suite, we require it to be a human-readable character here.
    gDisableColors = true;

    options args(argc, argv);

    if (args.help()) {
        TestFixture::printHelp();
        return EXIT_SUCCESS;
    }
    if (args.listClasses()) {  // Check for the new option
        listAllClassNames();
        return EXIT_SUCCESS;
    }
    const std::size_t failedTestsCount = TestFixture::runTests(args);
    return (failedTestsCount == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}