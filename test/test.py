def test_rename_files():
  import sys
  
  sys.path.insert(0, '../bin')
  from refactor import Refactor

  args = {}
  args['find'] = ['a','b']
  args['replace'] = ['c']
  args['plan'] = True
  args['rename'] = True

  args['input_file'] = None

  input_filepaths =  [ 'resources/',
                       'resources/a',
                       'resources/a/b',
                       'resources/a/b/c',
                       'resources/a/b/c/a.b',
                       'resources/a/b/c/a.b/z.a.b.z',
                       'resources/a/b/e',
                       'resources/a/b/e/a-b'
                     ]

  refactor = Refactor()
  refactor.run(args, input_filepaths)
