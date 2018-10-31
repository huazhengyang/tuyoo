#!/bin/bash
 
# Author:        zipxing@hotmail.com
# Created:       2015年04月08日 星期三 09时19分55秒
# FileName:      start.sh
# 
SHELL_PATH=`dirname $(readlink -f $0)`
PROJECT_PATH=$SHELL_PATH"/../"
FREETIME_PATH=$SHELL_PATH"/../../../../"
export PYTHONPATH=$FREETIME_PATH
cd $PROJECT_PATH 
killall -9 pypy-log
rm -fr /home/zhoux/bilog/*
pypy-log run.py LI01 127.0.0.1 7979 1 &
pypy-log run.py LI02 127.0.0.1 7979 1 &
pypy-log run.py LW01 127.0.0.1 7979 1 &
pypy-log run.py LW02 127.0.0.1 7979 1 &
