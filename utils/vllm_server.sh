set -x
MODEL_DIR="<fill ind >"
python -m vllm.entrypoints.openai.api_server \
    --model ${MODEL_DIR} \
    --chat-template chatml.jinja \
    --dtype auto \
    --api-key token-abc123 \
    --tensor-parallel-size 2 \
    --port ${PORT}