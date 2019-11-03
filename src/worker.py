import aio_pika
import asyncio
import asyncpg
import logging
import logging.handlers
import logging.config
import os
import datetime
import pytz
import json


log = logging.getLogger(__name__)

INSERT_USER_ACTIVE_TASK = '''INSERT INTO active_tasks(name, description, add_date, expired_date, user_id) 
VALUES ($1, $2, $3, $4, $5)'''


def init_logging(debug, service_name):
    if service_name:
        log_format = f"[%(asctime)s] [{service_name}] [%(levelname)s]:%(name)s:%(message)s"
    else:
        log_format = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"

    formatters = {'basic': {'format': log_format}}
    handlers = {'stdout': {'class': 'logging.StreamHandler',
                           'formatter': 'basic'}}

    level = 'DEBUG' if debug else 'INFO'
    # syslog_host = config.get('SYSLOG_HOST')
    # if syslog_host:
    #     address = (syslog_host, config.get('SYSLOG_PORT', logging.handlers.SYSLOG_UDP_PORT))
    #     handlers['syslog'] = {'class': 'logging.handlers.SysLogHandler',
    #                           'address': address,
    #                           'formatter': 'basic'}
    #     handlers_names = ['stdout', 'syslog']
    # else:
    handlers_names = ['stdout']  # TODO under else
    loggers = {
        '': {
            'level': level,
            'propagate': False,
            'handlers': handlers_names
        }
    }
    logging.basicConfig(level='WARNING', format=log_format)
    log_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': formatters,
        'handlers': handlers,
        'loggers': loggers
    }
    logging.config.dictConfig(log_config)


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process():
        item = json.loads(message.body)
        log.debug(item['name'])
        log.debug(f'Recieved message {item}')
        await insert_user_task(item)
        # if I not scared to lost data from queue
        # loop = asyncio.get_event_loop()
        # loop.create_task(insert_user_task(message))
        log.debug(f'Task finished {item}')
        # message.ack()


async def insert_user_task(item: dict):
    log.debug(f'Start processing message {item}')
    conn = await asyncpg.connect(host='localhost', port=5432, user='postgres',
                                 password='postgres', database='simple_database')
    await conn.execute(INSERT_USER_ACTIVE_TASK, item['name'], item.get('description', None),
                       item.get('add_time', datetime.datetime.now(pytz.utc)), item.get('expired_date', None),
                       item['user_id'])
    await conn.close()
    # message.ack()
    log.debug(f'Finish processing message {item}')


async def run():
    connection = await aio_pika.connect_robust("amqp://guest:guest@127.0.0.1/")
    queue_name = "user_task_to_db"
    channel = await connection.channel()
    await channel.set_qos(prefetch_count=3)
    log.info(f'Worker connected to queue: {queue_name}')
    queue = await channel.declare_queue(queue_name, durable=True)
    await queue.consume(process_message)
    return connection


def main():
    # TODO add worker number to logging
    init_logging(os.getenv('WORKER_DEBUG', True), 'Worker')
    log.info(f'Start worker at {datetime.datetime.now(pytz.utc)}')
    loop = asyncio.get_event_loop()
    connection = loop.run_until_complete(run())
    try:
        loop.run_forever()
    finally:
        loop.run_until_complete(connection.close())


if __name__ == '__main__':
    main()

