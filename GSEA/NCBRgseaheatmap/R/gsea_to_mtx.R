####################
#
#  Frederick National Laboratory
#  Susan Huse, susan.huse@@nih.gov
#  October 9, 2018
#
####################
#' Reads a GSEA output file and creates a matrix from the positive and negative report files, 
#' that serves as input to pathway_heatmap
#'
#' Reads in both the positive and negative GSEA enrichment reports from the appropriate directories, 
#'   reads the scoring column (default="GseaPreranked") and creates a single matrix of 
#'   positive and negative enrichment scores
#' 
#' The directory list should be generated with the list.dirs() function, 
#' these directories will be further filtered to only those containing the db name (e.g., GO or Path).
#'
#' Once the GSEA results have been read in, they will be filtered to only q (FDR) values 
#' less than the minimum (q).  
#' The set of resulting matrices for each comparison will be filtered to include only a maximum of preN values.
#' The matrices will then be combined across all comparisons, and the filtered again to a maximum number of rows (postN).  
#' The current RNASeq pipeliner sets the normalized GSEA score to "GseaPreranked", 
#' Use colname to set the appropriate column name for GSEA results derived from outside of pipeliner.
#'
#' @param dirlist a list of GSEA directories of interest, containing the results for multiple gene sets
#' @param db the geneset database to include, e.g., GO or Path, as imbedded in the output GSEA directory names
#' @param q minimum FDR / q-value cutoff for including genesets in the output matrix
#' @param preN maximum number of rows to include from each input GSEA analysis (pairwise comparison)
#' @param postN maximum number of rows to include in the final merged matrix.
#' @param colname name of the column in the GSEA output containing the normalized scores ("GseaPreranked" for RNASeq pipeliner results)
#' 
#' @return a list of three elements: 
#'         1) numeric matrix, with rownames as genesets, column names as comparisons
#'         2) a vector of names for the columns containing the actual enrichment data
#'         3) a vector of names for the column names containing q-values
#'
#' @author Susan Huse \email{susan.huse@@nih.gov}
#' @keywords RNASeq Pipeliner GSEA geneset heatmap
#'
#' @examples
#' alldirs = list.dirs(path=dir_gsea3, full.names=TRUE, recursive=FALSE)
#' nes <- gsea_to_mtx(dirlist, db="GO", q=0.1, preN=50, postN=50)
#' pdf("myoutput.pdf")
#' pathway_heatmap(nes, clustrow=clustrow, clustcol=1, cluster_cols=FALSE,
#'                 main=main, samples=samples, annotlegend=FALSE, 
#'                 fontsize_row=fontsize_row, fontsize_col=12)
#' dev.off()
#'
#' @export
gsea_to_mtx <- function(dirlist, db="GO", q=0.1, preN=25, postN=NULL, colname="GseaPreranked") {
  # read the directories, 
  # double check that there are at least two valid GSEA db directories
  dirlist = dirlist[grep(paste("", db, colname, sep="."), dirlist)]
  if(length(dirlist) < 2) {print("Insufficient GSEA directories to create heatmap"); return(NULL)}

  # set the list of normalized enrichment scores across all comparisons
  nes_list <- list()
  allRows <- c()

  # Step through the directories and import each matrix, filter
  for(d in dirlist) {
    # print(d)
    comparison = gsub(paste("", db, "GseaPreranked", "*$", sep="."), "", basename(d))
    
    # pull gsea_report_for_na_neg_1536947190154.xls and gsea_report_for_pos_neg_1536947190154.xls
    xlsfiles <- list.files(path=d, pattern="gsea_report_for_na", full.names=TRUE)
    xlsfiles = xlsfiles[grepl(".xls", xlsfiles)]

    # These are actually tab delimited files, not Excel formatted
    # import and grab the name, score, q
    neg <- as.data.frame(read.table(xlsfiles[1], header=TRUE, sep="\t"))[, c("NAME", "NES", "FDR.q.val")]
    pos <- as.data.frame(read.table(xlsfiles[2], header=TRUE, sep="\t"))[, c("NAME", "NES", "FDR.q.val")]

    df <- rbind(pos, neg)
    colnames(df) <- c("Name", comparison, paste0("qFDR_", comparison))

    # sort by q-value then filter the individual dataframes with "preN"
    dfq <- df[df[, 3] <= q, ]
    
    # We need to individually decide the top preN rows, 
    # but have to keep everything in the matrix, so that if it is not q-significant here, but is elsewhere
    # we have the NES value for it.
    theRows <- dfq[,1]
    if (! is.null(preN)) {
      df <- df[order(df[,3]),]
      
      if(length(theRows) > preN) {
        theRows <- theRows[1:preN]
      }
    }
    # print(df)
    
    # create a list for merge later
    if(length(theRows) > 0) {
      nes_list[[comparison]] <- df
      allRows <- union(allRows, theRows)
    }
  }
  
  # merge all
  first=TRUE
  for(x in nes_list) {
    if(first) {
      mergedDF <- x
      first <- FALSE
    } else {
      mergedDF <- merge(mergedDF, x, by="Name", all=TRUE)
    }
  }

  # Set the rownames and remove the gene sets from the data
  rownames(mergedDF) <- mergedDF$Name
  mergedDF <- mergedDF[, 2:ncol(mergedDF)]
  mergedDF <- mergedDF[allRows,]

  # find qsig rows
  qcols <- colnames(mergedDF)[grepl("^qFDR_", colnames(mergedDF), perl=TRUE)]
  dcols <- colnames(mergedDF)[! colnames(mergedDF) %in% qcols]

  # limit to postN rows if appropriate
  # sort the ones that are significant by how many columns are significant
  get_qrows <- function(x,q) { x[is.na(x)] <- 1; sum(x < q) }
  if(! is.null(postN)) {
    if (nrow(mergedDF) > postN) {
      qrows <- apply(mergedDF[,qcols], 1, function(x){get_qrows(x, q)})
      mergedDF <- mergedDF[names(sort(qrows, decreasing=TRUE)),]
      mergedDF <- mergedDF[1:postN,]
    }
  }

  # return the results as a list, including the matrix, the data columns and the q-value columns
  return(list(mtx = as.matrix(mergedDF), dcols=dcols, qcols=qcols))
}
