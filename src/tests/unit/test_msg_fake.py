from src.tests.generators.gen_msg_ai import gen_msg_fake, build_prompt

prompt = build_prompt(tipo="misto", quantidade=2)
print(prompt)

msg = gen_msg_fake(tipo="nfse", quantidade=2)
print(msg)