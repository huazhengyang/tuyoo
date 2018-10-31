# -*- coding:utf-8 -*-

"""
Created on 2018/6/29
@author: sean
"""



import redis
import argparse

redis_conf = [
    {
        "ip": '127.0.0.1',
        "port": 8004,
        "db": 1
    }
]
redis_size = len(redis_conf)

redis_user_conf = [
    {
        "ip": '127.0.0.1',
        "port": 8004,
        "db": 7
    },
    {
        "ip": '127.0.0.1',
        "port": 8004,
        "db": 8
    }
]
redis_user_size = len(redis_user_conf)

sps = []
user_sps = []


def get_redis_conf(idx):
    conf = redis_conf[idx]
    return conf["ip"], conf["port"], conf["db"]


def get_redis_user_conf(idx):
    conf = redis_user_conf[idx]
    return conf["ip"], conf["port"], conf["db"]


def get_idx(k):
    idx = abs(hash(str(k)))
    return idx % redis_size


def get_user_idx(user_id):
    return user_id % redis_user_size


def init_redis():
    for x in range(redis_size):
        ip, port, db = get_redis_conf(x)
        s = redis.StrictRedis(host=ip, port=port, db=db)
        sps.append(s.pipeline(transaction=False))

    for x in range(redis_user_size):
        ip, port, db = get_redis_user_conf(x)
        s = redis.StrictRedis(host=ip, port=port, db=db)
        user_sps.append(s.pipeline(transaction=False))


def del_user(user_id):
    if not user_id:
        print "用户ID错误"
        return
    print '111111111111111'
    user_key = "user:%s" % str(user_id)
    idx = get_user_idx(int(user_id))
    user_pipe = user_sps[idx]
    if user_pipe is None:
        print "redis 用户库配置错误"
        return
    # 关联属性
    print '2222222222222222'
    attrs = [
        "snsId",
        "mdevid",
        "email",
        "userAccount",
        "bindMobile"]
    print '------', user_key
    print '------', attrs
    print '------', user_pipe
    res = user_pipe.hmget(user_key, attrs).execute()
    if len(res) != 1 or len(res[0]) != 5 or len(filter(None, res[0])) == 0:
        #print ("没有用户:%s" % user_id)
        return
    print '33333333333333333333'
    values = res[0]
    dic_prefix = {
        "snsId": "snsidmap:%s",
        "mdevid": ["devidmap4:%s", "devidmap3:%s"],
        "email": "mailmap:%s",
        "userAccount": "accountmap:%s",
        "bindMobile": "mobilemap:%s"
    }
    dic_value = {}
    for i in range(0, len(attrs)):
        if not values[i]:
            print "用户%s属性未赋值" % attrs[i]
        else:
            dic_value[attrs[i]] = values[i]
    # 收集keys
    keys = []
    for k in dic_value:
        v = dic_value[k]
        prefix = dic_prefix[k]
        if isinstance(prefix, list):
            for pre in prefix:
                keys.append(pre % v)
        else:
            keys.append(prefix % v)
    # 分配redis
    print '444444444444444'
    dic_sps = {}
    for k in keys:
        idx = get_idx(k)
        if not dic_sps.get(idx):
            dic_sps[idx] = []
        dic_sps[idx].append(k)

    # 删除用户数据
    user_pipe.delete(user_key).execute()
    #print ("清除用户数据")
    # 批量删除
    for idx in dic_sps:
        pipe = sps[idx]
        if pipe is None:
            #print ("redis 数据库配置错误 索引=%s" % idx)
            continue
        keys = dic_sps[idx]
        pipe.delete(*keys).execute()
    print "清除关联数据"


if __name__ == "__main__":
    init_redis()
    parser = argparse.ArgumentParser()
    parser.add_argument("user_id", help="要删除的用户ID")
    args = parser.parse_args()
    del_user(args.user_id)
