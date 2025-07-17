import openai
import asyncio

class LLM:
    def __init__(self, api_key: str, model: str = "gpt-3.5-turbo", stream: bool = True):
        self.api_key = api_key
        self.model = model
        self.stream = stream
        openai.api_key = api_key

    async def chat(self, messages, stream=None, **kwargs):
        if stream is None:
            stream = self.stream
        loop = asyncio.get_event_loop()
        if stream:
            def stream_request():
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    stream=True,
                    **kwargs
                )
                content = ""
                for chunk in response:
                    delta = getattr(chunk.choices[0].delta, 'content', None)
                    if delta:
                        content += delta
                return content
            content = await loop.run_in_executor(None, stream_request)
            return content
        else:
            def normal_request():
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    **kwargs
                )
                return response.choices[0].message.content
            content = await loop.run_in_executor(None, normal_request)
            return content
