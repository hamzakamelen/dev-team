import chainlit as cl
from config.settings import config
from dev_agents.manager import manager
from dev_agents.summarizer import summarizer_agent
from utils.helpers import serialize_history, clean_output, MAX_HISTORY_LENGTH
from agents import Runner, InputGuardrailTripwireTriggered, OutputGuardrailTripwireTriggered
from openai.types.responses import ResponseTextDeltaEvent

@cl.on_chat_start
async def handle_start():
    cl.user_session.set("history", [])
    await cl.Message(
        content="""
        Hi! 👋 Welcome to DevTeam - your AI-powered Developer Team.
        I can help you with:
        - Frontend Development
        - Backend Development
        - Artificial Intelligence
        - Full Stack Development
        
🚀 Just drop a question and let’s build together!
        """
    ).send()

@cl.on_message
async def handle_message(message: cl.Message):
    try:
        history = cl.user_session.get("history")
        history.append({"role": "user", "content": message.content})

        msg = cl.Message(content="")
        await msg.send()

        if len(history) > MAX_HISTORY_LENGTH:
            summary_input = serialize_history(history)
            summary_result = await Runner.run(summarizer_agent, summary_input)
            history = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "assistant", "content": f"Summary: {summary_result.final_output}"},
                *history[-4:]
            ]
            cl.user_session.set("history", history)

        result = Runner.run_streamed(
            manager,
            input=serialize_history(history),
            run_config=config
        )

        async for event in result.stream_events():
            if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                await msg.stream_token(event.data.delta)

        final_text = result.final_output
        final_text_cleaned = clean_output(final_text)

        msg.content = final_text_cleaned
        await msg.update()

        history.append({"role": "assistant", "content": final_text_cleaned})
        cl.user_session.set("history", history)

    except InputGuardrailTripwireTriggered as e:
        await cl.Message(content=f"❌ Sorry, I cannot handle that request.\nReason: {getattr(e, 'output_info', {}).reasoning}").send()

    except OutputGuardrailTripwireTriggered as e:
        msg.content=f"⚠️ Output was rejected.\nReason: {getattr(e, 'output_info', {}).reasoning}"
        await msg.update()
