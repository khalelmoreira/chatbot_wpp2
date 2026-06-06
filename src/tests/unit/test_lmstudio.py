from openai import OpenAI

client = OpenAI(api_key="lm-studio", base_url="http://localhost:1234/v1")

ai_system = "Você é um extrator de dados fiscais. Extraia os seguintes dados: Cpf, email e telefone."

prompt = "cpf: 06648889952, email: khalel@khalel.com, telefone: 5522999663205"

response = client.chat.completions.create(
    model="google/gemma-4-e4b",
    messages=[
        {"role": "system", "content": ai_system},
        
        {"role": "user", "content": prompt}
    ],
    temperature=0
)

print(response.choices[0].message.reasoning_content)
print(response.choices[0].message.content)