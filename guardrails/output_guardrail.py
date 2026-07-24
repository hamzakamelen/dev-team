from dev_agents import Agent, Runner, output_guardrail, RunContextWrapper, GuardrailFunctionOutput
from pydantic import BaseModel
from config.settings import model
import json

class AIDomainOutput(BaseModel):
    is_domain_related: bool
    reasoning: str

output_guardrails_agent = Agent(
    name="Output Guardrail Checker",
    instructions="""You are a topic classification guardrail.
Analyze the AI's response and determine if it is related to:
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

@output_guardrail
async def output_guardrails_func(
    ctx: RunContextWrapper[None],
    agent: Agent,
    output
) -> GuardrailFunctionOutput:
    output_result = await Runner.run(output_guardrails_agent, output)
    raw = str(output_result.final_output).strip()

    # Strip markdown code fences if present
    if "```" in raw:
        parts = raw.split("```")
        raw = parts[1] if len(parts) >= 2 else raw
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    try:
        data = json.loads(raw)
        result = AIDomainOutput(
            is_domain_related=bool(data.get("is_domain_related", True)),
            reasoning=str(data.get("reasoning", ""))
        )
    except Exception:
        result = AIDomainOutput(is_domain_related=True, reasoning="Classification unavailable, allowing by default.")

    return GuardrailFunctionOutput(
        output_info=result,
        tripwire_triggered=not result.is_domain_related
    )
