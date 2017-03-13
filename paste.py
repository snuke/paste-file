#!/usr/bin/python

import sys, os, shutil
import redis

help_txt = \
'''
pst              : show registered file list
pst <key>        : copy file in current directory
pst <key> <path> : register file
pst del <key>    : unregister file
pst help         : help
'''

db = redis.Redis(host='localhost', port=6379, db=0)
z = 'paste_file'
args = sys.argv[1:]

def error(msg):
  print(msg)
  exit(0)

def help():
  error(help_txt)

def add(key, path):
  if not os.path.exists(path):
    error('file not found')
  path = os.path.abspath(path)
  db.hset(z,key,path)
  print('added {}: {}'.format(key,path))

def delete(key):
  if not db.hdel(z, key):
    error('key not found')
  print('deleted {}'.format(key))

def show():
  l = db.hgetall(z)
  print('registered files: {}'.format(len(l)))
  for key,val in l.items():
    print('{}: {}'.format(key,val))

def paste(key):
  path = db.hget(z, key)
  if path is None:
    error('key not found')
  if os.path.exists(os.path.basename(path)):
    error('this file already exists')
  shutil.copy(path, '.')
  print('pasted {}: {}'.format(key,path))

def main():
  global args
  if len(args) == 0:
    show()
    return
  cmd, args = args[0], args[1:]
  if cmd == 'help':
    help()
  elif cmd == 'add':
    if len(args) != 2:
      help()
    add(*args)
  elif cmd == 'del' or cmd == 'rm':
    if len(args) != 1:
      help()
    delete(*args)
  elif cmd == 'list' or cmd == 'show':
    show()
  elif len(args) == 1:
    add(cmd, args[0])
  else:
    if len(args) != 0:
      help()
    paste(cmd)

if __name__ == '__main__':
  main()
