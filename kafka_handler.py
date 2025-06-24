import os
import json
import asyncio
from kafka import KafkaConsumer, KafkaProducer
from main import process_trend_data

# Kafka 서버 주소와 토픽 이름 설정
KAFKA_BROKER_URL = os.environ.get("KAFKA_BROKER_URL", "localhost:19092")
CONSUMER_TOPIC = os.environ.get("CONSUMER_TOPIC", "trend-keywords")
PRODUCER_TOPIC = os.environ.get("PRODUCER_TOPIC", "trend-results")
CONSUMER_GROUP_ID = os.environ.get("CONSUMER_GROUP_ID", "trend-agent-group")

def json_serializer(data):
    return json.dumps(data, ensure_ascii=False).encode("utf-8")

def json_deserializer(data):
    try:
        return json.loads(data.decode("utf-8"))
    except json.JSONDecodeError:
        print(f"경고: JSON 디코딩 실패. 원본 메시지: {data}")
        return {}

def key_deserializer(key):
    if key:
        return key.decode('utf-8')
    return None

# Kafka Producer 인스턴스 (결과 전송용)
producer = KafkaProducer(
    bootstrap_servers=[KAFKA_BROKER_URL],
    value_serializer=json_serializer,
    acks='all', # 모든 리플리카에 저장 확인
    retries=3   
)

def consume_and_process():
    """Kafka로부터 메시지를 계속 수신하고 처리하는 메인 루프"""
    consumer = KafkaConsumer(
        CONSUMER_TOPIC,
        bootstrap_servers=[KAFKA_BROKER_URL],
        auto_offset_reset="earliest", 
        group_id=CONSUMER_GROUP_ID,
        key_deserializer=key_deserializer,
        value_deserializer=json_deserializer
    )

    for message in consumer:
        try:
            keyword = message.key
            trend_details = message.value

            if not (keyword and trend_details):
                print("경고: 유효하지 않은 메시지 수신 (키 또는 값이 비어있음)")
                continue

            print("\n" + "="*80)
            print(f"새 메시지 수신 (Offset: {message.offset}): 키워드 '{keyword}'")

            trend_data = {"keyword": keyword, **trend_details}
            
            final_result = asyncio.run(process_trend_data(trend_data))
            
            if final_result:
                print(f"처리 완료. 결과를 '{PRODUCER_TOPIC}' 토픽으로 전송")
                producer.send(PRODUCER_TOPIC, key=keyword.encode('utf-8'), value=final_result)
                producer.flush()
            else:
                print("처리 결과가 없어 Kafka로 전송하지 않습니다.")
                
        except Exception as e:
            print(f"처리 중 심각한 에러 발생: {e}")

if __name__ == "__main__":
    try:
        consume_and_process()
    except KeyboardInterrupt:
        print("\n프로그램을 종료합니다.")