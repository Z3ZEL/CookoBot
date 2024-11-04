import requests
import json
from dotenv import load_dotenv
import os
import time

# Load the .env file
dotenv = load_dotenv()

def make_prompt(user_message, objects, player):
    # Create a prompt
    prompt = f"""The user will give you an instruction, you have to transform it into a command that the player can execute. 
    The player is on a 15x15 tile map with different objects on some tiles.

    The player can do 3 different actions:
    - MOVE X,Y : move the player to the tile at position X,Y
    - PICK : pick up the object on the tile where the player is
    - DROP : drop the first object the player is holding

    You will get the following informations:
    - the player position (X,Y)
    - the position of the objects on the map

    INFORMATIONS:
    PLAYER POSITION: {player}
    OBJECTS POSITION: {objects}

    You must only answer with a command that the player can execute : MOVE X,Y, PICK or DROP.
    You must follow the format of the commands, for example: MOVE 1,2, PICK or DROP.
    You must provide a command that fits the best the user instruction.

    Example:
    USER_MESSAGE: Je veux que tu ailles à la position 1,2
    COMMAND: MOVE 1,2
    
    Your turn to answer the user message:
    USER_MESSAGE: {user_message}
    COMMAND: 
    """
    
    return prompt

# Function to make a request to the API
def make_request(prompt):

    def send_request():
        # Make a request to the API
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {os.getenv('API_KEY')}",
            },
            data=json.dumps({
                "model": "meta-llama/llama-3.1-70b-instruct:free", # Optional
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        return response.json()
    
    # Send request 
    response = send_request()
    print(response)

    # Check if the rate limit was reached
    while('error' in response and response['error']['code'] == 429): 
        # Wait for 30 seconds and try again
        print('Rate limit reached, waiting for 30 seconds')
        time.sleep(30)
        response = send_request()

    # Check if the request was successful
    if 'error' in response:
        raise Exception(f"Failed to make the request: {response.json()}")

    # Get the answer from the response
    answer = response['choices'][0]['message']['content']
    print(answer)
    return answer