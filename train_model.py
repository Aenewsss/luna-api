# train_model.py
from transformers import AutoModelForCausalLM, Trainer, TrainingArguments
from datasets import load_from_disk

# Carregar o modelo e o tokenizer
model = AutoModelForCausalLM.from_pretrained("./pretrained_model")

# Carregar o dataset tokenizado
tokenized_dataset = load_from_disk("./tokenized_dataset")

# Configurações de treinamento
training_args = TrainingArguments(
    output_dir="./results",
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=8,
    num_train_epochs=1,
    weight_decay=0.01,
)

# Definir o trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset,
)

# Treinar o modelo
trainer.train()

# Salvar o modelo treinado
model.save_pretrained("./trained_model")