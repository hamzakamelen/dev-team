from agents import Agent
from .experts import frontend_expert, backend_expert, ai_expert, full_stack_expert
from guardrails.input_guardrail import input_guardrails_func
from guardrails.output_guardrail import output_guardrails_func

manager = Agent(
    name="Manager",
    instructions="""
    You are a Manager. Route incoming user questions to the correct expert agent.

    Rules:
    - Frontend only → Frontend Expert
    - Backend only → Backend Expert
    - AI/ML/Agents → AI Expert
    - Full Stack (frontend + backend) → Full Stack Expert
    - Otherwise → Say politely it's outside scope.
    """,
    input_guardrails=[input_guardrails_func],
    output_guardrails=[output_guardrails_func],
    handoffs=[frontend_expert, backend_expert, ai_expert, full_stack_expert],
)
