"""Iteration 4: Server logic allows us to create a chat log."""
import openai
from shiny import App, ui

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

# compose a message stream
_SYS = {"role": "system", "content": _SYSTEM_MSG}
_WELCOME = {"role": "assistant", "content": WELCOME_MSG}
stream = [_SYS, _WELCOME]

# Shiny User Interface ----------------------------------------------------

app_ui = ui.page_fillable(
    ui.panel_title("Choose Your Own Adventure: Jungle Quest!"),
    ui.accordion(
    ui.accordion_panel("Step 1: Your OpenAI API Key",
        ui.input_text(id="key_input", label="Enter your openai api key"),
    ), id="acc", multiple=False),
    ui.chat_ui(id="chat"),
    fillable_mobile=True,
)

# Shiny server logic ------------------------------------------------------


def server(input, output, session):
    chat = ui.Chat(
        id="chat", messages=[ui.markdown(WELCOME_MSG)], tokenizer=None
        )
    

    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def respond():
        """Respond to the user's message.
        
        We use async here because:
        1. It allows the function to perform I/O operations
        (like API calls) without blocking the entire application.
        2. It improves responsiveness, especially when dealing with
        potentially slow network requests to the OpenAI API.
        3. It works well with Shiny's event-driven architecture, allowing
        other parts of the app to remain interactive while waiting for the
        API response.
        """
        # Get the user's input
        user = chat.user_input()
        #  update the stream list
        stream.append({"role": "user", "content": user})
        # Append a response to the chat
        client = openai.AsyncOpenAI(api_key=input.key_input())
        response = await client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=stream,
            temperature=0.7, # increase to make the model more creative
            )
        model_response = response.choices[0].message.content
        await chat.append_message(model_response)
        #  if the model indicates game over, end the game with a message.
        if "the end..." in model_response.lower():
            await chat.append_message(
                {
                    "role": "assistant",
                    "content": "Game Over! Refresh the page to play again."
                    })
            exit()
        else:
            stream.append({"role": "assistant", "content": model_response})


app = App(ui=app_ui, server=server)
