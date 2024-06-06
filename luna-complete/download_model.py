from transformers import AutoModelForCausalLM, AutoTokenizer
from accelerate import disk_offload
import torch
import logging

# Ativar logging detalhado
logging.basicConfig(level=logging.DEBUG)
import transformers
transformers.logging.set_verbosity_debug()

model_id = "meta-llama/Meta-Llama-3-8B"

print('here 7')
# Baixar o modelo e o tokenizer
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16,
    low_cpu_mem_usage=True,
).cpu()

print('here 15')
disk_offload(model=model, offload_dir="offload")
print('here 17')
tokenizer = AutoTokenizer.from_pretrained(model_id)

print('here 12')
# Salvar o modelo e o tokenizer
model.save_pretrained("./pretrained_model")
tokenizer.save_pretrained("./pretrained_model")