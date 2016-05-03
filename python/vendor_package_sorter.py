#!/usr/bin/python

#
# Written by Ned Wilson <ned@n3d.org>, 2016-02-27
# Takes one argument on the command line: a directory, which contains a vendor submission.
#
# The first test performed on each file name is a pattern match, to see if the filename is valid (or relevant).
# If a file is determined to be valid, as in, it starts with a shot, then it is sorted based on a series of rules.
#
# If the file is invalid, then it is moved into a manual sort location, defined in the GLOBALS section below.
# 
# Next, a series of additional pattern matching operations are applied to the file to fill in the value for 
# various tokens, such as sequence, shot, version number, file extension, etc.
#
# Finally, a series of rules are applied to the file, to determine where, in the filesystem, it should be moved to.
# These are all defined in the GLOBALS section as well.
#
# This will only work on MacOS or UNIX systems; the paths and separators are not designed to work on Windows.
#

#
# IMPORTS SECTION
#

import os
import sys
import glob
import re
import subprocess

#
# GLOBALS SECTION
#

# Show code that script is operating under
g_s_show_code = "monolith"
# Destination shot tree directory for sorting operations
g_s_shot_tree_root = "/Volumes/monovfx/_vfx/SHOT_TREE"
# Destination for invalid files
g_s_invalid_file_dest = "/Volumes/monovfx/_vfx/SHOT_TREE/z_to_be_sorted"

# Check to see if we are in DEV mode, if so, change the paths around to non-production ones
try:
	if os.environ['DEV']:
		g_s_shot_tree_root = "%s/sandbox/_vfx/SHOT_TREE"%os.environ['HOME']
		g_s_invalid_file_dest = "%s/sandbox/_vfx/SHOT_TREE/_z_to_be_sorted"%os.environ['HOME']
		print "INFO: Working in DEV mode."
except KeyError:
	pass

# Global boolean to determine if the destination sequence or shot should be uppercased
g_b_dest_uc = False
g_lst_tags_uc = [ '{sequence}', '{shot}' ]

# Regular expression to determine if a file is part of an image sequence
g_re_img_seq = re.compile(r'.*\.[0-9]+\.[a-zA-Z]{3,}$')

# Valid File Pattern Match
g_re_valid_file = re.compile(r'^[a-zA-Z]{3}[0-9]{4}')

# Token Assignment Dictionary
g_dict_token_assign = { '{sequence}' : re.compile(r'^([a-zA-Z]{3})'),
						'{shot}' : re.compile(r'^([a-zA-Z]{3}[0-9]{4})'),
						'{filehead}' : re.compile(r'^(.*)\.'),
						'{fileext}' : re.compile(r'\.([a-zA-Z]{3,})$'),
						'{fileextra}' : re.compile(r'^[a-zA-Z]{3}[0-9]{4}([a-zA-Z0-9_-]*)\.'),
						'{version}' : re.compile(r'_[vV][0]*([1-9][0-9]*)'),
						'{frame}' : re.compile(r'\.([0-9]+)\.') }

# List of valid files. Will contain a List of ValidFile objects. 						
g_lst_valid_files = []

# List of invalid files. Will contain a List of InvalidFile objects.
g_lst_invalid_files = []

# List of file extensions to ignore
g_list_fileext_ignore = ['pdf', 'cdl', 'ale', 'edl', 'csv', 'xls', 'xlsx']

# Unix command to create destination file, and arguments
# Uncomment below to copy instead of link
# g_s_create_cmd = "/bin/cp"
# g_s_create_cmd_args = "-vf"
g_s_create_cmd = "/bin/ln"
g_s_create_cmd_args = "-v"

# ValidFile class definition
class ValidFile:

	def __init__(self, m_s_src_file_path):
		self.i_s_src_file_path = m_s_src_file_path
		self.i_dict_tokens = {}
		self.i_s_dest_file_path = ""
		self.i_b_isseq = False
		self.i_b_rule_match = False
		
	def __repr__(self):
		retstr = "ValidFile: Source Path: %s "%self.i_s_src_file_path
		retstr = retstr + "ValidFile: Destination Path: %s "%self.i_s_dest_file_path
		for key in self.i_dict_tokens:
			retstr = retstr + "ValidFile: %s : %s "%(key, self.i_dict_tokens[key])
		retstr = retstr + "ValidFile: Is Image Sequence? %s "%self.i_b_isseq
		retstr = retstr + "ValidFile: Rule Match? %s "%self.i_b_rule_match
		return retstr
	
	def no_rule_match_path(self, m_s_invalid_path):
		l_s_invalid_path = ""
		if self.i_b_isseq:
			l_s_invalid_path = os.path.join(m_s_invalid_path, os.path.basename(self.i_s_src_file_path).split[0], os.path.basename(self.i_s_src_file_path))
		else:
			l_s_invalid_path = os.path.join(m_s_invalid_path, os.path.basename(self.i_s_src_file_path))
		self.i_s_dest_file_path = l_s_invalid_path
		
