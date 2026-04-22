"""Read library sheets from CatCost Excel for full analysis."""
import os
import sys
import xml.etree.ElementTree as ET
import zipfile

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

XLSX = os.path.join(os.path.dirname(__file__), '..', 'CatCost_v1-1-1', 'CatCost_v1-1-1.xlsx')
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def get_ss(z):
    ss = []
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root:
        texts = [t.text or '' for t in si.iter(f'{{{NS}}}t') if t.text]
        ss.append(''.join(texts))
    return ss


def cell_val(cell, ss):
    t = cell.get('t', '')
    v = cell.find(f'{{{NS}}}v')
    if v is None:
        return ''
    val = v.text or ''
    if t == 's':
        try:
            return ss[int(val)]
        except Exception:
            return val
    return val


def dump_sheet(z, fname, ss, max_rows=200):
    root = ET.fromstring(z.read('xl/worksheets/' + fname))
    sd = root.find(f'{{{NS}}}sheetData')
    if sd is None:
        return
    for i, row in enumerate(sd):
        if i >= max_rows:
            print(f'  ... (truncated at row {max_rows})')
            break
        vals = [cell_val(c, ss) for c in row]
        nonempty = [v for v in vals if v.strip()]
        if nonempty:
            print('  ' + ' | '.join(nonempty[:14]))


with zipfile.ZipFile(XLSX) as z:
    ss = get_ss(z)
    for fname, name, mr in [
        ('sheet12.xml', 'Materials Library', 30),   # first 30 rows to see structure
        ('sheet13.xml', 'Step Library', 60),
        ('sheet14.xml', 'Equip. Library', 30),
        ('sheet15.xml', 'Spent Cat Library', 60),
        ('sheet16.xml', 'UnitConv', 60),
        ('sheet17.xml', 'ChemPPI', 20),
        ('sheet18.xml', 'CEPCI', 20),
    ]:
        print(f'\n\n{"="*70}')
        print(f'  SHEET: {name}')
        print(f'{"="*70}')
        dump_sheet(z, fname, ss, mr)
