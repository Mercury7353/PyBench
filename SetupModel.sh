python -m vllm.entrypoints.openai.api_server \
  --model <your model path> \
  --chat-template <your jinja template file path> \
  --dtype auto \
  --api-key token-abc123 \
  --port 8001 \
  --trust-remote-code \


