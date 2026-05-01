# Red Button Test — Cost & Reasoning Report

Total test cost: **$1.0363**  
Total judge cost: **$0.7411**  
Grand total: **$1.7774**  
Total input tokens: **50,079**  
Total output tokens: **244,956**  
Total reasoning tokens: **135,553**  

## Per-model breakdown

| Model | Provider | Calls | Input tok | Output tok | Reasoning tok | Test cost | Avg/call |
|---|---|---:|---:|---:|---:|---:|---:|
| Qwen3.5 397B A17B | tokenfactory | 40 | 1,560 | 57,546 | 0 | $0.2081 | $0.0052 |
| Claude Opus 4.7 (max) | openrouter | 40 | 1,840 | 5,220 | 0 | $0.1397 | $0.0035 |
| Gemini 3.1 Pro Preview | openrouter | 40 | 520 | 8,618 | 8,133 | $0.1045 | $0.0026 |
| Qwen3.6 Max Preview | openrouter | 40 | 1,560 | 15,126 | 13,713 | $0.0960 | $0.0024 |
| Kimi K2.6 | openrouter | 40 | 1,390 | 21,054 | 23,457 | $0.0745 | $0.0019 |
| GPT-5.5 (xhigh) | openrouter | 40 | 1,320 | 1,958 | 1,140 | $0.0653 | $0.0016 |
| Claude Sonnet 4.6 (max) | openrouter | 40 | 1,500 | 3,918 | 1,110 | $0.0633 | $0.0016 |
| GLM-5.1 | openrouter | 40 | 1,240 | 15,498 | 14,478 | $0.0555 | $0.0014 |
| GPT-5.4 (xhigh) | openrouter | 40 | 1,320 | 3,165 | 2,291 | $0.0508 | $0.0013 |
| Grok 4.3 | openrouter | 40 | 3,020 | 14,880 | 14,512 | $0.0410 | $0.0010 |
| MiMo-V2.5-Pro | openrouter | 40 | 11,120 | 7,585 | 2,871 | $0.0339 | $0.0008 |
| Claude Haiku 4.5 | openrouter | 40 | 1,500 | 5,441 | 0 | $0.0287 | $0.0007 |
| MiniMax-M2.7 | openrouter | 40 | 1,293 | 14,908 | 16,680 | $0.0183 | $0.0005 |
| GPT-5.4 mini (xhigh) | openrouter | 40 | 1,320 | 3,334 | 2,244 | $0.0160 | $0.0004 |
| Nemotron 3 Super | tokenfactory | 40 | 1,840 | 11,467 | 0 | $0.0109 | $0.0003 |
| DeepSeek V4 Pro (Max) | openrouter | 40 | 1,339 | 9,246 | 7,691 | $0.0086 | $0.0002 |
| gpt-oss-120B (high) | tokenfactory | 40 | 3,680 | 6,394 | 0 | $0.0044 | $0.0001 |
| Solar Pro 3 | openrouter | 40 | 3,940 | 5,771 | 0 | $0.0041 | $0.0001 |
| DeepSeek V4 Flash (Max) | openrouter | 40 | 1,260 | 11,552 | 10,751 | $0.0034 | $0.0001 |
| Gemini 3 Flash | openrouter | 40 | 1,041 | 958 | 0 | $0.0034 | $0.0001 |
| gpt-oss-20B (high) | openrouter | 40 | 1,856 | 15,429 | 16,482 | $0.0022 | $0.0001 |
| DeepSeek V3.2 | tokenfactory | 40 | 1,260 | 3,271 | 0 | $0.0018 | $0.0000 |
| Mistral Small 4 | openrouter | 40 | 1,800 | 2,082 | 0 | $0.0015 | $0.0000 |
| Gemma 4 31B | openrouter | 40 | 1,560 | 535 | 0 | $0.0004 | $0.0000 |

## Reasoning tokens — default vs reasoning_off

Models with non-zero reasoning in either column are reasoning-capable. If reasoning_off has near-zero, the disable signal worked.

| Model | default avg rt | reasoning_off avg rt | default avg cost | reasoning_off avg cost |
|---|---:|---:|---:|---:|
| Kimi K2.6 | 1173 | 0 | $0.0035 | $0.0002 |
| MiniMax-M2.7 | 834 | 0 | $0.0009 | $0.0000 |
| gpt-oss-20B (high) | 824 | 0 | $0.0001 | $0.0000 |
| Grok 4.3 | 726 | 0 | $0.0020 | $0.0000 |
| GLM-5.1 | 724 | 0 | $0.0026 | $0.0002 |
| Qwen3.6 Max Preview | 686 | 0 | $0.0046 | $0.0002 |
| DeepSeek V4 Flash (Max) | 538 | 0 | $0.0002 | $0.0000 |
| Gemini 3.1 Pro Preview | 407 | 0 | $0.0052 | $0.0000 |
| DeepSeek V4 Pro (Max) | 252 | 132 | $0.0003 | $0.0002 |
| MiMo-V2.5-Pro | 144 | 0 | $0.0011 | $0.0006 |
| GPT-5.4 (xhigh) | 115 | 0 | $0.0021 | $0.0004 |
| GPT-5.4 mini (xhigh) | 112 | 0 | $0.0006 | $0.0002 |
| GPT-5.5 (xhigh) | 57 | 0 | $0.0025 | $0.0008 |
| Claude Sonnet 4.6 (max) | 56 | 0 | $0.0020 | $0.0012 |
| gpt-oss-120B (high) | 0 | 0 | $0.0002 | $0.0001 |
| Claude Opus 4.7 (max) | 0 | 0 | $0.0028 | $0.0042 |
| Claude Haiku 4.5 | 0 | 0 | $0.0007 | $0.0007 |
| Gemini 3 Flash | 0 | 0 | $0.0001 | $0.0001 |
| Gemma 4 31B | 0 | 0 | $0.0000 | $0.0000 |
| DeepSeek V3.2 | 0 | 0 | $0.0000 | $0.0000 |
| Qwen3.5 397B A17B | 0 | 0 | $0.0102 | $0.0002 |
| Nemotron 3 Super | 0 | 0 | $0.0004 | $0.0002 |
| Mistral Small 4 | 0 | 0 | $0.0000 | $0.0000 |
| Solar Pro 3 | 0 | 0 | $0.0001 | $0.0001 |