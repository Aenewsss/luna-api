import os
from fastapi import FastAPI
from app.classes.classes import MessageRequest
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI(title="luna-api")

# Definir os caminhos para os modelos
trained_model_path = "./trained_model"
pretrained_model_path = "./pretrained_model"


# Função para carregar o modelo e o tokenizer
def load_model_and_tokenizer():
    print("\nline 16")
    if os.path.exists(trained_model_path):
        print("\nline 18")
        model = AutoModelForCausalLM.from_pretrained(trained_model_path)
        tokenizer = AutoTokenizer.from_pretrained(trained_model_path)
    elif os.path.exists(pretrained_model_path):
        print("\nline 22")
        model = AutoModelForCausalLM.from_pretrained(pretrained_model_path)
        tokenizer = AutoTokenizer.from_pretrained(pretrained_model_path)
    else:
        print("\nline 26")
        model_id = "meta-llama/Meta-Llama-3-8B"
        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
        ).cpu()

        from accelerate import disk_offload
        disk_offload(model=model, offload_dir="offload")

        tokenizer = AutoTokenizer.from_pretrained(model_id)

    return model, tokenizer


model, tokenizer = load_model_and_tokenizer()


@app.post("/send-message")
async def chat_llm(request: MessageRequest):

    print("request.message", request.message)

    inputs = tokenizer(request.message, return_tensors="pt")
    outputs = model.generate(inputs["input_ids"], max_length=50, num_return_sequences=1)
    generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

    print("generated_text")

    return {"response": generated_text}


@app.get("/")
async def helloWorld():
    return {"message": "Hello World"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
