#!/usr/bin/env Rscript
# This script is used to lookup the gene_name for a column of gene_ids and
# add the gene_names as an extra column to the output.
# Example use case: RSEM outputs do not have gene_name but only gene_id. 
# This script can then be used to add the gene_name column to the count matrix
# gene_id to gene_name lookup is created on the fly from a user provided GTF.
#
# Eg:
#
# Rscript add_gene_name_to_count_matrix.R \
#  -r rsem.raw_counts_matrix.tsv.tmp \
#  -g /data/RBL_NCI/Wolin/mESC_slam_analysis/resources/mm10/mm10_plus_45S_plus_5S.v2.genes.gtf \
#  -o rsem.raw_counts_matrix.tsv
#
suppressPackageStartupMessages(library("argparse"))

# create parser object
parser <- ArgumentParser()

# specify our desired options 
# by default ArgumentParser will add an help option 

parser$add_argument("-r", "--rawcountsmatrix", 
                    type="character", 
                    help="file with raw counts matrix with gene_id column",
                    required=TRUE)
parser$add_argument("-g", "--gtf", 
                    type="character", 
                    help="GTF file with gene_name and gene_id",
                    required=TRUE)
parser$add_argument("-o","--outfile", 
                    type="character",
                    help="count matrix with gene_name column included",
                    required=TRUE)


args <- parser$parse_args()

library("rtracklayer")
library("tidyverse")
gtf2<-rtracklayer::import(args$gtf)
gtf2<-as.data.frame(gtf2)
unique(data.frame(gene_id=gtf2$gene_id,gene_name=gtf2$gene_name)) %>% drop_na() -> lookuptable

in_df=read.csv(args$rawcountsmatrix,sep="\t",header=TRUE,check.names=FALSE)

out_df=merge(in_df,lookuptable,by=c("gene_id"))

write.table(out_df,file=args$outfile,sep="\t",quote=FALSE,row.names=FALSE,col.names=TRUE)
