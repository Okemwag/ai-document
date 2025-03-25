from celery import shared_task
from transformers import pipeline

from .models import Document
from .services.document_processor import update_document_status

# Load model only once to improve performance
model_id = "meta-llama/Meta-Llama-3.1-8B-Instruct"

generation_pipeline = pipeline(
    "text-generation",
    model=model_id,
    model_kwargs={"torch_dtype": "auto"},
    device_map="auto"
)

@shared_task(bind=True)
def improve_document(self, document_id):
    """
    Task to paraphrase and improve a document using LLaMA model.
    """
    try:
        document = Document.objects.get(id=document_id)

        input_text = document.original_content

        messages = [
            {"role": "system", "content": "You are an AI assistant that rewrites and improves documents for clarity, style, and grammar."},
            {"role": "user", "content": input_text}
        ]

        outputs = generation_pipeline(
            messages,
            max_new_tokens=512,
        )

        improved_content = outputs[0]['generated_text']

        # Save improved content to the database
        update_document_status(document, status='completed', improved_content=improved_content)

    except Exception as e:
        # Handle failure
        update_document_status(document, status='failed')
        raise e
