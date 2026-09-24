# Exercise 1: Reading a specimen — GPT-2 XL vs. Mistral 7B

Done: 2026-09-24
Specimens: [`gpt2-xl`](../../data/models/gpt2-xl.json) (OpenAI, Nov. 2019) and
[`mistral-7b-v0-1`](../../data/models/mistral-7b-v0-1.json) (Mistral AI, Sept. 2023)

A model's `config.json` is its collation formula: a short list of numbers
and names that fixes the model's physical shape. It says nothing about what the
model learned, only how it is built. The two specimens below are four years
apart and on opposite sides of the LLaMA recipe.

Every value is cited to a source in the list at the bottom. "Config" means
the model's `config.json` on Hugging Face, pinned to a commit. "Code" means
the source code that actually builds the model, used where the config
names a setting without saying what it does.

## The table

| Character | Config field (GPT-2 / Mistral) | GPT-2 XL | Mistral 7B |
|---|---|---|---|
| Parameters | — | 1542M [2] | 7.3B [8] |
| Layers | `n_layer` / `num_hidden_layers` | 48 [1] | 32 [5][6] |
| Hidden size | `n_embd` / `hidden_size` | 1600 [1] | 4096 [5][6] |
| Attention heads | `n_head` / `num_attention_heads` | 25 [1] | 32 [5][6] |
| Width per head | (derived: hidden ÷ heads) | 64 [4] | 128 [6] |
| Key/value heads | — / `num_key_value_heads` | 25: one per head, no field [4] | 8 [5][6] |
| Feed-forward width | `n_inner` / `intermediate_size` | 6400 (field is `null`; code defaults to 4 × hidden) [1][4] | 14336 [5][6] |
| Vocabulary | `vocab_size` | 50,257 [1][2] | 32,000 [5][6] |
| Context length | `n_positions` / `max_position_embeddings` | 1024 [1][2] | 8192 per paper [6]; config says 32768 [5] |
| Attention window | — / `sliding_window` | none: every token sees all earlier ones | 4096 [5][6] |
| Positional encoding | `n_positions` / `rope_theta` | learned absolute [3][4] | rotary (RoPE) [7] |
| Normalization | `layer_norm_epsilon` / `rms_norm_eps` | LayerNorm, before each sub-block [2][4] | RMSNorm, before each sub-block [7] |
| Activation | `activation_function` / `hidden_act` | GELU (tanh approximation, `gelu_new`) [1][3][9] | SiLU inside a gated unit (SwiGLU) [5][7] |

## Each row in one sentence

- **Parameters.** The total count of learned numbers (weights) in the model; Mistral has about five times as many.
- **Layers.** How many identical blocks the text passes through in sequence, each one revising every token's representation.
- **Hidden size.** How many numbers represent each token inside the model; it is the width of the "lane" every layer reads from and writes to.
- **Attention heads.** How many independent lookups each layer runs, each deciding which earlier tokens matter to the current one; the heads divide the hidden size between them.
- **Width per head.** The hidden size divided by the head count: GPT-2 XL runs more, narrower lookups (25 × 64); Mistral runs fewer, wider ones (32 × 128).
- **Key/value heads.** In GPT-2 each head keeps its own record of every earlier token; in Mistral, groups of four heads share one record (grouped-query attention), which cuts the memory needed while generating.
- **Feed-forward width.** After attention, each token passes through a small network of its own, and this is that network's inner width; most of a model's parameters sit here.
- **Vocabulary.** How many distinct pieces of text (tokens) the model can read and write; it is fixed by the tokenizer, not learned during training.
- **Context length.** How many tokens the model can take in at once.
- **Attention window.** Mistral lets each token look back only 4,096 tokens per layer, but because layers stack, information can travel further than that indirectly.
- **Positional encoding.** GPT-2 learns a separate vector for each of its 1,024 positions and adds it to the token, so it has no vector for position 1,025; Mistral instead rotates each query and key by an angle set by its position, so attention registers how far apart two tokens are, with no fixed table.
- **Normalization.** Both models rescale each token's numbers before every attention and feed-forward step to keep them stable; LayerNorm also shifts them to average zero, and RMSNorm skips that shift and only rescales.
- **Activation.** The curve that makes the network more than a stack of multiplications: GPT-2 applies GELU to one projection, while Mistral computes two projections and uses SiLU of one to gate the other, which is why its feed-forward block has three weight matrices where GPT-2's has two.

