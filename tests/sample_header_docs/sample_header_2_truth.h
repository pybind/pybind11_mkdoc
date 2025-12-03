/*
  This file contains docstrings for use in the Python bindings.
  Do not edit! They were automatically extracted by pybind11_mkdoc.
 */

#define MKD_EXPAND(x)                                      x
#define MKD_COUNT(_1, _2, _3, _4, _5, _6, _7, COUNT, ...)  COUNT
#define MKD_VA_SIZE(...)                                   MKD_EXPAND(MKD_COUNT(__VA_ARGS__, 7, 6, 5, 4, 3, 2, 1, 0))
#define MKD_CAT1(a, b)                                     a ## b
#define MKD_CAT2(a, b)                                     MKD_CAT1(a, b)
#define MKD_DOC1(n1)                                       mkd_doc_##n1
#define MKD_DOC2(n1, n2)                                   mkd_doc_##n1##_##n2
#define MKD_DOC3(n1, n2, n3)                               mkd_doc_##n1##_##n2##_##n3
#define MKD_DOC4(n1, n2, n3, n4)                           mkd_doc_##n1##_##n2##_##n3##_##n4
#define MKD_DOC5(n1, n2, n3, n4, n5)                       mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5
#define MKD_DOC7(n1, n2, n3, n4, n5, n6, n7)               mkd_doc_##n1##_##n2##_##n3##_##n4##_##n5##_##n6##_##n7
#define DOC(...)                                           MKD_EXPAND(MKD_EXPAND(MKD_CAT2(MKD_DOC, MKD_VA_SIZE(__VA_ARGS__)))(__VA_ARGS__))

#if defined(__GNUG__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wunused-variable"
#endif


static const char *mkd_doc_Base = R"doc(A simple base class.)doc";

static const char *mkd_doc_Base_method1 =
R"doc(Description for method1.

This is the extended description for method1.

Args:
    p1: I am the first parameter.
    p2: I am the second parameter.

Returns:
    An integer is what I return.

Raises:
    runtime_error: Throws runtime error if p1 is empty.)doc";

static const char *mkd_doc_Base_method2 =
R"doc(Description for method1.

This is the extended description for method1.

Args:
    p1: I am a very long description for parameter 1. Let's ensure
        that this gets wrapped properly.
    p2: I am a very long descripton for paramet 2. However, I'm broken
        out onto two lines. Will this be parsed correctly?

Returns:
    An integer is what I return.

Raises:
    runtime_error: Throws runtime error if p1 is 0.
    invalid_argument: Throws invalid_argument error if p2 is 0.)doc";

#if defined(__GNUG__)
#pragma GCC diagnostic pop
#endif

