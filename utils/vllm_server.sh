set -x
MODEL_DIR="/mnt/data/user/tc_agi/panyinxu/models/Qwen1.5-32B-Chat"
PORT=8000
python -m vllm.entrypoints.openai.api_server \
    --model ${MODEL_DIR} \
    --chat-template chatml.jinja \
    --dtype auto \
    --api-key token-abc123 \
    --tensor-parallel-size 2 \
    --port ${PORT}