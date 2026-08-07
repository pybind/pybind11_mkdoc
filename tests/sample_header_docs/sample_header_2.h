#pragma once

#include <map>
#include <string>
#include <vector>

/**
 * @class Base
 * @brief A simple base class.
 */
class Base {
  public:
    /**
     * @brief Description for method1.
     *
     * This is the extended description for method1.
     *
     * @param p1 I am the first parameter.
     * @param p2 I am the second parameter.
     * @return An integer is what I return.
     *
     * @throws runtime_error Throws runtime error if p1 is empty.
     */
    int method1(std::vector<float> p1, std::map<std::string,std::string> p2);

    /**
     * @brief Description for method1.
     *
     * This is the extended description for method1.
     *
     * @param p1 I am a very long description for parameter 1. Let's ensure that this gets wrapped properly.
     * @param p2 I am a very long description for parameter 2.
     *           However, I'm broken out onto two lines. Will this be parsed correctly?
     *
     * @return An integer is what I return.
     *
     * @throw runtime_error Throws runtime error if p1 is 0.
     * @exception invalid_argument Throws invalid_argument error if p2 is 0.
     */
    void method2(int p1, int p2);

#ifdef MY_EXTRA_DEFINE
    /**
     * @brief A method that is only included if MY_EXTRA_DEFINE is defined.
     */
    void method3();
#endif

#ifdef MY_OTHER_DEFINE
    /**
     * @brief A method that is only included if MY_OTHER_DEFINE is defined.
     */
    void method4();
#endif
};
