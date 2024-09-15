"""Iteration 1: How to query the OpenAI API."""
import openai

_SYSTEM_MSG = """
You are the guide of a 'choose your own adventure'- style game: a mystical
journey through the Amazon Rainforest. Your job is to create compelling
outcomes that correspond with the player's choices. You must navigate the
player through challenges, providing choices, and consequences, dynamically
adapting the tale based on the player's inputs. Your goal is to create a
branching narrative experience where each of the player's choices leads to
a new path, ultimately determining their fate. The player's goal is to find
the lost crown of Quetzalcoatl.

Here are some rules to follow:
1. Always wait for the player to respond with their input before providing
any choices. Never provide the player's input yourself. This is most
important.
2. Ask the player to provide a name, gender and race.
3. Ask the player to choose from a selection of weapons that will be used
later in the game.
4. Have a few paths that lead to success. 
5. Have some paths that lead to death.
6. Whether or not the game results in success or death, the response must
include the text "The End...", I will search for this text to end the game.
"""

WELCOME_MSG = """
Welcome to the Amazon Rainforest, adventurer! Your mission is to find the
lost Crown of Quetzalcoatl.
However, many challenges stand in your way. Are you brave enough, strong
enough and clever enough to overcome the perils of the jungle and secure
the crown?

Before we begin our journey, choose your name, gender and race. Choose a
weapon to bring with you. Choose wisely, as the way ahead is filled with
many dangers.
"""


def query_openai(
        prompt: str,
        api_key: str,
        sys_prompt:str = _SYSTEM_MSG,
        start_prompt:str = WELCOME_MSG,
        ) -> str:
    """Query the chat completions endpoint.

    Parameters
    ----------
    prompt: str
        The prompt to query the chat completions endpoint with.
    api_key: str
        The API key to use to query the chat completions endpoint.
    sys_prompt: str
        The system prompt to help guide the model behaviour. By default,
        the system prompt is set to _SYSTEM_MSG.
    start_prompt: str
        The start prompt which will be presented to the user as the app
        begins. By default, the start prompt is set to WELCOME_MSG.

    Returns
    -------
    str
        The response from the chat completions endpoint.
    """

    client = openai.OpenAI(api_key=api_key)
    # need to handle cases where queries go wrong.
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": sys_prompt},
                {"role": "assistant", "content": start_prompt},
                {"role": "user", "content": prompt},
            ]
        )
        return response.choices[0].message.content
    # in cases where the API key is invalid.
    except openai.AuthenticationError as e:
        raise ValueError(f"Is your API key valid?:\n {e}")


model_response = query_openai(
    prompt="What is the capital of the moon?",
    api_key="sk-proj-1234567890"
    )
