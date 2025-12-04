"""
Example: Integrating Easy Dataset with a custom frontend framework.

This example shows how to integrate Easy Dataset with Flask,
but the same approach works with Django or any other framework.
"""

# This will be implemented in task 17.2
# For now, this is a placeholder

if __name__ == "__main__":
    print("Custom frontend integration example")
    print("Full implementation coming in task 17.2")
    
    # Future implementation:
    # from flask import Flask, jsonify, request
    # from easy_dataset import EasyDataset
    # 
    # app = Flask(__name__)
    # dataset = EasyDataset()
    # 
    # @app.route('/api/projects', methods=['POST'])
    # def create_project():
    #     data = request.json
    #     project = dataset.create_project(**data)
    #     return jsonify(project.to_dict())
    # 
    # @app.route('/api/projects/<project_id>', methods=['GET'])
    # def get_project(project_id):
    #     project = dataset.get_project(project_id)
    #     return jsonify(project.to_dict())
    # 
    # if __name__ == '__main__':
    #     app.run(debug=True)
