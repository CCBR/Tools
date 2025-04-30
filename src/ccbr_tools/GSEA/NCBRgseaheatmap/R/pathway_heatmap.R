####################
#
#  Frederick National Laboratory
#  Susan Huse, susan.huse@@nih.gov
#  October 9, 2018
#
####################
#' Creates a pretty heatmap of both gene set enrichment and q-values for multiple GSEA comparisons
#'
#' Creates a heatmap (using pheatmap) from the matrix, with a primary heatmap of GSEA enrichment scores
#'   and a secondary heatmap of q-values (FDR).
#'
#' Assumes that a matrix of normalized enrichment scores from GSEA analyses has been created using gsea_to_mtx.
#' The heatmap is created using the pheatmap package.  Many of the pheatmap parameters are included in this function.
#' A more stringent q-value can be set then used in gsea_to_mtx for subsequent heatmaps
#' Currently the ordering of the q-value columns is not the same as the data (enrichment score) columns.
#' Setting of the fontsize_row, fontsize_col, clustrow, and clustcol will likely take several tries to create the optimum heatmap for your data.
#'
#' @param nes matrix of GSEA normalized enrichment scores and q-values created with gsea_to_mtx()
#' @param q minimum FDR / q-value cutoff for including genesets in the output matrix
#' @param clustrow number of sections to split the heatmap into based on the row dendogram. (see pheatmap: cutree_rows)
#' @param clustcol number of sections to split the heatmap into based on the column dendogram. (see pheatmap: cutree_cols)
#' @param annotlegend boolean to include the annotation_legend or not (see pheatmap)
#' @param samples sample names to be used in the annotation_col, should be in the same order as the data matrix (see pheatmap)
#' @param fontsize_row font size for row text displaying gene sets (see pheatmap)
#' @param fontsize_col font size for col text displaying sample names (see pheatmap)
#' @param main text string for main heatmap title
#'
#' @return a heatmap object for printing
#'
#' @author Susan Huse \email{susan.huse@@nih.gov}
#' @keywords RNASeq Pipeliner GSEA geneset heatmap
#'
#' @examples
#' alldirs = list.dirs(path=dir_gsea3, full.names=TRUE, recursive=FALSE)
#' dirlist = alldirs[grepl(paste0("KO_vs_WT.", i, ".GseaPreranked.[0-9]*$"), alldirs, perl=TRUE)]
#' nes <- gsea_to_mtx(dirlist, db="GO", q=0.1, preN=50, postN=50)
#' main=paste("Gene Set Enrichment:", i, "\nPairwise comparisons by experiment")
#' fontsize_row=8
#' clustrow = 3
#' pdf("myoutput.pdf")
#' pathway_heatmap(nes, clustrow=clustrow, clustcol=1, cluster_cols=FALSE,
#'                 main=main, samples=NULL, annotlegend=FALSE,
#'                 fontsize_row=fontsize_row, fontsize_col=12)
#' dev.off()
#'
#' @import pheatmap
#' @import RColorBrewer
#' @import randomcoloR
#' @export
pathway_heatmap <- function(nes, q=0.1, clustrow=1, clustcol=1, cluster_cols=TRUE, main="",
                            annotlegend=TRUE, samples=NULL, fontsize_row=12, fontsize_col=12) {
  require("pheatmap")
  require("RColorBrewer")
  require("randomcoloR")
  datamtx <- nes$mtx[, nes$dcols]
  datamtx[is.na(datamtx)] <- 0

  # Create the q sig annotation along the side
  colorvector <- c("white", "black"); names(colorvector) <- 0:1

  # Reset the qFDR matrix to 0/1 NotSig / Sig
  annotrow <- as.data.frame(nes$mtx[, nes$qcols])
  annotrow[annotrow <= q] <- -1
  annotrow[annotrow > q] <- 0
  annotrow[annotrow == -1] <- 1
  annotrow[is.na(annotrow)] <- 0

  # create the list of annotation colors
  anncolors <- list()
  for(i in 1:ncol(annotrow)) {
    anncolors[[colnames(annotrow)[i]]] <- colorvector
    annotrow[, i] <- as.factor(annotrow[, i])
  }

  # Create annotation of samples along the top
  if(is.null(samples)) {
    annotcol=NULL
  } else {
    annotcol <- data.frame(Samples=factor(samples))
    rownames(annotcol) <- nes$dcols

    colorvector <- distinctColorPalette(length(unique(samples)))
    names(colorvector) <- unique(samples)
    anncolors[["Samples"]] <- colorvector
  }

  # double check the requested number of clusters
  if (clustrow < 1) {clustrow <- 1}
  if (clustcol < 1) {clustcol <- 1}
  if (! cluster_cols) {clustcol == NULL}

  # Set the colorramp for the data
  if(max(datamtx) <= 0) {
    pctRed = 0
    pctBlue = 100
  } else if(min(datamtx) >= 0) {
    pctRed = 100
    pctBlue = 0
  } else {
    pctRed <- round(max(datamtx) / (max(datamtx) - min(datamtx)) * 100)
    pctBlue <- abs(round(min(datamtx) / (max(datamtx) - min(datamtx)) * 100))
  }

  reds = colorRampPalette(brewer.pal(n=7, name = "Reds"))(pctRed)
  blues = colorRampPalette(rev(brewer.pal(n=7, name = "Blues")))(pctBlue)
  color = c(blues, rep("#BEBEBE",1), reds)


  # export the heatmap
  return(pheatmap(datamtx,
                  main=main,
                  color=color,
                  annotation_row=annotrow,
                  annotation_colors=anncolors,
                  annotation_legend=annotlegend,
                  annotation_col=annotcol,
                  fontsize_row=fontsize_row,
                  fontsize_col=fontsize_col,
                  cutree_rows = clustrow,
                  cutree_cols = clustcol,
                  cluster_cols=cluster_cols,
                  show_rownames=TRUE))
}
