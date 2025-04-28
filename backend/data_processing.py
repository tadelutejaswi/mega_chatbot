import csv

class DataProcessor:
    def __init__(self, knowledge_file):
        self.knowledge_file = knowledge_file
    
    def get_knowledge_base(self):
        knowledge_base = []
        try:
            with open(self.knowledge_file, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    knowledge_base.append(row)
        except FileNotFoundError:
            print(f"Error: The file {self.knowledge_file} was not found.")
        except Exception as e:
            print(f"Error reading knowledge base: {e}")
        return knowledge_base