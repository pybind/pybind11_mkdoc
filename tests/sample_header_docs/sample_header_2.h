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
     */
    int method1(std::vector<float> p1, std::map<std::string,std::string> p2);
};
