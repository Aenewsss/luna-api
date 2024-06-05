from transformers import AutoTokenizer
from datasets import Dataset

tokenizer = AutoTokenizer.from_pretrained("./pretrained_model")

data = {
    "text": ["Exemplo de frase 1", "Exemplo de frase 2", "Exemplo de frase 3"]
}

dataset = Dataset.from_dict(data)

# Tokenizar os dados
def tokenize_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

tokenized_dataset = dataset.map(tokenize_function, batched=True)

# Salvar dataset tokenizado
tokenized_dataset.save_to_disk("./tokenized_dataset")