from dev_agents import Agent, Runner, input_guardrail, RunContextWrapper, GuardrailFunctionOutput, TResponseInputItem
from pydantic import BaseModel
from config.settings import model
import json

class OutputDomain(BaseModel):
    is_domain_related: bool
    reasoning: str

input_guardrails_agent = Agent(
    name="Input Guardrail Checker",
    instructions="""You are a topic classification guardrail.
Analyze the user's question and determine if it is related to:
- Frontend Development
- Backend Development
- Artificial Intelligence
- Full Stack Development

You MUST respond with ONLY a raw JSON object (no markdown, no code blocks, no extra text):
{"is_domain_related": true, "reasoning": "your explanation"}
or
{"is_domain_related": false, "reasoning": "your explanation"}""",
    model=model,
)

@input_guardrail
async def input_guardrails_func(
    ctx: RunContextWrapper[None],
    agent: Agent,
    input: str | list[TResponseInputItem] # type: ignore
) -> GuardrailFunctionOutput:
    result = await Runner.run(input_guardrails_agent, input)
    raw = str(result.final_output).strip()

    # Strip markdown code fences if present
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) >= 2 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        output = OutputDomain(
            is_domain_related=bool(data.get("is_domain_related", True)),
            reasoning=str(data.get("reasoning", ""))
        )
    except Exception:
        output = OutputDomain(is_domain_related=True, reasoning="Classification unavailable, allowing by default.")

    return GuardrailFunctionOutput(
        output_info=output,
        tripwire_triggered=not output.is_domain_related
    )
