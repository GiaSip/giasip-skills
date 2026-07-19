#!/usr/bin/env bash
# api-dispatch.sh — API 直调派遣脚本
# 两种 provider 模式：
#   direct     （默认）— 逐厂商直连：DeepSeek/Qwen/GLM/豆包/MiniMax，各自一个 .env + key
#   openrouter — 海外聚合平台，一个 key 调多模型（含 Claude/GPT/Gemini/Kimi 等）
#   siliconflow— 国内聚合平台（硅基流动），一个 key 调 DeepSeek/Qwen/GLM/Kimi/MiniMax
# 用于无 CLI Agent 的模型，通过 OpenAI 兼容 API 直接调用完成纯分析任务
# 比 CLI Agent 快 10 倍——无启动开销，直接发请求收回答
#
# Usage:
#   # 逐厂商直调（默认，向后兼容）
#   api-dispatch.sh --model <qwen|deepseek|glm|doubao|minimax> "prompt"
#
#   # 聚合平台易用路径（一个 key）——设一次 env，全局生效
#   export DISPATCH_PROVIDER=openrouter   # 或 siliconflow
#   api-dispatch.sh --model deepseek "prompt"
#
#   # 单次覆盖 provider
#   api-dispatch.sh --via siliconflow --model kimi "prompt"
#
#   # 逃生口：透传任意聚合平台 model ID（别名表覆盖不到时）
#   api-dispatch.sh --via openrouter --model-id anthropic/claude-sonnet-5 "prompt"
#
#   echo "长文本" | api-dispatch.sh --model <model> --stdin
#
# Provider 解析优先级：--via 标志 > $DISPATCH_PROVIDER env > direct（默认）
#
# Key 文件（放 ~/.config/ai-keys/）：
#   direct:      deepseek.env / dashscope.env / zai.env / volcengine.env / minimax.env
#   openrouter:  openrouter.env   (export OPENROUTER_API_KEY=...)
#   siliconflow: siliconflow.env  (export SILICONFLOW_API_KEY=...)
#
# 安全说明：
#   - 每个 provider 只读取自己白名单内的 key 变量（KEY_ENV_VARS），不会误取环境里其它 provider 的 key。
#   - API key 通过 `curl -K -`（config 走 stdin）传入，不出现在进程 argv。config 里的值都经 cfg_escape 转义，避免注入额外 curl 选项。
#   - 注意：若 .env 用 `export` 导出 key，它仍在进程环境里，同用户可经 `ps e` / /proc/<pid>/environ 看到；不想暴露就在 .env 里去掉 `export`（脚本用 ${!var} 读取，不依赖 export）。
#   - prompt/body 写入仅本人可读（0600）临时文件，退出即删。
#   - `.env` 会被 source（等于执行文件内 shell），务必只指向你自己创建的文件，别 source 来历不明的内容。
#
# Exit: 0 = success (output on stdout), 1 = failed (error on stderr)

set -euo pipefail

