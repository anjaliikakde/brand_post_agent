# """
# RQ Worker

# Runs background job worker.
# """

# import redis
# from rq import Worker, Queue, Connection

# from app.core.config import settings


# def start_worker():

#     redis_conn = redis.from_url(settings.REDIS_URL)

#     queue = Queue("default", connection=redis_conn)

#     with Connection(redis_conn):

#         worker = Worker([queue])

#         worker.work()


# if __name__ == "__main__":

#     start_worker()