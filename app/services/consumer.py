import json
import threading
import logging
from functools import wraps
from datetime import datetime, timezone
from confluent_kafka import Consumer, KafkaError
from model.consumer import ConsumerCreationRequest
from fastapi import HTTPException
import redis

logging.basicConfig(level=logging.INFO)

def handle_exceptions(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}") from e
    return wrapper

class KafkaConsumerService:
    def __init__(self, kafka_broker: str):
        self.kafka_broker = kafka_broker
        self.consumers = {}
        self.consumers_lock = threading.Lock()
        self.redis_client = redis.StrictRedis(
            host='redis', port=6379, db=0, decode_responses=True
        )

    def _generate_redis_key(self, pipeline_name: str) -> str:
        return f"{pipeline_name}"

    def _get_event_type(self, event_code: str) -> str:
        event_type_mapping = {
            'c': 'create', 'u': 'update', 'd': 'delete',
            'r': 'read', 't': 'truncate', 'm': 'message'
        }
        return event_type_mapping.get(event_code, 'unknown')

    def _parse_timestamp(self, ts_ms: int) -> tuple:
        if not ts_ms:
            return "unknown", "unknown"
        timestamp_seconds = ts_ms / 1000
        date_time = datetime.fromtimestamp(timestamp_seconds, tz=timezone.utc)
        return date_time, date_time.strftime('%Y-%m-%d %H:%M:%S')

    @handle_exceptions
    def start_consumer(self, request: ConsumerCreationRequest):
        with self.consumers_lock:
            if request.consumer_id in self.consumers:
                return {"message": f"Consumer '{request.consumer_id}' already running."}
            
            consumer = self._create_kafka_consumer(request)
            self._start_consumer_thread(request, consumer)
            
            return {"message": f"Started consumer '{request.consumer_id}' for topic '{request.kafka_topic}'."}

    def _create_kafka_consumer(self, request: ConsumerCreationRequest) -> Consumer:
        return Consumer({
            'bootstrap.servers': self.kafka_broker,
            'group.id': f'{request.consumer_id}-group',
            'auto.offset.reset': request.auto_offset_reset
        })

    def _start_consumer_thread(self, request: ConsumerCreationRequest, consumer: Consumer):
        self.consumers[request.consumer_id] = {
            'consumer': consumer,
            'running': True,
            'topic': request.kafka_topic
        }
        thread = threading.Thread(
            target=self._message_consumption_loop,
            args=(request.consumer_id, request.kafka_topic, request.pipeline_name, request.max_event, request.max_time),
            daemon=True
        )
        self.consumers[request.consumer_id]['thread'] = thread
        thread.start()

    @handle_exceptions
    def stop_consumer(self, consumer_id: str):
        with self.consumers_lock:
            if consumer_id not in self.consumers:
                return {"message": f"Consumer '{consumer_id}' not running."}
            
            consumer_data = self.consumers.pop(consumer_id)
            consumer_data['consumer'].close()
            return {"message": f"Stopped consumer '{consumer_id}'."}

    def _message_consumption_loop(self, consumer_id: str, topic: str, pipeline_name: str, max_event: int, max_time: int):
        consumer = self.consumers[consumer_id]['consumer']
        consumer.subscribe([topic])

        try:
            while self.consumers[consumer_id]['running']:
                msg = consumer.poll(timeout=1.0)
                if msg is None:
                    continue
                
                if msg.error():
                    self._handle_kafka_error(msg.error(), topic)
                    continue
                
                self._process_message(msg, pipeline_name, max_event, max_time)
        except Exception as e:
            logging.error(f"Consumer {consumer_id} error: {e}")
        finally:
            consumer.close()
            self._mark_consumer_stopped(consumer_id)

    def _handle_kafka_error(self, error: KafkaError, topic: str):
        if error.code() == KafkaError._PARTITION_EOF:
            logging.info(f"Reached end of partition for {topic}.")
        else:
            logging.error(f"Consumer error: {error}")

    def _mark_consumer_stopped(self, consumer_id: str):
        with self.consumers_lock:
            if consumer_id in self.consumers:
                self.consumers[consumer_id]['running'] = False

    def _process_message(self, msg, pipeline_name: str, max_event: int, max_time: int):
        message = json.loads(msg.value().decode('utf-8'))
        payload = message.get('payload', {})
        
        event_type = self._get_event_type(payload.get('op'))
        date_time, formatted_date = self._parse_timestamp(payload.get('ts_ms'))
        
        source = payload.get('source', {})
        self._update_redis_state(
            pipeline_name, 
            event_type,
            formatted_date,
            source.get('table'),
            source.get('schema'),
            source.get('db'),
            max_event,
            max_time
        )
    def _update_redis_state(self, pipeline_name: str, event_type: str, formatted_date: str, 
                          table: str, schema: str, db: str, max_event: int, max_time: int):
        redis_key = self._generate_redis_key(pipeline_name)
        existing_data = self.redis_client.hgetall(redis_key)

        if existing_data and existing_data.get('event'):
            self._update_existing_event(redis_key, existing_data, event_type, formatted_date)
        else:
            self._create_new_event(redis_key, event_type, formatted_date, table, schema, db)

        self._check_sync_requirements(redis_key, event_type, formatted_date, max_event, max_time)

    def _create_new_event(self, redis_key: str, event_type: str, formatted_date: str,
                        table: str, schema: str, db: str):
        new_event = {
            'event_type': event_type,
            'first_event_time': formatted_date,
            'last_event_time': formatted_date,
            'event_count': 1
        }
        redis_message = {
            'table_name': table,
            'schema_name': schema,
            'db_name': db,
            'event': json.dumps(new_event),
        }
        self.redis_client.hset(redis_key, mapping=redis_message)

    def _update_existing_event(self, redis_key: str, existing_data: dict, 
                             event_type: str, formatted_date: str):
        existing_event = json.loads(existing_data['event'])
        updated_event = {
            'event_type': event_type,
            'first_event_time': existing_event.get('first_event_time', formatted_date),
            'last_event_time': formatted_date,
            'event_count': existing_event.get('event_count', 0) + 1
        }
        self.redis_client.hset(redis_key, 'event', json.dumps(updated_event))

    def _check_sync_requirements(self, redis_key: str, event_type: str, 
                               formatted_date: str, max_event: int, max_time: int):
        event_data = self._get_event_data(redis_key)
        if not event_data:
            return

        if self._should_trigger_sync(event_data, max_event, max_time):
            self.trigger_sync(redis_key, event_type, formatted_date)

    def _get_event_data(self, redis_key: str) -> dict:
        try:
            event_json = self.redis_client.hget(redis_key, 'event')
            return json.loads(event_json) if event_json else {}
        except json.JSONDecodeError:
            logging.error(f"Invalid JSON in Redis key {redis_key}")
            return {}

    def _should_trigger_sync(self, event_data: dict, max_event: int, max_time: int) -> bool:
        if event_data.get('event_count', 0) >= max_event:
            logging.info(f"Event count threshold reached: {event_data['event_count']}")
            return True

        last_event_str = event_data.get('last_event_time')
        if not last_event_str:
            return False

        try:
            last_event = datetime.strptime(last_event_str, '%Y-%m-%d %H:%M:%S')
            time_diff = datetime.utcnow() - last_event
            if time_diff.total_seconds() > max_time:
                logging.info(f"Time threshold reached: {time_diff} since last event")
                return True
        except Exception as e:
            logging.error(f"Error parsing last event time: {e}")
        
        return False

    def trigger_sync(self, redis_key: str, event_type: str, formatted_date: str):
        print(f"Sync triggered for {redis_key} ({event_type} at {formatted_date})")
        self._reset_event_count(redis_key)

    def _reset_event_count(self, redis_key: str):
        event_data = self._get_event_data(redis_key)
        if not event_data:
            return

        event_data['event_count'] = 0
        self.redis_client.hset(redis_key, 'event', json.dumps(event_data))
        print(f"Reset event count for {redis_key}")

    @handle_exceptions
    def get_consumer_info(self, consumer_id: str):
        with self.consumers_lock:
            consumer_info = self.consumers.get(consumer_id)
        
        if not consumer_info:
            return {"message": f"Consumer '{consumer_id}' not running."}
        
        consumer = consumer_info['consumer']
        return {
            "consumer_id": consumer_id,
            "topic": consumer_info['topic'],
            "running": consumer_info['running'],
            "thread": "running" if consumer_info['running'] else "stopped",
            "consumer_info": str(consumer),
        }

    @handle_exceptions
    def list_consumers(self):
        with self.consumers_lock:
            if not self.consumers:
                return {"message": "No active consumers"}
            
            return {
                "running_consumers": [{
                    "consumer_id": cid,
                    "topic": data["topic"],
                    "running": data["running"],
                    "thread_status": "running" if data["running"] else "stopped"
                } for cid, data in self.consumers.items()]
            }