MODEL=""
MODEL_ID_OVERRIDE=""
PROVIDER_OVERRIDE=""
PROMPT=""
USE_STDIN=false
TIMEOUT_OVERRIDE=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --model|-m)
      [[ $# -ge 2 ]] || { echo "[api-dispatch] $1 需要一个值" >&2; exit 1; }
      MODEL="$2"; shift 2 ;;
    --model-id)
      [[ $# -ge 2 ]] || { echo "[api-dispatch] $1 需要一个值" >&2; exit 1; }
      MODEL_ID_OVERRIDE="$2"; shift 2 ;;
    --via|--provider)
      [[ $# -ge 2 ]] || { echo "[api-dispatch] $1 需要一个值" >&2; exit 1; }
      PROVIDER_OVERRIDE="$2"; shift 2 ;;
    --timeout|-t)
      [[ $# -ge 2 ]] || { echo "[api-dispatch] $1 需要一个值" >&2; exit 1; }
      TIMEOUT_OVERRIDE="$2"; shift 2 ;;
    --stdin) USE_STDIN=true; shift ;;
    --help|-h)
      cat <<'HELP'
Usage:
  api-dispatch.sh --model <alias> "prompt"
  echo "prompt" | api-dispatch.sh --model <alias> --stdin

Provider (resolve order: --via > $DISPATCH_PROVIDER > direct):
  direct       Per-vendor direct call (default). Aliases: qwen|deepseek|glm|doubao|minimax
  openrouter   Overseas aggregator, one key. Aliases: deepseek|qwen|glm|kimi|minimax|claude|gpt|gemini
  siliconflow  China aggregator (SiliconFlow), one key. Aliases: deepseek|qwen|glm|kimi|minimax

Flags:
  --via <provider>     Override provider for this call (openrouter|siliconflow|direct)
  --model-id <raw>     Pass a raw aggregator model ID verbatim (bypasses the alias table)
  --timeout <sec>      Per-call timeout (default 180)
  --stdin              Read prompt from stdin

Aggregator model IDs go stale — verify on the vendor's models page, or use --model-id.
See references/model-roster.md for the current alias → model-ID tables.
HELP
      exit 0
      ;;
    *) PROMPT="$1"; shift ;;
  esac
done

# Read from stdin if --stdin flag is set
if $USE_STDIN; then
  PROMPT=$(cat)
fi

if [[ -z "$PROMPT" ]]; then
  echo "Usage: api-dispatch.sh --model <alias> \"prompt\"  (see --help)" >&2
  exit 1
fi

TIMEOUT="${TIMEOUT_OVERRIDE:-${API_TIMEOUT:-180}}"
AI_KEYS_DIR="$HOME/.config/ai-keys"

# --- Resolve provider: --via flag > DISPATCH_PROVIDER env > direct ---
PROVIDER="${PROVIDER_OVERRIDE:-${DISPATCH_PROVIDER:-direct}}"

# Per-provider state, all initialised so `set -u` is happy in every branch.
# KEY_ENV_VARS = space-separated whitelist of allowed key variable names for THIS
# provider only — prevents another provider's key (e.g. a globally-exported
# OPENROUTER_API_KEY) from being picked up during a direct call.
EXTRA_HEADER_LINES=()
BASE_URL_ENVVAR=""
BASE_URL_DEFAULT=""
KEY_ENV_VARS=""

case "$PROVIDER" in
  # =========================================================================
  # AGGREGATOR: OpenRouter (overseas) — one key, many vendors incl. Claude/GPT/Gemini
  # =========================================================================
  openrouter)
    KEY_FILE="$AI_KEYS_DIR/openrouter.env"
    KEY_ENV_VARS="OPENROUTER_API_KEY API_KEY"
    BASE_URL_DEFAULT="https://openrouter.ai/api/v1"
    BASE_URL_ENVVAR="OPENROUTER_BASE_URL"
    DISPLAY_NAME="OpenRouter"
    # Optional attribution headers (OpenRouter-recommended, harmless if unset)
    EXTRA_HEADER_LINES+=("HTTP-Referer: ${OPENROUTER_REFERER:-https://github.com/GiaSip/giasip-skills}")
    EXTRA_HEADER_LINES+=("X-Title: ${OPENROUTER_TITLE:-giasip-dispatch}")
    if [[ -n "$MODEL_ID_OVERRIDE" ]]; then
      MODEL_ID="$MODEL_ID_OVERRIDE"
    else
      # alias → OpenRouter model ID (VOLATILE — slugs verified present 2026-07-19; check https://openrouter.ai/models)
      case "$MODEL" in
        deepseek) MODEL_ID="deepseek/deepseek-v3.2" ;;
        deepseek-r1|reasoner) MODEL_ID="deepseek/deepseek-r1" ;;
        qwen)     MODEL_ID="qwen/qwen3.6-plus" ;;
        glm)      MODEL_ID="z-ai/glm-5.2" ;;
        kimi)     MODEL_ID="moonshotai/kimi-k3" ;;
        minimax)  MODEL_ID="minimax/minimax-m3" ;;
        claude)   MODEL_ID="anthropic/claude-sonnet-5" ;;
        gpt)      MODEL_ID="openai/gpt-5.5" ;;
        gemini)   MODEL_ID="google/gemini-3.1-pro-preview" ;;
        *)
          echo "[api-dispatch] OpenRouter 别名表无 '$MODEL'。" >&2
          echo "[api-dispatch] 用 --model-id <raw> 透传，或查 https://openrouter.ai/models" >&2
          exit 1
          ;;
      esac
    fi
    ;;

  # =========================================================================
  # AGGREGATOR: SiliconFlow 硅基流动 (China) — one key, DeepSeek/Qwen/GLM/Kimi/MiniMax
  # Intl users: export SILICONFLOW_BASE_URL=https://api.siliconflow.com/v1
  # =========================================================================
  siliconflow)
    KEY_FILE="$AI_KEYS_DIR/siliconflow.env"
    KEY_ENV_VARS="SILICONFLOW_API_KEY API_KEY"
    BASE_URL_DEFAULT="https://api.siliconflow.cn/v1"
    BASE_URL_ENVVAR="SILICONFLOW_BASE_URL"
    DISPLAY_NAME="SiliconFlow 硅基流动"
    if [[ -n "$MODEL_ID_OVERRIDE" ]]; then
      MODEL_ID="$MODEL_ID_OVERRIDE"
    else
      # alias → SiliconFlow model ID (VOLATILE — live-tested 2026-07-19; check https://siliconflow.cn/models)
      case "$MODEL" in
        deepseek) MODEL_ID="deepseek-ai/DeepSeek-V4-Pro" ;;
        deepseek-r1|reasoner) MODEL_ID="deepseek-ai/DeepSeek-R1" ;;
        qwen)     MODEL_ID="Qwen/Qwen3.6-35B-A3B" ;;
        glm)      MODEL_ID="zai-org/GLM-5.2" ;;
        kimi)     MODEL_ID="Pro/moonshotai/Kimi-K2.6" ;;
        minimax)  MODEL_ID="MiniMaxAI/MiniMax-M2.5" ;;
        *)
          echo "[api-dispatch] SiliconFlow 别名表无 '$MODEL'。" >&2
          echo "[api-dispatch] 用 --model-id <raw> 透传，或查 https://siliconflow.cn/models" >&2
          exit 1
          ;;
      esac
    fi
    ;;

  # =========================================================================
  # DIRECT: per-vendor direct call (default, backward compatible)
  # =========================================================================
  direct)
    if [[ -z "$MODEL" ]]; then
      echo "Usage: api-dispatch.sh --model <qwen|deepseek|glm|doubao|minimax> \"prompt\"" >&2
      exit 1
    fi
    case "$MODEL" in
      qwen|qwen-max|qwen-plus|qwen3.5|qwen3.6)
        KEY_FILE="$AI_KEYS_DIR/dashscope.env"
        KEY_ENV_VARS="DASHSCOPE_API_KEY API_KEY"
        API_URL="https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        MODEL_ID="qwen3.6-plus"
        DISPLAY_NAME="Qwen3.6 Plus (通义千问)"
        ;;
      deepseek|deepseek-r1|deepseek-reasoner|deepseek-v4)
        KEY_FILE="$AI_KEYS_DIR/deepseek.env"
        KEY_ENV_VARS="DEEPSEEK_API_KEY API_KEY"
        API_URL="https://api.deepseek.com/chat/completions"
        MODEL_ID="deepseek-v4-pro"
        DISPLAY_NAME="DeepSeek V4-Pro"
        ;;
      glm|glm-4|glm-4-plus|glm-5|glm-5.1)
        KEY_FILE="$AI_KEYS_DIR/zai.env"
        KEY_ENV_VARS="ZAI_API_KEY ZHIPUAI_API_KEY BIGMODEL_API_KEY API_KEY"
        API_URL="https://open.bigmodel.cn/api/paas/v4/chat/completions"
        MODEL_ID="glm-5.1"
        DISPLAY_NAME="GLM-5.1 (智谱)"
        ;;
      doubao|doubao-pro|seed|volcengine)
        KEY_FILE="$AI_KEYS_DIR/volcengine.env"
        KEY_ENV_VARS="VOLCENGINE_API_KEY VOLC_API_KEY ARK_API_KEY API_KEY"
        API_URL="https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        MODEL_ID="doubao-seed-2-0-pro-260215"
        DISPLAY_NAME="豆包 Seed-2.0 Pro (字节)"
        ;;
      minimax|minimax-m2.7|m2.7)
        KEY_FILE="$AI_KEYS_DIR/minimax.env"
        KEY_ENV_VARS="MINIMAX_API_KEY API_KEY"
        API_URL="https://api.minimax.io/v1/chat/completions"
        MODEL_ID="MiniMax-M2.7"
        DISPLAY_NAME="MiniMax M2.7"
        ;;
      *)
        echo "[api-dispatch] direct 模式不支持的模型: $MODEL" >&2
        echo "[api-dispatch] direct 支持: qwen, deepseek, glm, doubao, minimax" >&2
        echo "[api-dispatch] 或用聚合平台: --via openrouter / --via siliconflow" >&2
        exit 1
        ;;
    esac
    ;;

  *)
    echo "[api-dispatch] 未知 provider: '$PROVIDER'（支持 direct / openrouter / siliconflow）" >&2
    exit 1
    ;;
