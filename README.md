Templatizer
===========
Templatizer is a general purpose data-driven generator written in Python.

Getting Started
---------------

This short `guide` will help you get started with Templatizer in no time.

### Install

* `git clone git://github.com/icebreaker/templatizer.git`
* `cd templatizer`
* `sudo python setup.py install`

### Configure

Templatizer can be configured via `$HOME/.templatizer` which is a simple text file 
containing one `path` per line:

	~/cool-templates
	~/secret-project/templates

These paths are system-wide directories containing one or more Templatizer templates
and will be scanned when Templatizer is started.

### Templates

What would be Templatizer without templates? Nada.

Each template **MUST** have at least `descriptor` file with the `.templatizer` extension in addition
to any other files / directories in the template.

The `template descriptor` is light-weight JSON:

*(examples/test.templatizer)*

	{ 
		"name": "test",
		"actions":
		[	
			["%NAME-LOWCASE%.hpp","test/test.hpp"],
			["mkdir -p %NAME%","shell"]
		],
		"arguments":
		{
			"name": 
			{
				"%NAME%":"v",
				"%NAME-LOWCASE%":"v.lower()",
				"%NAME-UPCASE%":"v.upper()"
			},
			"namespace":
			{
				"%NAMESPACE%":"v",
				"%NAMESPACE-OPEN%":"v + '::'",
				"%NAMESPACE-INC%":"v.replace('::','/') + '/'"
			}
		},
		"constants":
		{
			"%MONTH%":"datetime.now().month"
		}
	}

* `name` is a unique name identifying this template, and it will be used when registering
* `actions` contains the files to be generated and shell commands `executed` in the order
they are listed; can contain variables or constants which will be substituted before execution
* `arguments` are "lambdas" and receive the value of the associated command line argument as parameter `v`;
each command line argument can have one or more associated `key => value` pairs
* `constants` are "lambdas" which evaluate to a `constant` value

There are a couple of *internal built-in constants* as follows:

* `%YEAR%` - current year
* `%DATE%` - current date in the format `%d/%m/%y`
* `%TPLDIR%` - absolute path to the `active` template's parent directory

### How to use?
Once you have at least one valid template, it's very easy to use and the results are generated
relative to the current directory.

	templatizer test --name=Hello --namespace=foundation::framework

### Available Templates
There's a repository where I'll share my general-purpose templates so be sure to check it out
for some real life examples by click right [here](https://github.com/icebreaker/Templatizer-Templates) .

TODO
----
* unit tests

Contribute
----------
* Fork the project.
* Make your feature addition or bug fix.
* Send me a pull request. Bonus points for topic branches.
* Do **not** bump the version number.

License
-------
Copyright (c) 2011, Mihail Szabolcs

Templatizer is provided **as-is** under the **GPL** license. For more information see LICENSE.
