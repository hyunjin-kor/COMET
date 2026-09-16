# Manufacturing diagram source

`fig3a_manufacturing_v2.pptx` contains editable English and Korean labels over
the original generated apparatus illustration. The drawing is conceptual and
does not specify a laboratory apparatus or procedure. It contains no numerical results.
The original illustration and generation prompt are in `artwork/`.

Export with Microsoft PowerPoint:

```powershell
scripts/export_note_diagram_slides.ps1 -SourceDirectory docs/paper/diagram-sources-2026-09-15 -Names fig3a_manufacturing_v2
```

Since 16 September 2026 this deck is the retained artwork and label source only:
its labels were transplanted into `../diagram-sources-2026-09-16/fig3_manufacturing.pptx`,
which now holds the complete Figure 3. The export manifest records the source and output
checksums. Numerical panels are drawn by `scripts/draw_application_note_figures.py` from the
separate frozen manufacturing study. Edit the source deck and re-export; do not retouch
generated figure files. AI use must be disclosed in the adjacent caption and
Acknowledgments under ACS policy. This artwork is not a TOC graphic.
