import asyncio

from lumen.ai.llm import Kilo

MODEL = "nvidia/nemotron-3-ultra-550b-a55b:free"


async def main():
    llm = Kilo(
        model_kwargs={"default": {"model": MODEL}},
        usage_pricing={MODEL: {"input": 0.0, "output": 0.0}},  # USD per million tokens
    )
    with llm.capture_usage() as usage:
        await llm.invoke([{"role": "user", "content": "Name one penguin species."}])
    print(usage.input_tokens, usage.output_tokens, usage.cost_usd)


asyncio.run(main())
