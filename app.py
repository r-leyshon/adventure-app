"""Main app file for the Jungle Quest game."""

from pathlib import Path

from faicons import icon_svg
import openai
from shiny import App, ui, reactive
from shinyswatch import theme

from constants import WELCOME_MSG, stream

# Create a welcome message
welcome = ui.markdown(
    WELCOME_MSG
)

def input_text_with_button(id, label, button_label, placeholder=""):
    """
    An interface component combining an input text widget with an action
    button. IDs for the text field and button can be accessed as <id>_text
    and <id>_btn respectively.
    """
    return ui.div(
        ui.input_text(
            id=f"{id}_text", label=label, placeholder=placeholder),
        ui.input_action_button(
            id=f"{id}_btn",
            label=button_label,
            style="margin-top:32px;margin-bottom:32px;color:#04bb8c;border-color:#04bb8c;"
            ),
        class_="d-flex gap-2"
    )
        
# ui ----------------------------------------------------------------------
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
    ui.accordion_panel("Step 1: Your OpenAI API Key",
        ui.div(
            icon_svg("key", a11y="decorative", position="absolute"),
                style="float:left;padding-left:12.2rem;"),
        input_text_with_button(
            id="key_input",
            label="Enter your OpenAI API key",
            button_label="Submit",
            placeholder="Enter API key here"
        ),
        ui.markdown(
            "**Note:** The app doesn't store your key between sessions."
            ),
        ui.p(
            "Using openai api costs money. Monitor your account fees."),
        ui.markdown(
            "To get an API key, follow to [OpenAI API Sign Up](https://openai.com/index/openai-api/)"
            ),
    ), id="acc", multiple=False, icon=str(icon_svg("key")),
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
    openai_client = reactive.Value(None)
    chat = ui.Chat(id="chat", messages=[welcome], tokenizer=None)


    @reactive.Effect
    @reactive.event(input.key_input_btn)
    async def handle_api_key_submit(
        reactive_client:reactive.Value=openai_client):
        """Update the UI with a notification when user submits key.
        
        Checks the validity of the API key by querying the models list
        endpoint.

        Parameters
        ----------
        reactive_client : reactive.Value
            The reactive value holding an OpenAI client instance,
            openai_client by default.
        """

        api_key = input.key_input_text()
        client = openai.AsyncOpenAI(api_key=api_key)
        try:
            resp = await client.models.list()
            if resp:
                openai_client.set(client)
                ui.notification_show(
                    f"API key validated: {api_key[:5]}...")
        except openai.AuthenticationError as e:
            ui.notification_show(
                "Bad key provided. Please try again.", type="warning")
            

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
        flag_check = await check_moderation(
            usr_prompt, input.key_input_text())
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