# InvalidFile class definition
class InvalidFile:

	def __init__(self, m_s_src_file_path):
		self.i_s_src_file_path = m_s_src_file_path
		self.i_s_dest_file_path = ""
		self.i_b_isseq = False
		
	def __repr__(self):
		retstr = "InvalidFile: Source Path: %s "%self.i_s_src_file_path
		retstr = retstr + "InvalidFile: Destination Path: %s "%self.i_s_dest_file_path
		retstr = retstr + "InvalidFile: Is Image Sequence? %s"%self.i_b_isseq
		return retstr
		
# Rule class definition
class Rule:

	IS_EQUAL_TO = 0
	# IS NOT EQUAL_TO not yet implemented.
	IS_NOT_EQUAL_TO = 1
	# CONTAINS not yet implemented.
	CONTAINS = 2
	DOES_NOT_CONTAIN = 3
	
	# Rule constructor. Used to define an equality test and a successful output path, which is tokenized.
	# Example usage:
	# test_rule = Rule('{extension}', Rule.IS_EQUAL_TO, 'exr', '%s/{sequence}/{shot}/output/{filehead}.{frame}.{fileext}'%g_s_shot_tree_root)
	def __init__(self, m_s_tag, m_int_test, m_s_valid, m_s_output_path):
		self.i_s_tag = m_s_tag
		self.i_int_test = m_int_test
		self.i_s_valid = m_s_valid
		self.i_s_output_path = m_s_output_path
	
	# takes a ValidFile object as an argument. If the rule evaluates as true, will set the destination path
	# in the ValidFile object and return True. If not, will return false.	
	def evaluate(self, m_obj_valid_file):
		l_b_retval = False
		for key in m_obj_valid_file.i_dict_tokens:
			if key == self.i_s_tag:
				if self.i_int_test == self.IS_EQUAL_TO:
					if m_obj_valid_file.i_dict_tokens[key] == self.i_s_valid:
						l_b_retval = True
				elif self.i_int_test == self.DOES_NOT_CONTAIN:
					# if the match is a list and not a string, loop through.
					if isinstance(self.i_s_valid, (list, tuple)):
						l_b_loopmatch = False
						for l_s_match in self.i_s_valid:
							if l_s_match not in m_obj_valid_file.i_dict_tokens[key]:
								l_b_loopmatch = True
							else:
								l_b_loopmatch = False
						l_b_retval = l_b_loopmatch
					else:
						if self.i_s_valid not in m_obj_valid_file.i_dict_tokens[key]:
							l_b_retval = True
		if l_b_retval:
			l_s_output_path = self.i_s_output_path
			for key in m_obj_valid_file.i_dict_tokens:
				l_s_output_path = l_s_output_path.replace(key, m_obj_valid_file.i_dict_tokens[key])
			m_obj_valid_file.i_s_dest_file_path = l_s_output_path
			m_obj_valid_file.i_b_rule_match = True
		return l_b_retval
			
# Rule Definitions
g_lst_rules = [ Rule('{fileext}', Rule.IS_EQUAL_TO, 'exr', '%s/{sequence}/{shot}/2k/{shot}{fileextra}/{shot}{fileextra}.{frame}.{fileext}'%g_s_shot_tree_root),
				Rule('{fileext}', Rule.IS_EQUAL_TO, 'mov', '%s/{sequence}/{shot}/output/{shot}{fileextra}.{fileext}'%g_s_shot_tree_root),
				Rule('{filehead}', Rule.DOES_NOT_CONTAIN, ['comp','temp'], '%s/{sequence}/{shot}/element/{shot}{fileextra}/{shot}{fileextra}.{frame}.{fileext}'%g_s_shot_tree_root) ]

