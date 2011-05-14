Templatizer
===========
Templatizer is a general purpose data-driven (**JSON**) light-weight generator written in Python.

Purpose
-------
It doesn't matter if you are using VI(m) as your IDE or something in the lines of Eclipse, at one point
or another you will want to be able to auto-create certain (more or less project dependent) structures 
skeletons, files, directories or you name it.

Templatizer's purpose is to solve this with mimimal friction and a fully data-driven architecture which
makes it possible to have project-agnostic templates, or project specific ones and yet generate them
using the very same interface and syntax.

There's no need for verbose and complicated XML template descriptors, 
JSON provides a minimal and explicit structure which is just as efficient and readable as pretty 
much any XML would be. Isn't that just lovely?

Getting Started
---------------

### Install

* clone (i.e `git clone git://github.com/icebreaker/templatizer.git`)
* symlink (i.e. `ln -s /path/to/templatizer.py /usr/bin/templatizer`)
* make it executable (i.e. `chmod +x /usr/bin/templatizer`)

### Configure

Templatizer can be configured via `$HOME/.templatizer` which is a simple JSON
structure with the following format:

	{
		"paths":["~/cool-templates","~/secret-project/templates"],
		"constants":
		{
			"%FULLNAME%":"'John Doe'",
			"%USERNAME%":"os.environ['USERNAME']",
			"%YEAR%":"datetime.now().year"
		}
	}

* `paths` are system-wide directories containing one or more templates.
* `constants` are basically "lambdas" which evaluate to a value, the constants defined here
can/will be overridden by any constants with the same name from any specific templates.

### Templates

What would be Templatizer without templates? Nada.

Each template must have at least `descriptor` file with the `.templatizer` extension in addition
to any other files / directories in the template.

The `template descriptor` just like the `config` file above follow the same concise and transparent JSON structure
and format:

*(examples/test.templatizer)*

	{ 
		"version":"10",
		"author":"John Doe",
		"description":"Basic skeleton for unit tests.",
		"name": "test",
		"package":
		[	
			["%NAME-LOWCASE%.hpp","test/test.hpp"],
			["BOOMTOWN/%NAME%","dir"],
			["mkdir -p %NAME%","shell"]
		],
		"variables":
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
			"%YEAR%":"datetime.now().year"
		}
	}

* `version`, `author` and `description` are optional (*for now*) but needless to say *nice-to-have*
* `name` is the actual name this template will be registered, duplicate names will trigger
a *WARNING* so they can be changed to something unique; also this is the first command line
argument you'll pass to Templatizer
* `package` contains the files, directories and shell commands, `executed` in the order
they are listed here, each can contain variables or constants which will be substituted
before `execution`
* `variables` are also lambdas and receive the associated command line argument as parameter `v`,
each command line argument can have one, or multiple variables associated with it
* `constants` are basically "lambdas" which evaluate to a value, the constants defined here
override the `constants` defined in the `global` Templatizer configuration file. For more
information please consult the **Configure** section above.

For the actual "template", take a look at `examples/test/test.hpp` which uses the variables and
constants defined in the `template descriptor` above.

### Run Templatizer, Run
Once you have at least one valid template, it's very very easy to use and the resulted files / directories
will be placed in the working directory.

`templatizer test --name=Hello --namespace=foundation::framework`

### Tips and Tricks
If a variable is ommitted in the command line it will be replaced with a harmless `EMPTY` string, making
it possible to implement *safe fallbacks* in the templates.

It is possible to pass in `--path=$HOME/mypath/templates` when executing Templatizer and it will load
all valid templates from the given path before generating anything.

If for some reason something goes wrong, or is not clear it is possible to pass `--verbose=X` where
`X` is a number, to increase the verbosity level and show more information. (the default is 1 [one])

Contribute
----------
* Fork the project.
* Make your feature addition or bug fix.
* Send me a pull request. Bonus points for topic branches.

License
-------
Copyright (c) 2011, Mihail Szabolcs

Templatizer is provided **as-is** under the GPLv3 license. For more information see LICENSE.
