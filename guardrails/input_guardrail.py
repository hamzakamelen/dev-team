from dev_agents import Agent, Runner, input_guardrail, RunContextWrapper, GuardrailFunctionOutput, TResponseInputItem
from pydantic import BaseModel
from config.settings import model

class OutputDomain(BaseModel):
    is_domain_related: bool
    reasoning: str

input_guardrails_agent = Agent(
    name="Input Guardrail Checker",
    instructions="""
    You are a topic classification guardrail.
    Analyze the user's question and determine if it is related to:
    - Frontend Development
    - Backend Development
    - Artificial Intelligence
    - Full Stack Development
    """,
    model=model,
    output_type=OutputDomain
)

@input_guardrail
async def input_guardrails_func(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem] # type: ignore
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrails_agent, input)
    return GuardrailFunctionOutput(
        output_info=result.final_output,
        tripwire_triggered=not result.final_output.is_domain_related
    )
