import re
from dataclasses import dataclass, field
from typing import List

@dataclass
class BotConfig:
    ModelName: str = ""
    HostAddress: str = ""
    Rules: List[str] = field(default_factory=list)
    Contexts: List[str] = field(default_factory=list)

def parse_bot_config_to_class(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    result = {}
    current_key = None
    buffer = []
    in_code_block = False

    for line in lines:
        stripped = line.strip()

        if not stripped.startswith("```"):
            match = re.match(r"#\s*(\w+)", stripped)
            if match:
                if current_key:
                    result[current_key] = buffer[0] if len(buffer) == 1 else buffer
                current_key = match.group(1)
                buffer = []
                continue

            if current_key and stripped:
                buffer.append(stripped)

    if current_key:
        result[current_key] = buffer[0] if len(buffer) == 1 else buffer

    return BotConfig(
        ModelName=result.get("ModelName", ""),
        HostAddress=result.get("HostAddress", ""),
        Rules=result.get("Rules", []),
        Contexts=result.get("Contexts", [])
    )

# Usage
file_path = 'bot_build/bot1.txt'
bot_config = parse_bot_config_to_class(file_path)

# Print the result
print(f"Model Name: {bot_config.ModelName}")
print(f"Host Address: {bot_config.HostAddress}")
print("Rules: ")
for rule in bot_config.Rules:
    print(f"- {rule}")
print("Contexts: ")
for context in bot_config.Contexts:
    print(f"- {context}")