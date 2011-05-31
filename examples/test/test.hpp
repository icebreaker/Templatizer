/*
	Copyright (c) 1987-%YEAR%, John Doe
	All rights reserved.

	Oh, %MONTH% is awesome.
*/
#ifndef %NAME-UPCASE%TEST_HPP
#define %NAME-UPCASE%TEST_HPP

#include "foundation/framework/test/test.hpp"
#include "%NAMESPACE-INC%%NAME-LOWCASE%.hpp"

namespace tests {

class %NAME%TestC : public TestC
{
public:
	void exec(void);
	const char *name(void) const;
};

inline
void %NAME%TestC::exec(void)
{
	TEST_ASSERT(1 == 1);
}

inline
const char *%NAME%TestC::name(void) const
{
	return "%NAMESPACE-OPEN%%NAME%C";
}

}

#endif
