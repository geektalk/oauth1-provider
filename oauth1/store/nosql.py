import redis
import json
import uuid


class Oauth1StoreRedis(object):
    redis_host = 'localhost'
    redis_port = 6379
    redis_db = 0
    redis_ns = ""

    conn = None

    def __init__(self, namespace="oauth1-redis"):
        self.conn = redis.StrictRedis(host=self.redis_host, port=self.redis_port, db=self.redis_db)
        if not self.conn:
            raise Exception('Redis is not properly setup. Check redis configs?')

        self.redis_ns = namespace

    def nonce_is_declared(self, nonce):
        hash_name = "%s-nonces" % self.redis_ns
        res = self.conn.hget(hash_name, nonce)
        if res:
            return True
        else:
            self.conn.hset(hash_name, nonce, 1)
            return False

    def create_new_consumer_tokens(self, app_name, app_desc, app_platform, app_url):
        tokens = self._generate_new_consumer_tokens()
        hash_name = "%s-app_info" % self.redis_ns

        app = json.dumps({
            'id': uuid.uuid4().__str__().replace('-', ''),
            'name': app_name,
            'description': app_desc,
            'platform': app_platform,
            'app_url': app_url
        })
        self.conn.hset(hash_name, tokens['consumer_key'], app)

        hash_name = "%s-consumer_tokens" % self.redis_ns
        self.conn.hset(hash_name, tokens['consumer_key'], tokens['consumer_secret'])

    def _generate_new_consumer_tokens(self):
        return {
            'consumer_key': uuid.uuid4().__str__().replace('-', ''),
            'consumer_secret': uuid.uuid4().__str__().replace('-', '')
        }

    def is_valid_consumer_key(self, cons_key):
        hash_name = "%s-consumer_tokens" % self.redis_ns
        cons_sec = self.conn.hget(hash_name, cons_key)

        if isinstance(cons_sec, str):
            return True
        else:
            return False

    def get_consumer_secret(self, consumer_key):
        hash_name = "%s-consumer_tokens" % self.redis_ns
        cons_sec = self.conn.hget(hash_name, consumer_key)

        if isinstance(cons_sec, str):
            return cons_sec
        else:
            return None