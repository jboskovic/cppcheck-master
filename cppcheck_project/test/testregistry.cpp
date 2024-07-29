#include "testregistry.h"

TestRegistry& TestRegistry::instance() {
    static TestRegistry registry;
    return registry;
}

void TestRegistry::addTestClass(const std::string& testClassName) {
    testClasses.insert(testClassName);
}

const std::unordered_set<std::string>& TestRegistry::getTestClasses() const {
    return testClasses;
}