esac

# --- Load API key ---
if [[ ! -f "$KEY_FILE" ]]; then
  echo "[api-dispatch] Key 文件不存在: $KEY_FILE" >&2
  if [[ "$PROVIDER" == "openrouter" ]]; then
    echo "[api-dispatch] 聚合易用路径：在 $KEY_FILE 写 'export OPENROUTER_API_KEY=...'（一个 key 调多模型，https://openrouter.ai/keys）" >&2
  elif [[ "$PROVIDER" == "siliconflow" ]]; then
    echo "[api-dispatch] 聚合易用路径：在 $KEY_FILE 写 'export SILICONFLOW_API_KEY=...'（一个 key 调多模型，https://siliconflow.cn）" >&2
  fi
  exit 1
fi

# shellcheck source=/dev/null
source "$KEY_FILE"

# Resolve aggregator base URL AFTER sourcing, so a *_BASE_URL defined *inside* the
# .env file (e.g. SILICONFLOW_BASE_URL for the intl endpoint) actually takes effect.
if [[ -n "$BASE_URL_ENVVAR" ]]; then
  base_from_env="${!BASE_URL_ENVVAR:-}"
  API_URL="${base_from_env:-$BASE_URL_DEFAULT}/chat/completions"
fi

# Read the API key ONLY from this provider's whitelisted variable names.
API_KEY=""
for var in $KEY_ENV_VARS; do
  if [[ -n "${!var:-}" ]]; then
    API_KEY="${!var}"
    break
  fi
