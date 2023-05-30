from flask import Flask, jsonify, request
from flask_cors import CORS
from confluent_kafka import Producer , KafkaError
import json

app = Flask(__name__)
CORS(app)
producer = Producer({'bootstrap.servers': 'kafka:9092'})

class Teacher:
    def __init__(self,course, description):

        self.course = course
        self.description = description


@app.route('/add', methods=['POST'])
def add_course_to_kafka():
    data = request.get_json()
    try:
        
        producer.produce('my_topic', value=json.dumps(data).encode('utf-8'), headers={'method_type': 'POST'})
        producer.flush()
        return jsonify({'message': 'course sended successfully to student.'})
    except KafkaError as e:
        return jsonify({'error': str(e)})
    

@app.route('/delete', methods=['DELETE'])
def delete_course_to_kafka():
    
    data = request.get_json()
    try:
        producer.produce('my_topic', value=json.dumps(data).encode('utf-8'), headers={'method_type': 'DELETE'})
        producer.flush()
        return jsonify({'message': 'course sended successfully to student.'})
    except KafkaError as e:
        return jsonify({'error': str(e)})
    

@app.route('/update', methods=['PUT'])
def update_course_to_kafka():
    data = request.get_json()
    try:
        producer.produce('my_topic', value=json.dumps(data).encode('utf-8'), headers={'method_type': 'PUT'})
        producer.flush()
        return jsonify({'message': 'course sended successfully to student.'})
    except KafkaError as e:
        return jsonify({'error': str(e)})
    


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port = 5000)