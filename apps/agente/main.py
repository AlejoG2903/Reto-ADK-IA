# Simplemente ejecutar el agente desde agente_clinica
import sys
from agente_clinica.agent import root_agent

if __name__ == "__main__":
    if len(sys.argv) > 1:
        user_message = " ".join(sys.argv[1:])
        response = root_agent.generate_content(user_message)
        print(response.text)
    else:
        print("Por favor, proporciona un mensaje para el agente.")