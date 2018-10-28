#!/bin/python
# Alex Ethier 2018 https://github.com/alexethier/refactor

import argparse
import sys
import pprint
pp = pprint.PrettyPrinter(indent=2)
import os
import os.path
from stat import S_ISFIFO

class Refactor:

  def __init__(self):
    pass;

  # From the input lists of lists generate a new list containing the cross product between all input elements.
  def combine(self, token_options, separators=[" ", "_", "-", ".", "/"]):

    # If there are more than two token lists, use recursion to combine all the lists together except the first one.
    if(len(token_options) > 2):
      current_options = token_options[1:]
      combinations = self.combine(current_options)
      new_token_options = []
      new_token_options.append(token_options[0])
      new_token_options.append(combinations)

      return self.combine(new_token_options)

    # If there are exactly two token lists combine them in all the standard ways.
    elif(len(token_options) == 2):
      combinations = []
      for first_token in token_options[0]:
        for second_token in token_options[1]:
          combinations.append(first_token + second_token)
          if second_token != "":
            for separator in separators:
              combinations.append(first_token + separator + second_token)
            # Add other common token separators here.
          else:
            # If dummy variables are used then combining the tokens should not include a separator.
            # In order to keep the indexes in sync we need to add one dummy combination for each real combination.
            for separator in separators:
              combinations.append(first_token + second_token)

      return combinations

    else:
      # If there is one token list there is nothing to do but return it.
      return token_options[0]

  # Obtain a list of different token patterns and return all possible combinations
  def computeCombinations(self, token_list):
    all_combinations = []
    for token in token_list:
      combination_options = []
      combination_options.append(token.lower())
      combination_options.append(token.upper())
      combination_options.append(token.title())
      # Other casing options can be added here

      all_combinations.append(combination_options)

    return self.combine(all_combinations)

  def pad_tokens(self, token_list, length):
    while length > 0:
      token_list.append("")
      length = length - 1
    return token_list

  # Pads the two lists so they are the same length, the shorter list will get dummy tokens.
  # This is necessary to keep the indexes between find and replace tokens synchronized.
  def get_tokens(self, find_tokens, replace_tokens):

    token_object = {}

    difference = len(find_tokens) - len(replace_tokens)
    if difference > 0:
      token_object['find_tokens'] = find_tokens
      token_object['replace_tokens'] = self.pad_tokens(replace_tokens, difference)
    elif difference < 0:
      token_object['find_tokens'] = self.pad_tokens(find_tokens, -1 * difference)
      token_object['replace_tokens'] = replace_tokens
    else:
      token_object['find_tokens'] = find_tokens
      token_object['replace_tokens'] = replace_tokens

    return token_object

  def refactorFile(self, filepath, replace_map, plan=False):
    content = None
    with open(filepath, "r") as input_file:
      content = input_file.read()

    if(plan):
      matched_keys = {};
      for key in replace_map:
        if key in content:
          matched_keys[key] = replace_map[key]

      return matched_keys;
    else:
      for key in replace_map:
        content = content.replace(key, replace_map[key])

      with open(filepath, "w") as output_file:
        output_file.write(content)

#  def renameFile(self, filepath, replace_map, plan=False):
#
#    refactor_filepath = filepath
#    for key in replace_map:
#      refactor_filepath = refactor_filepath[::-1].replace(key[::-1], replace_map[key][::-1],1)[::-1]
#      #refactor_filepath = refactor_filepath.replace(key, replace_map[key],1)
#      if refactor_filepath != filepath:
#        break
#
#    if refactor_filepath != filepath:
#      print(filepath + " -> " + refactor_filepath)
#      return refactor_filepath  
    
# Changing directories like so: one/two/three -> 1/2/3 is intrinsically different than names like
# /a/one-two-three/b -> a/1-2-3/b because the first case changes a whole span of directories
# Consider this mapping change: -f one two three -r 1 2
# We need (the option) to preserve the directory structure, so the following change will be scheduled: one/two/three -> 1/2/three
# This means chopping the find list so that it is equal in length to the replace list.

# Plan: Change paths in two steps:
# First check the entire span of the path and make a replacement, use a special replace map for this.  Record the mapping.
# Second change individual elements (split on '/').
# Record the mapping of input to output for all changes
# Then finally make necessary adjustments using the directory sorted order (root level directories first).

