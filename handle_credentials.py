"""Handle the API key input and validation."""
from shiny import ui, module, reactive
from faicons import icon_svg
import openai


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


@module.ui
def api_key_ui():
    """
    UI component, combining supporting text elements with the submission
    field / button combo, provided by input_text_with_button().
    """
    return ui.accordion_panel("Step 1: Your OpenAI API Key",
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
    )
# dropped icon? Line 70 in app.py

@module.server
def api_key_server(input, output, session) -> reactive.Value:
    """
    Server module for the api_key_ui component. Serves a shiny reactive
    value containing an OpenAI client instance, if the API key is valid.

    Returns
    -------
    openai_client : reactive.Value
        A reactive value containing an OpenAI client instance, if the API
        key is valid.
    """
    openai_client = reactive.Value(None)


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
    

    return openai_client
