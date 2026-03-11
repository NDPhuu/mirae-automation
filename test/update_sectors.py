import pandas as pd
import re

df = pd.read_csv('d:/WORKS/Project/mirae-automation/data_sectors.csv')
sectors = {}

for idx, row in df.iterrows():
    sym = str(row['Symbol']).strip()
    ind = str(row['Industry']).strip()
    
    if pd.isna(row['Symbol']) or not sym or sym.lower() == 'nan' or sym == 'Dữ liệu được cung cấp bởi FiinTrade' or 'http' in sym:
        continue
    
    if ind == 'nan' or not ind:
        ind = 'Khác'
        
    if ind not in sectors:
        sectors[ind] = []
        
    if sym not in sectors[ind]:
        sectors[ind].append(sym)

# Count total elements
total_stocks = sum(len(v) for v in sectors.values())
print(f"Total valid stocks parsed from CSV: {total_stocks}")

# Define string replacement
sector_str = 'SECTOR_MAPPING = {\n'
for ind, syms in sectors.items():
    formatted_syms = str(syms).replace("'", '"')
    sector_str += f'    "{ind}": {formatted_syms},\n'
sector_str += '}'

filepath = 'd:/WORKS/Project/mirae-automation/src/config.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace existing using regex
pattern = re.compile(r'SECTOR_MAPPING = \{.*?\n\}', re.DOTALL)
new_content = re.sub(pattern, sector_str, content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Successfully replaced SECTOR_MAPPING in src/config.py")
