"""
Example: Batch processing multiple documents.

This example demonstrates how to process multiple documents
in batch and generate a complete dataset programmatically.
"""

# This will be implemented in task 17.2
# For now, this is a placeholder

if __name__ == "__main__":
    print("Batch processing example")
    print("Full implementation coming in task 17.2")
    
    # Future implementation:
    # from easy_dataset import EasyDataset
    # from pathlib import Path
    # 
    # dataset = EasyDataset()
    # dataset.configure_llm({
    #     "provider": "openai",
    #     "api_key": "sk-...",
    #     "model": "gpt-4"
    # })
    # 
    # # Create project
    # project = dataset.create_project(
    #     name="Batch Processing Project",
    #     description="Processing multiple documents"
    # )
    # 
    # # Process all PDF files in a directory
    # docs_dir = Path("./documents")
    # all_chunks = []
    # 
    # for pdf_file in docs_dir.glob("*.pdf"):
    #     print(f"Processing {pdf_file.name}...")
    #     chunks = dataset.process_file(project.id, str(pdf_file))
    #     all_chunks.extend(chunks)
    # 
    # # Generate questions for all chunks
    # print(f"Generating questions for {len(all_chunks)} chunks...")
    # questions = dataset.generate_questions(
    #     project.id,
    #     [c.id for c in all_chunks],
    #     batch_size=10
    # )
    # 
    # # Generate answers
    # print(f"Generating answers for {len(questions)} questions...")
    # answers = dataset.generate_answers(
    #     project.id,
    #     [q.id for q in questions],
    #     batch_size=10
    # )
    # 
    # # Export to multiple formats
    # dataset.export_dataset(project.id, format="json", output_path="dataset.json")
    # dataset.export_dataset(project.id, format="jsonl", output_path="dataset.jsonl")
    # dataset.export_dataset(project.id, format="csv", output_path="dataset.csv")
    # 
    # print("Batch processing complete!")
