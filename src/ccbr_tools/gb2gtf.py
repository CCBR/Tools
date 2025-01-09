"""
Module for converting GenBank files to GTF format.

Usage:
    python gb2gtf.py sequence.gb > sequence.gtf
"""

# download GenBank file from NCBI and then
# Usage:python gb2gtf.py sequence.gb  > sequence.gtf

import sys
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.SeqFeature import SeqFeature, FeatureLocation
from Bio import SeqIO
import Bio


def main():
    if check_args(sys.argv):
        gb2gtf(sys.argv)


usage_msg = """Convert GenBank files to GTF format.

Usage: gb2gtf sequence.gb > sequence.gtf
"""


def check_args(args):
    valid_usage = True
    if len(args) < 2 or "-h" in args or "--help" in args:
        print(usage_msg)
        valid_usage = False
    return valid_usage


def gb2gtf(args):
    # get all sequence records for the specified genbank file
    recs = [rec for rec in SeqIO.parse(args[1], "genbank")]

    # print the number of sequence records that were extracted
    # print(len(recs))

    # print annotations for each sequence record
    # for rec in recs:
    # 	print(rec.annotations)

    # print the CDS sequence feature summary information for each feature in each
    # sequence record
    for rec in recs:
        # print(type(rec))
        seqname = rec.id
        # feats = [feat for feat in rec.features if feat.type == "CDS"]
        feats = [feat for feat in rec.features]
        for feat in feats:
            #        print(feat)
            l = feat.location
            start = l.start
            end = l.end
            if feat.location.strand == 1:
                strand = "+"
            else:
                strand = "-"
            if feat.type == "gene":
                gffstring = list()
                gffstring.append(seqname)
                gffstring.append("RefSeq")
                gffstring.append("gene")
                gffstring.append(str(start))
                gffstring.append(str(end))
                gffstring.append(".")
                gffstring.append(strand)
                gffstring.append(".")
                q = feat.qualifiers
                try:
                    gene = q["gene"][0]
                except:
                    try:
                        gene = q["locus_tag"][0]
                    except:
                        exit("Something fishy!")

                x = 'gene_name "%s"; gene_id "%s"' % (gene, gene)
                gffstring.append(x)
                print("\t".join(gffstring) + ";")
            #            #print(feat.qualifiers.keys())
            #            #print(feat.qualifiers.values())
            elif feat.type == "CDS":
                # if feat.type=="CDS":
                gffstring = list()
                gffstring.append(seqname)
                gffstring.append("RefSeq")
                gffstring.append("transcript")
                gffstring.append(str(start))
                gffstring.append(str(end))
                gffstring.append(".")
                gffstring.append(strand)
                gffstring.append(".")
                q = feat.qualifiers
                try:
                    gene = q["gene"][0]
                except:
                    try:
                        gene = q["locus_tag"][0]
                    except:
                        exit("Something fishy!")
                x = (
                    'gene_name "%s"; gene_id "%s"; transcript_id "%s"; transcript_name "%s"'
                    % (gene, gene, gene, gene)
                )
                gffstring.append(x)
                print("\t".join(gffstring) + ";")
                gffstring[2] = "exon"
                if isinstance(l, Bio.SeqFeature.CompoundLocation):
                    parts = l.parts
                    # lenparts=len(parts)
                    for i, part in enumerate(parts):
                        j = i + 1
                        start = part.start
                        end = part.end
                        gffstring2 = gffstring
                        gffstring2[3] = str(start)
                        gffstring2[4] = str(end)
                        y = x + "; exon_number %s" % (str(j))
                        gffstring2[8] = y
                        print("\t".join(gffstring2) + ";")
                else:
                    y = x + "; exon_number 1"
                    gffstring[8] = y
                    print("\t".join(gffstring) + ";")

            #            print(j,part)
            else:
                continue

            # else:

    #        print(l.start)
    #        exit()
    #        for l in feat.location:
    #            print(l.start)
    #            print(l.end)
    #            print(l.strand)
    #            exit()
    #        print(type(feat.location))
    #        print(feat.strand)
    #        exit()


if __name__ == "__main__":
    main()
