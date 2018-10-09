####################
#
#  Frederick National Laboratory
#  Susan Huse, susan.huse@@nih.gov
#  October 9, 2018
#
####################
#' Creates a pretty heatmap with q-values for multiple GSEA comparisons
#'  expects a matrix containing normalized enrichment scores and q-values from gsea_to_mtx()
#'
#' Creates a heatmap (using pheatmap) from the matrix, with a primary heatmap of GSEA enrichment scores
#'   and a secondary heatmap of q-values (FDR). 
#'   A more stringent q-value can be set then used in gsea_to_mtx for subsequent heatmaps
#'
#' @param nes matrix of GSEA normalized enrichment scores and q-values created with gsea_to_mtx()
#' @param q minimum FDR / q-value cutoff for including genesets in the output matrix
#' @param clustrow number of clusters for the row dendogram (see pheatmap)
#' @param clustcol number of clusters for the row dendogram (see pheatmap)
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
#' nes <- gsea_to_mtx(dirlist, db="GO", q=0.1, preN=50, postN=50)
#' pathway_heatmap(nes, clustrow=clustrow, clustcol=1, cluster_cols=FALSE,
#'                 main=main, samples=samples, annotlegend=FALSE, 
#'                 fontsize_row=fontsize_row, fontsize_col=12)
#'
#' @export
pathway_heatmap <- function(nes, q=0.1, clustrow=1, clustcol=1, cluster_cols=TRUE, main=NULL, 
                            annotlegend, samples=NULL, fontsize_row=12, fontsize_col=12) {
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
  pctRed <- round(max(datamtx) / (max(datamtx) - min(datamtx)) * 100)
  pctBlue <- abs(round(min(datamtx) / (max(datamtx) - min(datamtx)) * 100))
  reds = colorRampPalette(brewer.pal(n=7, name = "Reds"))(pctRed)
  blues = colorRampPalette(rev(brewer.pal(n=7, name = "Blues")))(pctBlue)
  color = c(blues, rep("#BEBEBE",3), reds)
  
  
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
