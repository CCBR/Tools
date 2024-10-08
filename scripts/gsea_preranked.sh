#!/bin/sh
##
## Susan Huse, NCBR, FNLCR
## susan.huse@nih.gov
## Tue Aug 7 15:33:35 EDT 2018
## run_gsea_preranked
##
##
set -e


if [ $# -lt 1 ]; then
  echo
  echo 'Usage:   run_gsea_preranked rankfile gmtfile label'
  echo 'Example: run_gsea_preranked KO_WT.rnk MousePath_GO_gmt.gmt KO_WT.GO'
  echo
  exit
fi
RNK=$1
GMT=$2
LABEL=$3
#LABEL=`echo $RNK | sed -e 's/\.rnk//'`
OUT="."

NPERM=100
SCORE='weighted'
SVGS='false'
MAKESETS='true'
PLOTTOP=20
MAX=1000
MIN=5

echo "java -cp ~/bin/gsea-3.0.jar -Xmx4g xtools.gsea.GseaPreranked -gmx $GMT -rnk $RNK -rpt_label $LABEL -out $OUT \
    -norm meandiv -nperm $NPERM -scoring_scheme $SCORE -create_svgs $SVGS -make_sets $MAKESETS -plot_top_x $PLOTTOP -rnd_seed timestamp \
    -set_max $MAX -set_min $MIN -zip_report false -gui false"

java -cp ~/bin/gsea-3.0.jar -Xmx4g xtools.gsea.GseaPreranked -gmx $GMT -rnk $RNK -rpt_label $LABEL -out $OUT \
    -norm meandiv -nperm $NPERM -scoring_scheme $SCORE -create_svgs $SVGS -make_sets $MAKESETS -plot_top_x $PLOTTOP -rnd_seed timestamp \
    -set_max $MAX -set_min $MIN -zip_report false -gui false


#java -cp ~/bin/gsea-3.0.jar -Xmx512m xtools.gsea.GseaPreranked -gmx /Users/husesm/FNL/Projects/Reference/GeneSets_Mouse/MousePath_Co-expression_gmt.gmt -norm meandiv -nperm 100 -rnk /Users/husesm/FNL/Projects/Colitis/NCBR-4/analysis/gsea/KO_Th17_NoTGFb.rnk -scoring_scheme classic -rpt_label KO_Th17_NoTGFb -create_svgs false -make_sets true -plot_top_x 20 -rnd_seed timestamp -set_max 500000 -set_min 15 -zip_report false -out /Users/husesm/FNL/Projects/Colitis/NCBR-4/analysis/gsea -gui false
