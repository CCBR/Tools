## HomologFinder

### Background
Human genenames often need to be converted to mouse homologs (and vice versa) for the purposes of GSEA etc. This tool tries to perform this task without querying BioMart which at times can be quite slow. This is achived by:
  1. Download Human/Mouse homologs from http://www.informatics.jax.org/faq/ORTH_dload.shtml. The first column in this file "DB Class Key", which is unique for each set of homologs from human or mouse.
  2. use "create_human_mouse_homolog_table.py" script to create lookup table for each human or mouse gene found in the download file from The Jackson Laboratory. This lookup table has two tab-delimited columns:
		1. Human or Mouse genename
		2. comma separated list of homologs in the other organism

**HomologFinder** will read the file created in step 2. and give a list of homologs of the opposite organism, ie. convert
  1. Human --> Mouse OR
  2. Mouse --> Human

**HomologFinder** will take either
  1. single gene name
  2. comma separated list of genes as a genelist
  3. genelist file with 1 gene name per line
