#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
import os

def check_and_add_header(filepath, header_text, presence_check_string):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if presence_check_string in content:
            print(f"{filepath} (OK)")
        else:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(header_text + content)
            print(f"{filepath} (ADDED)")
    except Exception as e:
        print(f"Erro ao processar o arquivo {filepath}: {e}")

def main():
    target_directory = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Processando arquivos .py em: {target_directory}")

    header_to_add = """#  SPDX-FileCopyrightText: Copyright © 2024 Lunarbase (https://lunarbase.ai/) <contact@lunarbase.ai>
#  #
#  SPDX-License-Identifier: GPL-3.0-or-later
"""
    string_to_check_for_presence = "SPDX-FileCopyrightText"

    found_py_files = False
    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith(".py"):
                # Ignora o próprio script se ele estiver no diretório alvo
                script_name = os.path.basename(__file__)
                if file == script_name and root == target_directory:
                    print(f"Ignorando o próprio script: {os.path.join(root, file)}")
                    continue
                
                found_py_files = True
                filepath = os.path.join(root, file)
                check_and_add_header(filepath, header_to_add, string_to_check_for_presence)

    if not found_py_files:
        print(f"Nenhum arquivo .py encontrado em {target_directory} (exceto possivelmente o próprio script).")

if __name__ == "__main__":
    main()