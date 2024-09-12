"""Main app file for the Jungle Quest game."""

from pathlib import Path

from faicons import icon_svg
import openai
from shiny import App, ui, reactive
from shinyswatch import theme

from constants import WELCOME_MSG, stream
from handle_credentials import api_key_ui, api_key_server
        
# ui ----------------------------------------------------------------------
# Create a welcome message for use in chat stream
welcome = ui.markdown(
    WELCOME_MSG
)
app_ui = ui.page_fillable(
    ui.div(
        ui.div(ui.p("Powered by"), style="float:left;"),
        ui.div(
            ui.img(src="openai.png", width="60rem"),
            style="float:left;padding-left:0.2rem;"
            ),
        ui.div(
            ui.p(f", made with "),
            style="float: left;padding-left:0.2rem"),
        ui.img(
            src="shiny-for-python.svg",
            width="100rem",
            style="padding-left:0.2rem;padding-top:0.2rem;float:left;"),
    ),
    ui.panel_title("Choose Your Own Adventure: Jungle Quest!"),
    ui.accordion(
        api_key_ui("api_key"),
        id="acc", multiple=False, icon=str(icon_svg("key")),
    ), 
    ui.div(
        ui.div(
            ui.h6("Step 2: Choose your adventure"), style="float:left;"),
        ui.div(
            icon_svg("dungeon", a11y="decorative", position="absolute"),
            style="float:left;padding-left:0.2rem;"),
    ),
        ui.chat_ui("chat"),
        theme=theme.darkly,

        fillable_mobile=True,
)

# server ------------------------------------------------------------------
def server(input, output, session):
    # openai_client = reactive.Value(None)
    chat = ui.Chat(id="chat", messages=[welcome], tokenizer=None)
    openai_client = api_key_server("api_key")


    async def check_moderation(
            prompt:str, reactive_client:reactive.Value=openai_client
            ) -> str:
        """Check if the prompt is flagged by OpenAI's moderation tool.

        Awaits the response from the OpenAI moderation tool before
        attempting to access the content.

        Parameters
        ----------
        prompt : str
            The user's prompt to check.
        reactive_client : reactive.Value
            The reactive value holding an OpenAI client instance,
            openai_client by default.

        Returns
        -------
        str
            The category violations if flagged, otherwise "good prompt".
        """

        response = await openai_client.get().moderations.create(
            input=prompt)
        content = response.results[0].to_dict()
        if content["flagged"]:
            infringements = []
            for key, val in content["categories"].items():
                if val:
                    infringements.append(key)
            return " & ".join(infringements)
        else:
            return "good prompt"


    # Define a callback to run when the user submits a message
    @chat.on_user_submit
    async def respond():
        """Logic for handling prompt & appending to chat stream."""
        # Get the user's input
        usr_prompt = chat.user_input()
        # Check moderation
        flag_check = await check_moderation(usr_prompt)
        if flag_check != "good prompt":
            await chat.append_message({
                "role": "assistant",
                "content": f"Your message may violate OpenAI's usage policy, categories: {flag_check}. Please rephrase your input and try again."
            })
        else:
            #  update the stream list
            stream.append({"role": "user", "content": usr_prompt})
            # Append a response to the chat
            response = await openai_client.get().chat.completions.create(
                model="gpt-3.5-turbo",
                messages=stream
            )
            model_response = response.choices[0].message.content
            await chat.append_message(model_response)

            if "the end..." in model_response.lower():
                await chat.append_message(
                    {"role": "assistant",
                    "content": "Game Over! Click refresh to play again. Remember to add your API key once more if playing again."}
                    )
                exit()
            else:
                stream.append(
                    {"role": "assistant", "content": model_response})


app_dir = Path(__file__).parent
app = App(app_ui, server, static_assets=app_dir / "www")
