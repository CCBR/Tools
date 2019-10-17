#Author: Vishal Koparde, PhD
#Take reformatted DEG out file from RNASeq contrast and the geneinfo.bed to make a Karyoplot with
#updregulated genes in red and downregulated genes in blue

library("argparse")

parser <- ArgumentParser()
parser$add_argument("-d", "--degout", type="character", required=TRUE,
                    help="Reformmated DEG out file from limma/edgeR/DESeq2")
parser$add_argument("-c", "--gene2coord", type="character", required=TRUE,
                    help="Gene to coordinate file ie geneinfo.bed")
parser$add_argument("-g", "--genome", type="character", required=TRUE,
                    help="Genome .. either hg19/hg38/mm9/mm10/Mmul8.0.1/canFam3")
parser$add_argument("-f", "--fdr", type="double", default=0.05,
                    help="FDR cutoff to use")
args <- parser$parse_args()

# setwd("/Users/kopardevn/Documents/Work/Projects/ccbr983/fastq2/GI_Skin_compares")
# args$degout="DESeq2_DEG_Skin_T-Skin_N_all_genes.txt"
# args$gene2coord="geneinfo.bed"
# args$fdr=0.05
# args$genome="hg19"


for (f in c(args$degout,args$gene2coord))
if (! file.exists(f)) {
  stop(paste("File does not exist:",f))
}

if (! args$genome %in% c("hg19","hg38","mm9","mm10","Mmul8.0.1","canFam3")) {
  stop("Only hg19/hg38/mm9/mm10/Mmul8.0.1/canFam3 genomes are supported!")
}


library("karyoploteR")
library("BSgenome.Mmusculus.UCSC.mm9")
library("BSgenome.Mmusculus.UCSC.mm10")
library("BSgenome.Hsapiens.UCSC.hg19")
library("BSgenome.Hsapiens.UCSC.hg38")
library("BSgenome.Mmulatta.UCSC.rheMac8")
library("BSgenome.Cfamiliaris.UCSC.canFam3.masked")

if (args$genome=="Mmul8.0.1"){args$genome="rheMac8"}

deseqout=read.delim(args$degout)
dim(deseqout)
fdr_filter=deseqout$fdr < args$fdr
positive_lfc_filter=deseqout$log2fc>1
negative_lfc_filter=deseqout$log2fc < -1
table(( negative_lfc_filter | positive_lfc_filter ) & fdr_filter )
deseqout_filtered=deseqout[( ( negative_lfc_filter | positive_lfc_filter ) & fdr_filter ),]

coordinates=read.delim(args$gene2coord,header=FALSE)
colnames(coordinates)=c("chr","start","end","strand","ensid","biotype","gene_name")
deseqout_filtered_w_coord=merge(deseqout_filtered,coordinates,by.x="gene",by.y="gene_name")
dim(deseqout_filtered_w_coord)

if(nrow(deseqout_filtered_w_coord)==0){
  stop("No DEGs found. Try increasing FDR cutoff")
}

genome=args$genome
chrs=c()
maxchrs=0
if (genome %in% c("hg19","hg38")) {maxchrs=22}
if (genome %in% c("mm10","mm9")) {maxchrs=19}
if (genome %in% c("rheMac8")) {maxchrs=20}
if (genome %in% c("canFam3")) {maxchrs=38}

for (i in seq(1,maxchrs)) {chrs=c(chrs,paste("chr",i,sep=""))}
chrs=c(chrs,"chrX")
if (! genome %in% c("canFam3")){chrs=c(chrs,"chrY")}

y=round(length(chrs)/2)
a=chrs[seq(1,y)]
b=chrs[seq(y+1,length(chrs))]
chrs_subsets=list(a,b)

deseqout_filtered_w_coord=deseqout_filtered_w_coord[deseqout_filtered_w_coord$chr %in% chrs,]
dim(deseqout_filtered_w_coord)

pos_scale_limit=abs(floor(fivenum(deseqout_filtered_w_coord$log2fc)[2]))+0.5
neg_scale_limit=-1*(abs(ceiling(fivenum(deseqout_filtered_w_coord$log2fc)[4]))+0.5)

deseqout_filtered_w_coord[deseqout_filtered_w_coord$log2fc > pos_scale_limit,]$log2fc=pos_scale_limit
deseqout_filtered_w_coord[deseqout_filtered_w_coord$log2fc < neg_scale_limit,]$log2fc=neg_scale_limit

upregulated=deseqout_filtered_w_coord[deseqout_filtered_w_coord$log2fc>0,]
downregulated=deseqout_filtered_w_coord[deseqout_filtered_w_coord$log2fc<0,]


for (i in seq(1,length(chrs_subsets))) {
  chrs2=unlist(chrs_subsets[i])
  pdf(paste("karyoplot",i,".pdf",sep=""))
  kp <- plotKaryotype(genome=genome, plot.type=2, chromosomes = chrs2, cytobands=NULL)

  kpDataBackground(kp, data.panel = 1, r0=0, r1=1)
  kpDataBackground(kp, data.panel = 2, r0=0, r1=1)
  kpHeatmap(kp, chr=upregulated$chr, 
            x0=upregulated$start, 
            x1=upregulated$end, 
            y=upregulated$log2fc, 
            data.panel = 1,
            colors = c("white", "red"))
  kpHeatmap(kp, chr=downregulated$chr, 
            x0=downregulated$start, 
            x1=downregulated$end, 
            y=downregulated$log2fc, 
            data.panel = 2,
            colors = c("blue", "white"))
  dev.off()
}
