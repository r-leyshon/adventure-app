"""Iteration 1: How to query the OpenAI API."""
import openai


def query_openai(prompt: str, api_key: str) -> str:
    """Query the chat completions endpoint.

    Parameters
    ----------
    prompt: str
        The prompt to query the chat completions endpoint with.
    api_key: str
        The API key to use to query the chat completions endpoint.

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
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    # in cases where the API key is invalid.
    except openai.AuthenticationError as e:
        raise ValueError(f"Is your API key valid?:\n {e}")



model_response = query_openai(prompt="What is the capital of the moon?", api_key="sk-proj-1234567890")
