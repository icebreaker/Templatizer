#!/usr/bin/env python
"""
	Copyright (c) 2011, Mihail Szabolcs
	For more information see LICENSE.
"""
import sys
import os
import glob
import json
import platform
import math
from datetime import datetime

class Templatizer:
	def __init__(self, argv=None, logger=sys.stdout, verbose=1):
		self.logger = logger
		self.verbose = verbose
		self.templates = {}
		self.arguments = {}
		self.constants = {}
		
		self.parse_arguments(argv)
		self.parse_config()
	
	def log(self, message, verbose = 0):
		if verbose < self.verbose:
			self.logger.write("%s\n" % message)
		
	def scan(self, template_dir):
		self.log('Searching %s for available templates ...' % template_dir)
		tpls = glob.glob(os.path.join(template_dir,'*.templatizer'))
		for tpl in tpls:
			self.log('\t-> Parsing %s ...' % tpl,1)
			if self.parse_template(template_dir, tpl):
				self.log('\t-> SUCCESS',1)
			else:
				self.log('\t-> FAIL',1)
				
	def parse_template(self, template_dir, template):
		tpl = json.loads(open(template).read())
		
		if not self.validate_template(tpl):
			self.log('\t-> %s is not a valid template file' % template, 1)
			return False
		
		if tpl['name'] in self.templates:
			self.log('WARNING: a template with the name %s already exists' % tpl['name'],1)
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
						
			if pkg[1] == "dir":
				pkg[0] = self.process_path(tpl, pkg[0])
			elif pkg[1] == "shell":
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
		if argv and isinstance(argv, list):
			# accepted argument format: --key=value
			for arg in argv:
				if arg.startswith("--") and arg.find("=") != -1:
					k,v = arg.split("=")
					k = k[2:]
					
					if k == "path": 
						self.scan(v)
					elif k == "verbose":
						self.verbose = int(v)
					else: 
						self.arguments[k] = v
						
	def parse_config(self):
		config_file = os.path.expanduser('~/.templatizer')
		if not os.path.exists(config_file) or not os.path.isfile(config_file): return
				
		config = json.loads(open(config_file).read())
		
		if 'paths' in config:
			for path in config['paths']: 
				self.scan(path)
		if 'constants' in config:
			for k, v in config['constants']: 
				self.constants[k] = str(eval('lambda: %s' % v)())
						
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
		if not template in self.templates:
			self.log('Template %s does not exist ...' % template)
			return 1
		
		tpl = self.templates[template]
									
		for pkg in tpl['package']:
			if len(pkg) < 2: continue
			
			# c = command (or filename), t = type (or filename)
			c, t = pkg
			
			if t == 'dir':
				if not os.path.exists(c): os.makedirs(c) # create directories
			elif t == 'shell':
				os.system(c) # execute shell commands
			else:
				if not os.path.exists(t): 
					self.log('Template %s doesn\'t exists, skipping ...' % t)					
				elif os.path.exists(c): 
					self.log('File %s exists, skipping ...' % c)
				else:
					with open(c,'w') as f: f.write(self.process(tpl, open(t).read()))
					
							
		return 0 # Success			
		
def main(argv):		
	if len(argv) < 3:
		print('usage: templatizer template [--key1=value1, --key2=value2]')
		return 1
		
	return Templatizer(argv[2:]).execute(argv[1])
	
if __name__ == "__main__":
	exit(main(sys.argv))

