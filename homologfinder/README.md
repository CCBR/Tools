## HomologFinder

### Background
Human genenames often need to be converted to mouse homologs (and vice versa) for the purposes of GSEA etc. This tool tries to perform this task without querying BioMart which at times can be quite slow. This is achived by:
  1. Download Human/Mouse homologs from http://www.informatics.jax.org/faq/ORTH_dload.shtml. The first column in this file "DB Class Key", which is unique for each set of homologs from human or mouse.
  2. use "create_human_mouse_homolog_table.py" script to create lookup table for each human or mouse gene found in the download file from The Jackson Laboratory. This lookup table has two tab-delimited columns:
    a. Human or Mouse genename
    b. comma separated list of homologs in the other organism

