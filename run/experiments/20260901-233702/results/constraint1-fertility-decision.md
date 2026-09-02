# CONSTRAINT 1 — tokenizer fertility ratio (alien / 3DOM)

Pre-committed band (reports/CANDIDATE_SELECTION.md): **[0.95, 1.05]** on the FERTILITY RATIO = total tokens / total characters.

Measured with `transformers.AutoTokenizer`, `add_special_tokens=False`, over the 62-item parallel positive corpus.

| tokenizer | metric | identity | alpha | beta | gamma |
|---|---|---:|---:|---:|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | tok/char | 0.3511 | 0.3750 | 0.4918 | 0.6802 |
| | ratio ÷ 3DOM | **1.000** | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-1.5B` | tok/char | 0.3511 | 0.3750 | 0.4918 | 0.6802 |
| | ratio ÷ 3DOM | **1.000** | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-3B` | tok/char | 0.3511 | 0.3750 | 0.4918 | 0.6802 |
| | ratio ÷ 3DOM | **1.000** | **1.068** | **1.401** | **1.937** |
| `Qwen/Qwen2.5-Coder-7B` | tok/char | 0.3511 | 0.3750 | 0.4918 | 0.6802 |
| | ratio ÷ 3DOM | **1.000** | **1.068** | **1.401** | **1.937** |
| `deepseek-ai/DeepSeek-V3` | tok/char | 0.3342 | 0.3587 | 0.4840 | 0.7636 |
| | ratio ÷ 3DOM | **1.000** | **1.073** | **1.448** | **2.285** |

## Verdict per candidate

| candidate | worst ratio across tokenizers | in [0.95, 1.05]? | verdict |
|---|---:|---|---|
| `alpha` | 1.073 | **NO** | **FAIL CONSTRAINT 1** |
| `beta` | 1.448 | **NO** | **FAIL CONSTRAINT 1** |
| `gamma` | 2.285 | **NO** | **FAIL CONSTRAINT 1** |

## Distinct tokenizers, not five

| repo | class | vocab size |
|---|---|---:|
| `Qwen/Qwen2.5-Coder-0.5B` | Qwen2Tokenizer | 151665 |
| `Qwen/Qwen2.5-Coder-1.5B` | Qwen2Tokenizer | 151665 |
| `Qwen/Qwen2.5-Coder-3B` | Qwen2Tokenizer | 151665 |
| `Qwen/Qwen2.5-Coder-7B` | Qwen2Tokenizer | 151665 |
| `deepseek-ai/DeepSeek-V3` | TokenizersBackend | 128815 |

The four Qwen2.5-Coder checkpoints share ONE tokenizer, so the five repos are **2 distinct tokenizers**, not five independent measurements. Reporting them as five would overstate the external validity of the fertility result.
