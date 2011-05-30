#!/usr/bin/env python

__author__  = 'Mihail Szabolcs'
__version__ = (0, 2, 0)
__license__ = 'GPL'

import sys
import os
import re
import glob
import json
import platform
import math
import logging
from datetime import datetime

EXIT_SUCCESS = 0
EXIT_ERROR = -1

ACTION_SHELL= 1
ACTION_FILE = 2

def qglob(path, pattern):
	""" Glob convenience helper """
	return glob.glob(os.path.join(path, pattern))

class TemplatizerException(Exception):
	""" Generic Templatizer Exception """
	pass

class TemplateNotFound(TemplatizerException):
	""" Templatizer Template Not Found Exception """
	pass

class DuplicateTemplate(TemplatizerException):
	""" Templatizer Duplicate Template Exception """
	pass

class InvalidTemplate(TemplatizerException):
	""" Templatizer Invalid Template Exception """
	pass

class InvalidActionHandler(TemplatizerException):
	""" Templatizer Invalid Action Handler Exception """
	pass

class Template:
	"""
		Template Class
	"""
	def __init__(self, path):
		""" Constructor """
		self.path = path
		self.constants = {}
		self.variables = {}
		self.actions = []

		self.__regexp = None
		self.__regexp_dict = {}
		self.__name = None

	def __getName(self):
		""" Getter for name attribute """
		return self.__name

	def __getActions(self):
		""" Getter for actions attribute """

	name = property(__getName, None, None, 'This template\'s name')
	actions = property(__getActions, None, None, 'This template\'s actions')

	def parse(self, filename, arguments={}):
		template = json.loads(open(filename).read())
		
		if not self.validate(template):
			raise InvalidTemplate("Invalid %s template" % filename)
	
		self.__name = template['name']

		if not self.parse_variables(template['variables'], arguments):
			return False

		if not self.parse_constants(template['constants']):
			return False

		if not self.preprocess():
			return False

		if not self.parse_actions(template['package']):
			return False

		return True
	
	def parse_variables(self, variables, arguments):
		""" Parses and evaluates variables based on the arguments """
		for k, v in variables.items():
			if k in arguments:
				vvv = arguments[k]
				for kk, vv in v.items():
					self.variables[kk] = str(eval('lambda v: %s' % vv)(vvv))
			else:
				for kk, vv in v.items():
					self.variables[kk] = '' # fallback to empty string

		return True

	def parse_constants(self, constants):
		""" Parses and evaluates constants """
		for k, v in constants.items():
			self.constants[k] = str(eval('lambda: %s' % v)())

		# built-in constants
		self.constants['%TPLDIR%'] = path

		return True

	def parse_actions(self, actions):
		""" Parses and evaluates actions """
		for action in actions:
			action[0] = self.process(action[0])

			if len(action) == 2:
				action[1] = os.path.join(self.path, self.process(action[1]))

			self.actions.append(action)

		return True

	def validate(self, parsed):
		""" Validates a parsed JSON template descriptor """
		for p in ['name','package','variables','constants']:
			if not p in parsed:
				return False
		
		return True

	def preprocess(self):
		""" Prepares the multi-regexp used for templating """
		self.__regexp_dict = dict(self.variables, **self.constants)
		self.__regexp = re.compile("(%s)" % "|".join(map(re.escape, self.__regexp_dict.keys())))

		return True

	def process(self, data):
		""" Processes a piece of data using the multi-regexp in one shot """
		return self.__regexp.sub(lambda mo: self.__regexp_dict[mo.string[mo.start():mo.end()]], data)
		
	def execute(self, action_handler):
		""" Execute """
		if not callable(action_handler):
			raise InvalidActionHandler("Invalid action handler")

		for action in self.actions:
			action_type = len(action)
			action_name = action[0]
			action_data = None
			
			if action_type == ACTION_FILE:
				action_data = self.process(open(action[1]).read())

			action_handler(action_type, action_name, action_data)

		return EXIT_SUCCESS

class Generator:
	"""
		Generator Class
	"""
	def __init__(self):
		""" Constructor """
		self.templates = {}

	def add_template(self, template):
		""" Registers a template with this generator """
		name = template.name
		
		if name in self.templates:
			raise DuplicateTemplate('Duplicate %s template' % name)

		self.templates[name] = template

	def action_handler(self, action_type, action_name, action_data=None):
		""" Default action handler which creates files and executes shell commands """
		print(action_name)
		print(action_data)
		"""
		os.system(c) # execute shell commands
		if not os.path.exists(t): 
			#self.log('Template %s doesn\'t exists, skipping ...' % t)					
			pass
		elif os.path.exists(c): 
			#self.log('File %s exists, skipping ...' % c)
			pass
		else:
			with open(c,'w') as f: f.write(self.process(tpl, open(t).read()))
			#self.log('File %s written ...' % c)
		"""

	def execute(self, name, path):
		""" Executes the generator """
		if not name in self.templates:
			raise TemplateNotFound('Template %s not found' % name)

		# change current working directory
		os.chdir(path)

		return self.templates[name].execute(self.action_handler)

class Templatizer:
	def __init__(self, argv={}, config='~/.templatizer'):
		""" Constructor """
		self.generator = Generator()
		self.arguments = {}
		
		self.parse_arguments(argv)
		self.parse_config(config)
	
	def parse_templates(self, path):
		""" Scans a directory for available templates """
		template_dir = os.path.expanduser(path)
		logging.debug('Searching %s for available templates ...' % template_dir)
		
		for template in qglob(template_dir,'*.templatizer'):
			logging.debug('-> Parsing %s ...' % template)

			tpl = Template(template_dir)
			if tpl.parse(template, self.arguments):
				self.generator.add_template(tpl)
				logging.debug('\t-> SUCCESS')
			else:
				logging.debug('\t-> FAIL')

	def parse_arguments(self, argv):
		""" Parses arguments into a key, value dictionary """
		for arg in argv:
			# accepted argument format: --key=value
			if arg.startswith('--') and arg.find('=') != -1:
				k, v = arg.split('=')
				self.arguments[k[2:]] = v
						
	def parse_config(self, config):
		""" Parses the configuration and scans all paths for available templates """
		config_file = os.path.expanduser(config)
		if not os.path.exists(config_file) or not os.path.isfile(config_file): return

		with open(config_file) as f:
			for path in f:
				self.parse_templates(path.strip())
						
	def execute(self, name):
		""" Executes the internal generator """
		try:
			return self.generator.execute(name, os.getcwd())
		except TemplatizerException as message:
			logging.debug(message)

		return EXIT_ERROR
		
def main(argv):
	""" Main """
	if len(argv) < 2:
		print('Templatizer v%d.%d.%d' % __version__)
		print('usage: %s [options] template [--key1=value1, --key2=value2]' % os.path.splitext(os.path.basename(argv[0]))[0])
		print('')
		print('Options:')
		print('\t-v, --version\tshows the version number')
		print('\t-d, --debug\tenables debug output')
		return EXIT_ERROR

	if '-v' in argv or '--version' in argv:
		print('%d.%d.%d' % __version__) # print version
		return EXIT_SUCCESS

	if argv[1] == '-d' or argv[1] == '--debug':
		argv.pop(1) # remove this item
		logging.basicConfig(level=logging.DEBUG)
	
	return Templatizer(argv[2:]).execute(argv[1])
	
if __name__ == '__main__':
	exit(main(sys.argv))