#  def old.renameFile(self, filepath, replace_map, plan=False):
#
#    # Given a path only rename the basename
#    dirname = os.path.dirname(filepath)
#    basename = os.path.basename(filepath)
#    
#    for key in replace_map:
#      basename = basename.replace(key, replace_map[key])
#
#    newpath = os.path.join(dirname, basename)
#    if newpath != filepath:
#      if(plan):
#        return newpath
#      else:
#        os.rename(filepath, newpath)

  def check_path(self, filepath):
    fullpath = os.path.abspath(filepath.rstrip('\n'))
    if os.path.exists(fullpath) and filepath != ".":
      return fullpath

  def boot(self):

    parser = argparse.ArgumentParser(description="Intelligently find and replace tokens while keeping case constant.  See https://github.com/alexethier/refactor for more details.")
    parser.add_argument("-i", "--input_file", nargs="*", help="Path to file(s) to edit.")
    parser.add_argument("-f", "--find", nargs="*", help="Ordered list of tokens to find.", required=True)
    parser.add_argument("-r", "--replace", nargs="*", help="Ordered list of tokens to replace.", required=True)
    parser.add_argument("-p", "--plan", action='store_true', default=False, help="The script will not modify any files.  It will show what replacements are planned.")
    parser.add_argument("-n", "--rename", action='store_true', default=False, help="Renames files and directories using the same replacement strategy.")

    args = parser.parse_args()

    # If there are more replace tokens than find tokens the code will run but we have to guess the separator and pattern to use.
    # Since this is unlikely to choose correctly it is better to just return an error.
    if(len(args['replace']) > len(args['find'])):
      sys.stderr.write("The number of replace tokens must not exceed the number of find tokens.  Try concatenating the replace tokens.\n")
      sys.exit(1)

    input_filepaths=[]
    if S_ISFIFO(os.fstat(0).st_mode):
      for line in sys.stdin:
        input_filepaths.append(line)

    self.run(args, input_filepaths)

  def run(self, args, input_filepaths):

    tokens = self.get_tokens(args['find'], args['replace'])
    find_tokens = tokens['find_tokens']
    replace_tokens = tokens['replace_tokens']

    # Because combinations are computed deterministically both lists will share the same ordering and can easily be mapped together.
    find_combinations = self.computeCombinations(find_tokens)
    replace_combinations = self.computeCombinations(replace_tokens)

    replace_map = {}
    for index in range(len(find_combinations)):
      find_combination = find_combinations[index]
      replace_combination = replace_combinations[index]
      replace_map[find_combination] = replace_combination

    # Datastructures to store planned changes
    all_changed_keys = {}
    all_changed_filepaths = {}

    # Determine a list of filepaths to execute over
    if args['input_file'] != None:
      for filepath in args['input_file']:
        if os.path.isfile(filepath):
          input_filepaths.append(filepath)
        else:
          print("WARNING: Invalid file path supplied: " + str(filepath))    

    filepaths = []
    for input_filepath in input_filepaths:
      fullpath = self.check_path(input_filepath)
      if fullpath != None:
        filepaths.append(fullpath)

    ## If we rename files and directories we need to rename the files at the bottom of the directory tree first
    ## So get the full paths of the files and sort by length
    #filepaths.sort(lambda x,y: cmp(len(x), len(y)))

    filetrees = {} # Keep a list of tree nodes to track file name changes
    # Perform replacements
    for filepath in filepaths:
      if os.path.isfile(filepath):
        if args['plan']:
          changed_keys = self.refactorFile(filepath, replace_map, True)
          all_changed_keys.update(changed_keys)
        else:
          self.refactorFile(filepath, replace_map)
      if args['rename']:
        # As a hack assume no files have '/' as a char in the name.
        for key in replace_map:
          new_filepath = filepath.replace(key, replace_map[key])
          filenames = new_filepath.split("/")
          filepointer = filetrees
          for filename in filenames:
            filepointer[filename] = {}
            filepointer = filepointer[filename]
          filepointer['/'] = {}
          filepointer['/']['src'] = os.path.basename(filepath)
          filepointer['/']['dest'] = filenames[-1]

        pp.pprint(filetrees)
          
        #if args.plan:
        #  new_filepath = self.renameFile(filepath, replace_map, True)
        #  if new_filepath != None:
        #    all_changed_filepaths[filepath] = new_filepath
        #else:
        #  self.renameFile(filepath, replace_map)

    if args['plan']:
      for key in all_changed_keys:
        print(key + " -> " + all_changed_keys[key])

      for key in all_changed_filepaths:
        print(key + " -> " + all_changed_filepaths[key])

if __name__ == "__main__":
  refactor = Refactor();
  refactor.boot();
