#!/usr/bin/env python

__author__  = 'Mihail Szabolcs'
__version__ = (0, 2, 0)
__license__ = 'GPL'

import sys
import os
import glob
import json
import platform
import math
import logging
from datetime import datetime

class Template:
	"""
		Template Class
	"""
	def __init__(self):
		""" Constructor """
		pass

class Generator:
	"""
		Generator Class
	"""
	def __init__(self):
		""" Constructor """
		pass

class Templatizer:
	def __init__(self, argv=None):
		self.templates = {}
		self.arguments = {}
		self.constants = {}
		
		self.parse_arguments(argv)
		self.parse_config('~/.templatizer')
	
	def scan(self, template_dir):
		template_dir = os.path.expanduser(template_dir)
		logging.debug('Searching %s for available templates ...' % template_dir)
		tpls = glob.glob(os.path.join(template_dir,'*.templatizer'))
		for tpl in tpls:
			logging.debug('\t-> Parsing %s ...' % tpl)
			if self.parse_template(template_dir, tpl):
				logging.debug('\t-> SUCCESS')
			else:
				logging.debug('\t-> FAIL')
				
	def parse_template(self, template_dir, template):
		tpl = json.loads(open(template).read())
		
		if not self.validate_template(tpl):
			#self.log('\t-> %s is not a valid template file' % template, 1)
			return False
		
		if tpl['name'] in self.templates:
			#self.log('WARNING: a template with the name %s already exists' % tpl['name'],1)
			return False
		
		tmp_vrs = {}
		
		vrs = tpl['variables']
		for k,v in vrs.items():
			if k in self.arguments:
				vvv = self.arguments[k]
				for kk, vv in v.items():
					tmp_vrs[kk] = str(eval('lambda v: %s' % vv)(vvv))
			else:
				for kk, vv in v.items():
					tmp_vrs[kk] = '' # fallback to empty string
					
		tpl['variables'] = tmp_vrs
		
		cnt = tpl['constants']
		for k,v in cnt.items():
			cnt[k] = str(eval('lambda: %s' % v)())
					
		for pkg in tpl['package']:
			if len(pkg) < 2: continue
						
			if pkg[1] == 'dir':
				pkg[0] = self.process_path(tpl, pkg[0])
			elif pkg[1] == 'shell':
				pkg[0] = self.process(tpl, pkg[0])
			else:
				pkg[0] = self.process_path(tpl, pkg[0])
				pkg[1] = self.process(tpl, os.path.join(template_dir, pkg[1]))
					
		self.templates[tpl['name']] = tpl
		
		return True
			
	def validate_template(self, template):
		if not 'name' in template:
			return False
		if not 'package' in template:
			return False
		if not 'variables' in template:
			return False
		if not 'constants' in template:
			return False
					
		return True
	
	def parse_arguments(self, argv):
		""" Parses arguments into a key, value dictionary """
		for arg in argv:
			# accepted argument format: --key=value
			if arg.startswith('--') and arg.find('=') != -1:
				k, v = arg.split('=')
				self.arguments[k[2:]] = v
						
	def parse_config(self, config):
		""" Parses the configuration, in this case loads all available templates """
		config_file = os.path.expanduser(config)
		if not os.path.exists(config_file) or not os.path.isfile(config_file): return
				
		config = json.loads(open(config_file).read())
		
		if 'paths' in config:
			for path in config['paths']: 
				self.scan(path)
						
	def process(self, template, content):
		for k, v in template['variables'].items():
			content = content.replace(k, v)
		for k, v in template['constants'].items():
			content = content.replace(k, v)
		for k, v in self.constants:
			content = content.replace(k, v)
			
		return content
		
	def process_path(self, template, path):
		return os.path.abspath(self.process(template, path))
	
	def execute(self, template):
		"""
		if not template in self.templates:
			#self.log('Template %s does not exist ...' % template)
			return 1
		
		tpl = self.templates[template]
									
		for pkg in tpl['package']:
			if len(pkg) < 2: continue
			
			# c = command (or filename), t = type (or filename)
			c, t = pkg
			
			if t == 'dir':
				if not os.path.exists(c): 
					os.makedirs(c) # create directories
					#self.log('Directory %s created ...' % c)
			elif t == 'shell':
				#self.log('%s' % c)
				os.system(c) # execute shell commands
			else:
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
							
		return 0 # Success			
		
def main(argv):
	""" Main """
	if len(argv) < 2:
		print('Templatizer v%d.%d.%d' % __version__)
		print('usage: %s [options] template [--key1=value1, --key2=value2]' % os.path.splitext(os.path.basename(argv[0]))[0])
		print('')
		print('Options:')
		print('\t-v, --version\tshows the version number')
		print('\t-d, --debug\tenables debug output')
		return 1

	if '-v' in argv or '--version' in argv:
		print('%d.%d.%d' % __version__) # print version
		return 1

	if argv[1] == '-d' or argv[1] == '--debug':
		argv.pop(1) # remove this item
		logging.basicConfig(level=logging.DEBUG)
	
	return Templatizer(argv[2:]).execute(argv[1])
	
if __name__ == '__main__':
	exit(main(sys.argv))
