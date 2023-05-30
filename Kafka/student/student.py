from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from confluent_kafka import Consumer 
import json

app = Flask(__name__)
CORS(app)

consumer = Consumer({
    'bootstrap.servers': 'kafka:9092',
    'group.id': 'my_group',
    'enable.auto.commit': True,
    'auto.offset.reset': 'earliest',
    
})

# Subscribe to the 'my_topic' topic
consumer.subscribe(['my_topic'])
  
class Student:
    
    @classmethod
    def add_to_db(cls,course_name,description):
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='1234',
                                      host='my-mysql', database='courses_db')
        cursor = cnx.cursor()

        # Define the query to retrieve all data
        query = "INSERT INTO courses (course, description) VALUES (%s, %s)"
        values = (course_name, description)
        
        cursor.execute(query, values)
        cnx.commit()

        cursor.close()
        cnx.close()


    def delete_from_db(course_name):
       try:
           cnx = mysql.connector.connect(user='root', password='1234',
                                        host='my-mysql', database='courses_db')
           cursor = cnx.cursor()
           query = "DELETE FROM courses WHERE course = %s"
           values = (course_name,)
           cursor.execute(query, values)
           cnx.commit()

       except mysql.connector.Error as error:
           print("Error: {}".format(error))

       finally:
            cursor.close()
            cnx.close()
    
    def update_database(cousers_name ,cousers_description):
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='1234',
                                     host='my-mysql', database='courses_db')
        cursor = cnx.cursor()
        query = "UPDATE courses SET description = %s WHERE course = %s"
        values = (cousers_description,cousers_name)
        cursor.execute(query, values)
        cnx.commit()

        cursor.close()
        cnx.close()

    def get_all_data_from_db():
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='1234',
                                      host='my-mysql', database='courses_db')
        cursor = cnx.cursor()

        # Define the query to retrieve all data
        query = "SELECT * FROM courses"
        
        # Execute the query and retrieve all data
        cursor.execute(query)
        data = cursor.fetchall()
        
        # Close the cursor and connection
        cursor.close()
        cnx.close()
        
        return data
    def get_data_by_id(id):
        # Connect to the database
        cnx = mysql.connector.connect(user='root', password='1234',
                                    host='my-mysql', database='courses_db')
        cursor = cnx.cursor()

        # Define the query to retrieve data with a specific ID
        query = "SELECT * FROM courses WHERE course = %s"

        # Execute the query and retrieve the data
        cursor.execute(query, (id,))
        data = cursor.fetchone()

        # Close the cursor and connection
        cursor.close()
        cnx.close()

        return data

@app.route('/add_course', methods=['POST'])
def add_course():
    while True:
        try:
            msg = consumer.poll(1.0)

            if msg is None:
                 return jsonify({'message': 'not get yet'})
            
            else:
                headers = dict(msg.headers())
                method_type = headers.get('method_type', {}).decode('utf-8')
                    
                if method_type == 'POST':
                    data = json.loads(msg.value().decode('utf-8'))
                    Student.add_to_db(data['course'], data['description'])
                    return jsonify({'message': 'course added successfully.'})
        except KeyboardInterrupt:
            consumer.close()
            return jsonify({'message': 'Consumer stopped.'})

@app.route('/delete_course', methods=['DELETE'])
def delete_course():
     while True:
        try:
            msg = consumer.poll(1.0)

            if msg is None:
                return jsonify({'message': 'not get yet'})
            
            else:
                headers = dict(msg.headers())
                method_type = headers.get('method_type', {}).decode('utf-8')
                if method_type == 'DELETE':
                    data = json.loads(msg.value().decode('utf-8'))
                    Student.delete_from_db(data['course'])
                    return jsonify({'message': 'course deleted successfully.'})
        except KeyboardInterrupt:
            consumer.close()
            return jsonify({'message': 'Consumer stopped.'})
    
    
       
@app.route('/update_course', methods=['PUT'])
def update_course():
    while True:
        try:
            msg = consumer.poll(1.0)

            if msg is None:
                 return jsonify({'message': 'not get yet'})
            
            else:
                headers = msg.headers()
                method_type = headers.get('method_type', {}).decode('utf-8')
                if method_type == 'PUT':
                    data = json.loads(msg.value().decode('utf-8'))
                    Student.update_database(data['course'], data['description'])
                    return jsonify({'message': 'course update successfully.'})
        except KeyboardInterrupt:
            consumer.close()
            return jsonify({'message': 'Consumer stopped.'})
    
@app.route('/get_all_data', methods=['GET'])
def get_all_data_from_database():

    data = Student.get_all_data_from_db()
    
    # Return the data as a response
    return  jsonify({'data': data})

@app.route('/courses/<string:id>', methods=['GET'])
def get_course_by_id(id):
    data = Student.get_data_by_id(id)       
    return  jsonify({'data': data})

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5001)