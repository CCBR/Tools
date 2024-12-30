"""
Quarto HTML format with FNL branding guidelines

First run `ccbr_tools quarto-add fnl`, then modify the `_quarto.yml` file with the following:

```yaml
website:
  ...
  page-footer:
    background: black
    foreground: white
    left: |
      [![](/_extensions/fnl/fnl-logo-dark.png){height=70px}](https://frederick.cancer.gov/research/science-areas/bioinformatics-and-computational-science/advanced-biomedical-computational-science)
    center: |
      Created by the
      [CCR Collaborative Bioinformatics Resource](https://github.com/CCBR)

format: fnl-html
```
"""
