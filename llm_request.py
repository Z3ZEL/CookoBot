import requests
import json
from dotenv import load_dotenv
import os
import time

# Load the .env file
dotenv = load_dotenv()

def make_prompt(user_message, objects, player, inventory):
    # Create a prompt
    prompt = f"""
    You are an AI helping a player to play a game.
    The world is a 15 by 15 grid. Each cell has coordinates (x, y) and can contain an object.
    The objects are fruits, and they are randomly placed on the grid.
    The player can move around the world, pick up fruits into their inventory, and drop them on an empty cell.
    The player can only pick up and drop a fruit on the cell they are currently on.
    
    The player can perform the following actions:

    - MOVE X,Y
    - PICK 
    - DROP

    Your goal is to follow the player's natural language instructions and help them play the game.
    You can only perform one action at a time. For instance if the instruction is to pick up a pear, if you're not on a pear, you must
    move to a case with a pear inside, then if you're on a pear, then you can pick it up.
    

    Here is the state of the world:
    {objects}

    Here is the player state:
    {player}
    
    Here is your current inventory:
    {inventory}

    Here is the user's message:
    {user_message}

    You must respond in a very specific format that you must strictly follow:
    Your message should start with "THOUGHTS:" followed by a brief sentence (no more than 50 words) explaining your reasoning.
    Then you should write "COMMAND:" followed by the commands available as stated earlier. If you have to perform multiple actions in a row
    you can separate them with ":" character. Of course the first will be the first triggered.


    Examples:

    THOUGHTS: To pick up an apple, I need to first be on a cell containing an apple, the closest one is at 10,10, then I will be able to pick it up
    COMMAND: MOVE 10,10:PICK

    ---
    THOUGHTS: To pick up a pear, I am already on a case with a pear, I just have to pick it up.
    COMMAND: PICK


    ---
    This is exemples but of course you can stack more than 2 actions in a row if needed. You can stack as many as you want. 
    """
    print(prompt)
    return prompt

# Function to extract the thoughts and command from the text
def extract_thoughts_and_command(text):
    # Initialiser les variables pour stocker les thoughts et la commande
    thoughts = None
    actions = None

    # Extraire les thoughts
    if "THOUGHTS:" in text:
        start_thoughts = text.index("THOUGHTS:") + len("THOUGHTS:")
        end_thoughts = text.index("COMMAND:")
        thoughts = text[start_thoughts:end_thoughts].strip()

    # Extraire la commande
    if "COMMAND:" in text:
        command_part = text.split("COMMAND:")[1].strip()
        actions = command_part.split(":")

    return thoughts, actions

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
    # print(response)

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