"""
Example: Using Easy Dataset as a library in your own Python application.

This example demonstrates how to use Easy Dataset programmatically
without running a web server.
"""

# This will be implemented in task 17.2
# For now, this is a placeholder

if __name__ == "__main__":
    print("Embedded usage example")
    print("Full implementation coming in task 17.2")
    
    # Future implementation:
    # from easy_dataset import EasyDataset
    # 
    # # Initialize
    # dataset = EasyDataset(database_url="sqlite:///my_dataset.db")
    # 
    # # Configure LLM
    # dataset.configure_llm({
    #     "provider": "openai",
    #     "api_key": "sk-...",
    #     "model": "gpt-4"
    # })
    # 
    # # Create project
    # project = dataset.create_project(
    #     name="My Project",
    #     description="Dataset for fine-tuning"
    # )
    # 
    # # Process file
    # chunks = dataset.process_file(project.id, "document.pdf")
    # 
    # # Generate questions and answers
    # questions = dataset.generate_questions(project.id, [c.id for c in chunks])
    # answers = dataset.generate_answers(project.id, [q.id for q in questions])
    # 
    # # Export dataset
    # dataset.export_dataset(project.id, format="json", output_path="dataset.json")
