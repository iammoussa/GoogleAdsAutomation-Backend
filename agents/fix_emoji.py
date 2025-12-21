#!/usr/bin/env python3
"""
Script per correggere le emoji corrotte in analyzer.py
"""

# Leggi il file
with open('analyzer.py', 'r', encoding='utf-8', errors='replace') as f:
    lines = f.readlines()

# Correzioni specifiche per numero di riga
line_fixes = {
    303: '        ========================================\n',
    381: '        logger.info(f"🔍 Inizio analisi campagna {campaign_id}")\n',
    572: '        logger.info("🔍 Analisi tutte le campagne con alert...")\n',
    586: '        logger.info(f"📊 Trovate {len(campaign_ids)} campagne da analizzare")\n',
    621: '            print(f"📊 ANALISI COMPLETATA - {len(results)} campagne")\n',
    646: '            print(f"📊 ANALISI CAMPAGNA {result[\'campaign_id\']}")\n',
}

# Applica le correzioni
for line_num, new_line in line_fixes.items():
    if line_num <= len(lines):
        old_line = lines[line_num - 1]
        lines[line_num - 1] = new_line
        print(f"✅ Riga {line_num} corretta")
        print(f"   Era:  {old_line.strip()[:60]}")
        print(f"   Ora:  {new_line.strip()[:60]}")
        print()

# Salva il file
with open('analyzer.py', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ File analyzer.py corretto e salvato!")
print("\n🧪 Verifica finale...")

# Verifica
with open('analyzer.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Cerca caratteri corrotti
suspicious = []
for i, line in enumerate(content.split('\n'), 1):
    if any(char in line for char in ['Ã', 'â', 'ð']):
        suspicious.append((i, line.strip()[:80]))

if suspicious:
    print(f"\n⚠️  Trovate ancora {len(suspicious)} righe sospette:")
    for line_num, line_text in suspicious[:5]:
        print(f"   Riga {line_num}: {line_text}")
else:
    print("\n✅ PERFETTO! Nessun carattere corrotto rimanente!")
    
    # Conta emoji corrette
    good_emojis = ['✅', '❌', '🔍', '📊', '🤖', '🎯', '⚠️', '➤', '📝', '📄', '🔄', '✂️', '€']
    total = sum(content.count(emoji) for emoji in good_emojis)
    print(f"   📊 Totale emoji corrette: {total}")
