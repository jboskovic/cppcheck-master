#ifndef TEST_MACROS_H
#define TEST_MACROS_H

#include "testregistry.h"

#define REGISTER_TEST_CLASS( CLASSNAME ) \
    namespace { \
        struct CLASSNAME##_Registrator { \
            CLASSNAME##_Registrator() { \
                TestRegistry::instance().addTestClass(#CLASSNAME); \
            } \
        }; \
        CLASSNAME##_Registrator instance_##CLASSNAME##_Registrator; \
    }

#endif // TEST_MACROS_H