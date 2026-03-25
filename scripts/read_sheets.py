"""Read key sheets from CatCost Excel for analysis."""
import zipfile
import xml.etree.ElementTree as ET
import sys
import os

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

XLSX = os.path.join(os.path.dirname(__file__), '..', 'CatCost_v1-1-1', 'CatCost_v1-1-1.xlsx')
NS = 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'


def get_ss(z):
    ss = []
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root:
        texts = [t.text or '' for t in si.iter('{%s}t' % NS) if t.text]
        ss.append(''.join(texts))
    return ss


def cell_val(cell, ss):
    t = cell.get('t', '')
    v = cell.find('{%s}v' % NS)
    if v is None:
        return ''
    val = v.text or ''
    if t == 's':
        try:
            return ss[int(val)]
        except Exception:
            return val
    return val


def dump_sheet(z, fname, ss, max_rows=80):
    root = ET.fromstring(z.read('xl/worksheets/' + fname))
    sd = root.find('{%s}sheetData' % NS)
    if sd is None:
        return
    for i, row in enumerate(sd):
        if i >= max_rows:
            break
        vals = [cell_val(c, ss) for c in row]
        nonempty = [v for v in vals if v.strip()]
        if nonempty:
            print('  ' + ' | '.join(nonempty[:12]))


with zipfile.ZipFile(XLSX) as z:
    ss = get_ss(z)
    for fname, name, mr in [
        ('sheet2.xml', '1 Inputs', 60),
        ('sheet3.xml', '2 Materials', 60),
        ('sheet4.xml', '3a Step Method', 80),
        ('sheet5.xml', '3b Equip', 50),
        ('sheet6.xml', '3c Utilities', 50),
        ('sheet7.xml', '3d CapEx', 80),
        ('sheet8.xml', '3e OpEx', 80),
        ('sheet9.xml', '4 Spent Catalyst', 80),
        ('sheet10.xml', '5a Summary', 50),
    ]:
        print(f'\n\n{"="*60}')
        print(f'  SHEET: {name}')
        print(f'{"="*60}')
        dump_sheet(z, fname, ss, mr)
