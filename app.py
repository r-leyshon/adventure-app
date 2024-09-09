from pathlib import Path

from faicons import icon_svg
import openai
from openai import OpenAIError
from shiny import App, ui, reactive
from shinyswatch import theme


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

# compose the messages log
_SYS = {"role": "system", "content": _SYSTEM_MSG}
stream = [_SYS]

WELCOME_MSG = """
Welcome to the Amazon Rainforest, adventurer! Your mission is to find the
lost Crown of Quetzalcoatl:\n
<div style="display: grid; place-items: center;"><img src="https://i.imgur.com/Fxa7p1D.jpeg" width=60%/></div>\n
However, many challenges stand in your way. Are you brave enough, strong
enough and clever enough to overcome the perils of the jungle and secure
the crown?

Before we begin our journey, choose your name, gender and race. Choose a
weapon to bring with you. Choose wisely, as the way ahead is filled with
many dangers.

"""
# compose the messages log
_SYS = {"role": "system", "content": _SYSTEM_MSG}
stream = [_SYS]
stream.append({"role": "assistant", "content": WELCOME_MSG})

# Create a welcome message
welcome = ui.markdown(
    WELCOME_MSG
)


# ui ----------------------------------------------------------------------
app_ui = ui.page_fillable(

    ui.div(
        ui.div(ui.p("Powered by"), style="float:left;"),
        ui.div(
            ui.img(src="openai.png", width="60rem"),
            style="float:left;padding-left:0.2rem;"
            ),
        ui.div(ui.p(f", made with "), style="float: left;padding-left:0.2rem"),
        ui.img(src="shiny-for-python.svg", width="100rem", style="padding-left:0.2rem;padding-top:0.2rem;float:left;"),
    ),
    ui.panel_title("Choose Your Own Adventure: Jungle Quest!"),
    ui.accordion(
    ui.accordion_panel("Step 1: Your OpenAI API Key",
        ui.div(
            icon_svg("key", a11y="decorative", position="absolute"),
                style="float:left;padding-left:12.2rem;"),
        ui.input_text(id="key_input", label="Enter your openai api key"),
        ui.markdown(
            "**Note:** The app does not store your key when the session ends."
            ),
        ui.p(
            "Using openai api costs money. Please monitor your account fees."),
        ui.markdown("To get an API key, follow to [OpenAI API Sign Up](https://openai.com/index/openai-api/)"),
    ), id="acc", multiple=False, icon=str(icon_svg("key")),
    ), 
    ui.div(
        ui.div(ui.h6("Step 2: Choose your adventure"), style="float:left;"),
        ui.div(icon_svg("dungeon", a11y="decorative", position="absolute"), style="float:left;padding-left:0.2rem;"),
    ),
        ui.chat_ui("chat"),
        theme=theme.darkly,

        fillable_mobile=True,
)


# server ------------------------------------------------------------------
def server(input, output, session):

    chat = ui.Chat(id="chat", messages=[welcome])
    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def _():
        # Get the user's input
        user = chat.user_input()
        #  update the stream list
        stream.append({"role": "user", "content": user})
        # Append a response to the chat
        client = openai.OpenAI(api_key=input.key_input())
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=stream
            )
        model_response = response.choices[0].message.content
        await chat.append_message(model_response)
        if "the end..." in model_response.lower():
            await chat.append_message(
                {"role": "assistant",
                "content": "Game Over! Refresh the page to play again."}
                )
            exit()
        else:
            stream.append({"role": "assistant", "content": model_response})


app_dir = Path(__file__).parent
app = App(app_ui, server, static_assets=app_dir / "www")