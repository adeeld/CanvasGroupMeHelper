import requests
import json


# Canvas API URL
API_URL = "https://rutgers.instructure.com/api/v1"

# API token generated from your Canvas account
API_KEY = input("Paste your API key here: ")

# id of the course you're trying to get students from
course_id = input("Paste course ID here: ") # Replace with your actual course ID


# function to get all students in a course
def get_students(course_id):
    students = []
    endpoint = f"{API_URL}/courses/{course_id}/users?per_page=100"  # adjusts per_page 
    headers = {'Authorization': f'Bearer {API_KEY}'}
    while endpoint:
        response = requests.get(endpoint, headers=headers)
        if response.status_code == 200:
            students.extend(response.json())
            # parse the link header for pagination
            link_header = response.headers.get('Link', None)
            if link_header:
                links = link_header.split(',')
                next_url = None
                for link in links:
                    if 'rel="next"' in link:
                        next_url = link.split(';')[0].strip('<> ')
                endpoint = next_url
            else:
                break
        else:
            #handle errors
            print(f"Error fetching page: {response.status_code}")
            print(response.json())
            break
    return students

def send_message(user_ids, subject, body):
    endpoint = f"{API_URL}/conversations"
    headers = {'Authorization': f'Bearer {API_KEY}'}
    data = {
        'recipients[]': user_ids,
        'subject': subject,
        'body': body
    }
    response = requests.post(endpoint, headers=headers, data=data)
    return response.json()

# send_message has limitation of 10, this function takes ID list as input and splits it into groups of 10
def send_messages_in_batches(user_ids, subject, body, batch_size=10):
    # splits user IDs into batches of the specified size since the limit was 10 each page 
    batches = [user_ids[i:i + batch_size] for i in range(0, len(user_ids), batch_size)]
    responses = []
    for batch in batches:
        response = send_message(batch, subject, body)
        responses.append(response)
    return responses


students = get_students(course_id)

# assuming the student data includes an 'id' field
student_ids = []
for student in students:
    student_ids.append(student['id'])

# send a message
subject = input("input your GroupMe link here: ")
body = input("Input your body for GroupMe message: ")

# send a message in batches (very cool)
responses = send_messages_in_batches(student_ids, subject, body)

# printing responses for logging purposes
#for response in responses:
#   print(response)

# send_message(student_ids, subject, body)