done

if [[ -z "$API_KEY" ]]; then
  echo "[api-dispatch] 在 $KEY_FILE 中未找到 API key（期望变量之一：${KEY_ENV_VARS}）" >&2
  exit 1
fi

# --- Build request body with python (json.dumps escapes model + prompt safely;
#     never string-concatenate MODEL_ID / PROMPT into JSON) ---
PAYLOAD="$(API_MODEL_ID="$MODEL_ID" API_PROMPT="$PROMPT" python3 -c '
import os, json
print(json.dumps({
    "model": os.environ["API_MODEL_ID"],
    "max_tokens": 8192,
    "messages": [{"role": "user", "content": os.environ["API_PROMPT"]}],
}))' 2>/dev/null || true)"
if [[ -z "$PAYLOAD" ]]; then
  echo "[api-dispatch] JSON 编码失败（需要 python3）" >&2
  exit 1
fi

# --- Temp files (0600, auto-removed) for the request body + curl stderr.
#     Register the cleanup trap BEFORE creating them, so if the second mktemp
#     fails the first file is still removed. ---
BODY_FILE=""
ERR_FILE=""
trap 'rm -f "$BODY_FILE" "$ERR_FILE"' EXIT
BODY_FILE="$(mktemp "${TMPDIR:-/tmp}/apidispatch.XXXXXX")"
ERR_FILE="$(mktemp "${TMPDIR:-/tmp}/apidispatch.XXXXXX")"
chmod 600 "$BODY_FILE" "$ERR_FILE"
printf '%s' "$PAYLOAD" > "$BODY_FILE"

echo "[api-dispatch] 正在调用 $DISPLAY_NAME ($MODEL_ID)..." >&2

