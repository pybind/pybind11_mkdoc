#pragma once

/// First overload of foo.
void foo(int x);

/// Second overload of foo.
void foo(double x);

/// Third overload of foo.
void foo(char x);

/// A real symbol that clashes with the suffix of the second foo overload.
void foo_2();

/// A real symbol that clashes with the suffix of the third foo overload.
void foo_3();
