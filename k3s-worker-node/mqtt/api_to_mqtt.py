#!/usr/bin/env python3
import json
import aiohttp
import asyncio
import paho.mqtt.client as mqtt

# terminal ---> mosquitto_sub -h localhost -t sonar/readings


MQTT_BROKER_HOST = "broker-service"
MQTT_BROKER_PORT = 1883
MQTT_TOPIC = "sonar/readings"


async def retrieve_sse():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post('http://nginx-service:80/distance/sonar') as response:
                    async for line in response.content:
                        if line.startswith(b'data:'):
                            data = json.loads(line.decode().strip()[6:])
                            mqtt_client.publish(MQTT_TOPIC, json.dumps(data))
        except asyncio.TimeoutError:
            await asyncio.sleep(3)




# def on_message(client, userdata, message):
#     print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")

# Set up MQTT client
mqtt_client = mqtt.Client()
# mqtt_client.on_message = on_message
mqtt_client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)
mqtt_client.subscribe(MQTT_TOPIC)
mqtt_client.loop_start()

# Start retrieving SSE and publishing to MQTT broker
asyncio.ensure_future(retrieve_sse())

# Wait for the asyncio loop to complete
asyncio.get_event_loop().run_forever()