# Escape a value for a curl-config double-quoted field: backslash + double-quote,
# and drop CR/LF — so a key / URL / header value can't break out of its quotes
# and inject an extra curl option (e.g. a second url/proxy/output line).
cfg_escape() {
  printf '%s' "$1" | tr -d '\r\n' | sed -e 's/\\/\\\\/g' -e 's/"/\\"/g'
}

# --- Call API. The config (incl. Authorization: Bearer <key>) is fed to curl via
#     stdin (-K -), so the key never appears in argv. ---
emit_curl_config() {
  printf 'url = "%s"\n' "$(cfg_escape "$API_URL")"
  printf 'header = "Content-Type: application/json"\n'
  printf 'header = "Authorization: Bearer %s"\n' "$(cfg_escape "$API_KEY")"
  local h
  for h in "${EXTRA_HEADER_LINES[@]+"${EXTRA_HEADER_LINES[@]}"}"; do
    printf 'header = "%s"\n' "$(cfg_escape "$h")"
  done
  printf 'data-binary = "@%s"\n' "$BODY_FILE"
}

set +e
API_RESPONSE="$(emit_curl_config | curl -sS --max-time "$TIMEOUT" -K - 2>"$ERR_FILE")"
curl_rc=$?
set -e

if [[ $curl_rc -ne 0 ]]; then
  # curl error text (e.g. "curl: (28) Operation timed out") contains no secrets
  echo "[api-dispatch] $DISPLAY_NAME 请求失败 (curl exit $curl_rc): $(head -c 200 "$ERR_FILE")" >&2
  exit 1
fi

if [[ -z "$API_RESPONSE" ]]; then
  echo "[api-dispatch] $DISPLAY_NAME 返回空响应（可能超时或网络错误）" >&2
  exit 1
fi

# --- Check for API error ---
ERROR_MSG=""
if command -v jq &>/dev/null; then
  ERROR_MSG=$(echo "$API_RESPONSE" | jq -r '.error?.message // empty' 2>/dev/null || true)
else
  ERROR_MSG=$(echo "$API_RESPONSE" | python3 -c '
import sys, json
try:
    r = json.load(sys.stdin)
    e = r.get("error", {})
    if e: print(e.get("message", "未知错误"))
except: pass
' 2>/dev/null || true)
fi

if [[ -n "$ERROR_MSG" ]]; then
  echo "[api-dispatch] $DISPLAY_NAME API 错误: $ERROR_MSG" >&2
  if [[ "$PROVIDER" != "direct" ]]; then
    echo "[api-dispatch] 若为 model 不存在，别名表可能已过时——查 models 页或用 --model-id 透传正确 ID" >&2
  fi
  exit 1
fi

# --- Parse response ---
CONTENT=""
REASONING=""

if command -v jq &>/dev/null; then
  CONTENT=$(echo "$API_RESPONSE" | jq -r '.choices[0]?.message?.content // empty' 2>/dev/null || true)
  # DeepSeek R1 includes reasoning_content with full chain-of-thought
  REASONING=$(echo "$API_RESPONSE" | jq -r '.choices[0]?.message?.reasoning_content // empty' 2>/dev/null || true)
else
  CONTENT=$(echo "$API_RESPONSE" | python3 -c '
import sys, json
try:
    r = json.load(sys.stdin)
    c = r["choices"][0]["message"]
    print(c.get("content", ""))
except: pass
' 2>/dev/null || true)
fi

if [[ -n "$CONTENT" ]]; then
  # DeepSeek R1: prepend reasoning process if available
  if [[ -n "${REASONING:-}" && "$REASONING" != "null" && "$REASONING" != "" ]]; then
    echo "<details><summary>🧠 推理过程</summary>"
    echo ""
    printf '%s\n' "$REASONING"
    echo ""
    echo "</details>"
    echo ""
  fi
  printf '%s\n' "$CONTENT"
  exit 0
fi

# Last resort: dump raw response for debugging
echo "[api-dispatch] 无法解析 $DISPLAY_NAME 响应:" >&2
echo "$API_RESPONSE" | head -c 500 >&2
exit 1
