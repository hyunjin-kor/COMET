"""Extract step method templates and CapEx/OpEx factors from CatCost Excel."""
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


def get_all_rows(z, fname, ss, max_rows=500):
    """Return all rows as list of dicts with col letter -> value."""
    root = ET.fromstring(z.read('xl/worksheets/' + fname))
    sd = root.find(f'{{{NS}}}sheetData')
    if sd is None:
        return []
    rows = []
    for i, row in enumerate(sd):
        if i >= max_rows:
            break
        row_dict = {}
        for cell in row:
            ref = cell.get('r', '')
            col = ''.join(c for c in ref if c.isalpha())
            row_dict[col] = cell_val(cell, ss)
        rows.append(row_dict)
    return rows


with zipfile.ZipFile(XLSX) as z:
    ss = get_ss(z)

    # ==== 3a Step Method - all templates ====
    print('\n' + '='*70)
    print('SHEET: 3a Step Method - Full dump')
    print('='*70)
    rows = get_all_rows(z, 'sheet4.xml', ss, max_rows=400)
    for i, row in enumerate(rows):
        nonempty = {k: v for k, v in row.items() if v.strip()}
        if nonempty:
            # Show columns A through J
            vals = []
            for col in 'ABCDEFGHIJ':
                if col in nonempty:
                    vals.append(f'{col}:{nonempty[col][:40]}')
            if vals:
                print(f'  Row{i+1}: ' + '  |  '.join(vals))

    # ==== 3b Equip - template structure ====
    print('\n\n' + '='*70)
    print('SHEET: 3b Equip - Equipment templates (first 200 rows)')
    print('='*70)
    rows = get_all_rows(z, 'sheet5.xml', ss, max_rows=200)
    for i, row in enumerate(rows):
        nonempty = {k: v for k, v in row.items() if v.strip()}
        if nonempty:
            vals = []
            for col in 'ABCDEFGHIJK':
                if col in nonempty:
                    vals.append(f'{col}:{nonempty[col][:35]}')
            if vals:
                print(f'  Row{i+1}: ' + '  |  '.join(vals))
