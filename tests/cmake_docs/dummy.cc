#include "sample header with spaces.h"
#include "sample_header_2.h"
#include "my_module_docs.h"
#include <iostream>

// This is not a real pybind11 module. It is just some dummy code so we can test out
// running pybind11-mkdoc.

int method1(std::vector<float>, std::map<std::string,std::string>) {return 0;}

void method2(int p1, int p2){
    std::cout << DOC(Base, method2) << std::endl;
}
