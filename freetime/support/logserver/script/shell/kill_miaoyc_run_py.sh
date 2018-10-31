ps aux | grep miaoyc | grep pypy | grep run.py | grep -v grep  | awk '{print $2}' |xargs kill -9
