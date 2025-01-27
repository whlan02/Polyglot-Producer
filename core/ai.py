import openai

class AIHelper:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key

    def generate_sentence(self, word, learning_lang):
        prompt = self._create_prompt(word, learning_lang)
        return self._query_openai(prompt)

    def _create_prompt(self, word, learning_lang):
        return f"Please generate 3 common sentences using the word '{word}' in the target language ({learning_lang}). For each sentence, provide a clear translation in the following JSON format:\n\n[\n  {{\n    \"sentence\": \"[Sentence in target language]\",\n    \"translation\": \"[Translation in English]\"\n  }},\n  {{\n    \"sentence\": \"[Sentence in target language]\",\n    \"translation\": \"[Translation in English]\"\n  }},\n  {{\n    \"sentence\": \"[Sentence in target language]\",\n    \"translation\": \"[Translation in English]\"\n  }}\n]"

    def _query_openai(self, prompt):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            if response and 'choices' in response and response.choices:
                message = response.choices[0].message
                if 'content' in message:
                    return message.content.strip()
            return "No valid response from the model."
        except Exception as e:
            print(f"Error: {e}")
            return "An error occurred while processing the request."
