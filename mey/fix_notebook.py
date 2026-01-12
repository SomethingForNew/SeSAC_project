import json
import os

notebook_path = 'mm.ipynb'

with open(notebook_path, 'r', encoding='utf-8') as f:
    nb = json.load(f)

for cell in nb['cells']:
    if cell['cell_type'] == 'code':
        # Join lines to search efficiently
        source_str = "".join(cell['source'])
        
        # Identify the specific block we want to replace
        target_snippet = "data = res.json().get('tbLnOpendataRtmsV', {})"
        
        if target_snippet in source_str and "requests.get(url)" in source_str:
            print("Found target cell.")
            
            # We will reconstruct the source lines for this block
            new_lines = []
            skip_next = False
            
            original_lines = cell['source']
            for i, line in enumerate(original_lines):
                # Check for the block start
                if 'res = requests.get(url)' in line:
                    # We found the start of the request block. 
                    # We will rewrite this entire section logically.
                    
                    # Add our new robust code
                    indent = "            " # 12 spaces
                    new_code = [
                        f"{indent}res = requests.get(url)\n",
                        f"{indent}if res.status_code != 200:\n",
                        f"{indent}    print(f'요청 실패: {{res.status_code}} {{year}} {{gu_nm}}')\n",
                        f"{indent}    print(res.text[:200])\n",
                        f"{indent}    break\n",
                        "\n",
                        f"{indent}try:\n",
                        f"{indent}    data = res.json().get('tbLnOpendataRtmsV', {{}})\n",
                        f"{indent}    rows = data.get('row', [])\n",
                        f"{indent}except ValueError as e:\n",
                        f"{indent}    print(f'JSON 파싱 실패 ({{year}} {{gu_nm}}): {{e}}')\n",
                        f"{indent}    print(f'응답 내용: {{res.text[:300]}}')\n",
                        f"{indent}    break\n"
                    ]
                    new_lines.extend(new_code)
                    
                    # Now we need to skip the old lines that we just replaced
                    # The old lines end after 'rows = data.get('row', [])' 
                    # We need to look ahead to find where to resume
                    # We'll just set a flag to skip lines until we see the check 'if not rows:' or similar
                    skip_next = True
                    continue
                
                if skip_next:
                    if 'if not rows:' in line:
                        skip_next = False
                        new_lines.append(line) # Add this line back
                    continue
                
                new_lines.append(line)
            
            cell['source'] = new_lines
            print("Patched the cell.")
            break

with open(notebook_path, 'w', encoding='utf-8') as f:
    json.dump(nb, f, indent=1, ensure_ascii=False)
    print("Notebook saved.")