## Things the exercise turned up

1. **A config field is not a design fact.** Mistral's paper gives a context
   length of 8192 [6]. Its config's `max_position_embeddings` is 32768 [5].
   The config number is an upper limit the loading code allows, not the length
   the model was described with. The record now stores 8192, with the config
   value in a note.
2. **The paper doesn't describe the whole model.** Mistral's paper says it
   is "based on a transformer architecture" and that "Compared to Llama, it
   introduces a few changes" [6]. It never names its normalization,
   activation or positional encoding. Those three rows come from Mistral's
   own reference code, committed on release day [7], not from the paper.
3. **The config names things without defining them.** `layer_norm_epsilon`
   and `rms_norm_eps` only *imply* which normalization is used; `n_inner:
   null` means "use the code's default." Where the config was silent, the
   table cites the code.
4. **Session 1 cited GPT-2's position method to the wrong paper.** The GPT-2
   paper never says its position embeddings are learned. It says the model
   "largely follows the details of the OpenAI GPT model" [2], and it is the
   GPT-1 paper that says "We used learned position embeddings instead of the
   sinusoidal version" [3]. The `gpt2-xl` record now cites GPT-1 and the code.
5. **Shared characters, no lineage edge.** Mistral's paper describes its
   design as changes from Llama, and RMSNorm, SwiGLU and RoPE all appear in
   the LLaMA 1 record. But no weights passed from LLaMA to Mistral, and
   Stemma records no edge between them. This is the split between
   classification and lineage that `docs/method.md` keeps separate.

## My notes

(Wilson writes this section)

## Questions I still have

## Records added or verified in Stemma

- `gpt2-xl`: positional-encoding source corrected (GPT-1 paper + code); normalization, activation, feed-forward width added.
- `mistral-7b-v0-1`: context length corrected 32768 → 8192 (paper), config value kept in a note; normalization, activation, feed-forward width added from the reference code.
- `zephyr-7b-beta`: note added that its 32768 context comes from the config, not a stated design value.

## Sources

1. GPT-2 XL `config.json`, commit `15ea56d`: https://huggingface.co/openai-community/gpt2-xl/raw/15ea56dee5df4983c59b2538573817e1667135e2/config.json
2. Radford et al. (2019), "Language Models are Unsupervised Multitask Learners," sec. 2.3 and Table 2: https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf
3. Radford et al. (2018), "Improving Language Understanding by Generative Pre-Training," sec. 4.1 (GELU, learned position embeddings): https://cdn.openai.com/research-covers/language-unsupervised/language_understanding_paper.pdf
4. Hugging Face `transformers` v4.34.0, `modeling_gpt2.py` (LayerNorm `ln_1`/`ln_2`, learned `wpe` position table, feed-forward default 4 × hidden, one K and V per head): https://github.com/huggingface/transformers/blob/v4.34.0/src/transformers/models/gpt2/modeling_gpt2.py
5. Mistral 7B v0.1 `config.json`, commit `27d67f1`: https://huggingface.co/mistralai/Mistral-7B-v0.1/raw/27d67f1b5f57dc0953326b2601d68371d40ea8da/config.json
6. Jiang et al. (2023), "Mistral 7B," sec. 2 and Table 1: https://arxiv.org/abs/2310.06825
7. Mistral AI reference implementation, `one_file_ref.py`, first commit (2023-09-27): RMSNorm (L176, L197–198), gated SiLU feed-forward (L152–173), rotary embeddings (L47–57, L210): https://github.com/mistralai/mistral-src/blob/c18d5b9166ffa16ce58827346ed56a28d2876e7e/one_file_ref.py
8. Mistral AI, "Mistral 7B" (release post, 2023-09-27): https://mistral.ai/news/announcing-mistral-7b
9. Hugging Face `transformers` v4.34.0, `activations.py` (`gelu_new` = tanh approximation of GELU): https://github.com/huggingface/transformers/blob/v4.34.0/src/transformers/activations.py
