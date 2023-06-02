'''
Caching for functions.
'''
from redis import StrictRedis
import base64
import configparser
import json
import logging
import redis
import redis_cache

config = configparser.ConfigParser()
config.read('/neamt/configuration.ini')

host = config['DEFAULT'].get('redis_host', 'redis')

client = StrictRedis(host=host, decode_responses=True)
cache = redis_cache.RedisCache(redis_client=client)

serializer = json.dumps
deserializer = json.loads

prefix = 'neamt'
ttl = 0
limit = 0

def get_key(namespace, args, kwargs):
    serialized_data = serializer([args, kwargs])
    if not isinstance(serialized_data, str):
        serialized_data = str(base64.b64encode(serialized_data), 'utf-8')
    return f'{prefix}:{namespace}:{serialized_data}'

def call_with_cache(fn, namespace, *args, **kwargs):
    result = None
    key = get_key(namespace, args, kwargs)
    try:
        result = client.get(key)
    except redis.exceptions.ConnectionError:
        logging.exception('Could not get a value from cache')
    keys_key = f'{prefix}:{namespace}:keys'
    if not result:
        result = fn(*args, **kwargs)
        result_serialized = serializer(result)
        try:
            redis_cache.get_cache_lua_fn(client)(keys=[key, keys_key], args=[result_serialized, ttl, limit])
        except redis.exceptions.ConnectionError:
            logging.exception('Could not set a value in cache')
    else:
        result = deserializer(result)
        logging.debug('Cached result: %s → %s', key, result)
    return result

def call_without_cache(fn, namespace, *args, **kwargs):
    return fn(*args, **kwargs)

call = call_with_cache if config['DEFAULT'].getboolean('redis_enabled', False) else call_without_cache
