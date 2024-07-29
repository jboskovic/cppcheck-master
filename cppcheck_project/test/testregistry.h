#ifndef TEST_REGISTRY_H
#define TEST_REGISTRY_H

#include <unordered_set>
#include <string>

class TestRegistry {
public:
    static TestRegistry& instance();

    void addTestClass(const std::string& testClassName);

    const std::unordered_set<std::string>& getTestClasses() const;

private:
    TestRegistry() = default;
    std::unordered_set<std::string> testClasses;
};

#endif // TEST_REGISTRY_H