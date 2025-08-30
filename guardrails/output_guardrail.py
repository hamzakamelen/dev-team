from dev_agents import Agent, Runner, output_guardrail, RunContextWrapper, GuardrailFunctionOutput
from pydantic import BaseModel
from config.settings import model

class AIDomainOutput(BaseModel):
    is_domain_related: bool
    reasoning: str

output_guardrails_agent = Agent(
    name="Output Guardrail Checker",
    instructions="""
    You are a topic classification guardrail.
    Analyze the AI's response and determine if it is related to:
    - Frontend Development
    - Backend Development
    - Artificial Intelligence
    - Full Stack Development
    """,
    model=model,
    output_type=AIDomainOutput
)

@output_guardrail
async def output_guardrails_func(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output
) -> GuardrailFunctionOutput:
    output_result = await Runner.run(output_guardrails_agent, output)
    return GuardrailFunctionOutput(
        output_info=output_result.final_output,
        tripwire_triggered=not output_result.final_output.is_domain_related
    )