# Program usage instructions, to be printed when the command line is in error				
def usage():
	l_s_usage = """
Usage: vendor_package_sorter.py [path_to_vendor_submission]

       [path_to_vendor_submission] should be a valid directory with
       shots submitted from a visual effects vendor, for example:
       /Volumes/monovfx/_vfx/POST_OFFICE/ILM/from_ilm/20160122/
"""
	print l_s_usage

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "ERROR: No path provided on the command line."
		usage()
		exit()
	if not os.path.isdir(sys.argv[1]):
		print "ERROR: Invalid directory or file provided on the command line."
		usage()
		exit()
	l_s_vendor_submission = sys.argv[1]
	print "INFO: Examining vendor submission folder at %s"%l_s_vendor_submission
	
	# Create a master list of every file in the vendor submission.
	# Ignore hidden files, like .DS_Store, etc.
	l_lst_all_files = []
	for dirname, subdirlist, filelist in os.walk(l_s_vendor_submission):
		for f in filelist:
			if f[0] == '.':
				continue
			l_lst_all_files.append(os.path.join(dirname, f))
			
	# Go through every file to see which ones are to be ignored, and which ones are valid or not.
	b_fileignore = False
	b_isseq = False
	for l_s_filepath in l_lst_all_files:
		b_fileignore = False
		b_isseq = False
		tmp_extension = os.path.splitext(l_s_filepath)[1][1:]
		for bad_ext in g_list_fileext_ignore:
			if tmp_extension.lower() == bad_ext:
				print "INFO: Ignoring file %s"%l_s_filepath
				b_fileignore = True
				break
		if b_fileignore:
			continue
		l_s_filebase = os.path.basename(l_s_filepath)
		if g_re_img_seq.match(l_s_filebase):
			b_isseq = True
		if g_re_valid_file.match(l_s_filebase):
			tmp_validfile = ValidFile(l_s_filepath)
			tmp_validfile.i_b_isseq = b_isseq
			g_lst_valid_files.append(tmp_validfile)
		else:
			tmp_invalidfile = InvalidFile(l_s_filepath)
			tmp_invalidfile.i_b_isseq = b_isseq
			if b_isseq:
				tmp_invalidfile.i_s_dest_file_path = os.path.join(g_s_invalid_file_dest, l_s_filebase.split('.')[0], l_s_filebase)
			else:
				tmp_invalidfile.i_s_dest_file_path = os.path.join(g_s_invalid_file_dest, l_s_filebase)
			g_lst_invalid_files.append(tmp_invalidfile)
	
	# Go through the list of valid files, and populate the list of tags.
	for validfile in g_lst_valid_files:
		# instantiate a new local copy of tokens dictionary 
		tmp_vf_tokens = {}
		# instantiate a new local copy of the basename for the source file path
		tmp_basename = os.path.basename(validfile.i_s_src_file_path)
		# loop through all tokens that we want to populate
		for key in g_dict_token_assign:
			# match the regular expression for the token against the local basename
			match_obj = g_dict_token_assign[key].search(tmp_basename)
			# if the regular expression for the token matches?
			if match_obj is not None:
				# should we be uppercasing the values of the tokens, and which tokens should be uppercased?
				if g_b_dest_uc and key in g_lst_tags_uc:
					tmp_vf_tokens[key] = match_obj.group(1).upper()
				else:
					tmp_vf_tokens[key] = match_obj.group(1)
		# Assign the local copy of the freshly populated tokens object to the valid file object
		validfile.i_dict_tokens = tmp_vf_tokens
	
	# Loop through all of the valid files once again, but this time, apply the rules to get a valid output path.
	# Create a new list with the files that matched a rule.
	# If no rules apply to a file, place file into a separate invalid list.
	l_lst_no_rules_match = []
	l_lst_rules_match = []
	
	# Evaluate all files for all rules
	for validfile in g_lst_valid_files:
		for rule in g_lst_rules:
			rule.evaluate(validfile)

	# Loop once again to find rule matches
	for validfile in g_lst_valid_files:
		if validfile.i_b_rule_match:
			l_lst_rules_match.append(validfile)
		# no rules matched, so, repoint to the invalid file destination
		else:
			validfile.no_rule_match_path(g_s_invalid_file_dest)
			l_lst_no_rules_match.append(validfile)
			l_lst_no_rules_match.append(validfile)
	
	# link or copy all valid files that matched sorting rules		
	if len(l_lst_rules_match) > 0:
		print ""
		print "INFO: Now processing valid files that matched file sorting rules."
		print ""
		for validfile in l_lst_rules_match:
			print "INFO: Creating %s"%validfile.i_s_dest_file_path
			if not os.path.exists(os.path.dirname(validfile.i_s_dest_file_path)):
				os.makedirs(os.path.dirname(validfile.i_s_dest_file_path))
			subprocess.call([g_s_create_cmd, g_s_create_cmd_args, validfile.i_s_src_file_path, validfile.i_s_dest_file_path])

	# link or copy all valid files that did not match sorting rules
	if len(l_lst_no_rules_match) > 0:
		print ""
		print "INFO: Now processing valid files that did not match file sorting rules."
		print ""
		for validfile in l_lst_no_rules_match:
			print "INFO: Creating %s"%validfile.i_s_dest_file_path
			if not os.path.exists(os.path.dirname(validfile.i_s_dest_file_path)):
				os.makedirs(os.path.dirname(validfile.i_s_dest_file_path))
			subprocess.call([g_s_create_cmd, g_s_create_cmd_args, validfile.i_s_src_file_path, validfile.i_s_dest_file_path])

	# link or copy all invalid files
	if len(g_lst_invalid_files) > 0:
		print ""
		print "INFO: Now processing invalid files."
		print ""
		for invalidfile in g_lst_invalid_files:
			print "INFO: Creating %s"%invalidfile.i_s_dest_file_path
			if not os.path.exists(os.path.dirname(invalidfile.i_s_dest_file_path)):
				os.makedirs(os.path.dirname(invalidfile.i_s_dest_file_path))
			subprocess.call([g_s_create_cmd, g_s_create_cmd_args, invalidfile.i_s_src_file_path, invalidfile.i_s_dest_file_path])

	print ""
	print "INFO: DONE!"
	print ""
