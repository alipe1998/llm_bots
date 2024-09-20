# model_config.py

MODEL_CONFIG = {
    "chatgpt": {
        "class": "GPTCompletions",
        "system_prompt": "Help the user with general questions",
        "state_file": None  # No state file needed for GPTCompletions
    },
    "llama3": {
        "class": "BedrockCompletions",
        "model": 'meta.llama3-70b-instruct-v1:0',
        "system_prompt": "You are a helpful assistant. You will be asked a lot of python coding questions.",
        "state_file": 'llama3_completions_state.json'
    },
    "jamba_instruct": {
        "class": "BedrockCompletions",
        "model": 'ai21.jamba-instruct-v1:0',
        "system_prompt": "You are a helpful assistant. You will be asked a lot of python coding questions.",
        "state_file": 'jamba_instruct_state.json'
    },
    "mistral_large": {
        "class": "BedrockCompletions",
        "model": 'mistral.mistral-large-2402-v1:0',
        "system_prompt": "You are a helpful assistant. You will be asked a lot of python coding questions.",
        "state_file": 'mistral_large_state.json'
    },
    "command_r_plus": {
        "class": "BedrockCompletions",
        "model": 'cohere.command-r-plus-v1:0',
        "system_prompt": "You are a helpful assistant. You will be asked a lot of python coding questions.",
        "state_file": 'command_r_plus.state.json'
    },
    "titan_text_premier": {
        "class": "BedrockCompletions",
        "model": 'amazon.titan-text-premier-v1:0',
        "system_prompt": None,
        "state_file": 'titan_g1_premier.json'
    }
}

# Channel configuration
CHANNEL_CONFIG = {
    "chatgpt-channel": "chatgpt",
    "llama3-channel": "llama3",
    "jamba-instruct-channel": "jamba_instruct",
    "mistral-large-channel": "mistral_large",
    "command-r-plus-channel": "command_r_plus",
    "titan-text-premier-channel": "titan_text_premier",
}
