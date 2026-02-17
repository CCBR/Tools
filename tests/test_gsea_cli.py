import sys

import pandas as pd
import pytest

import ccbr_tools.GSEA.deg2gs as deg2gs
import ccbr_tools.GSEA.multitext2excel as mt2excel


def test_deg2gs_gsea_pipeliner(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "gene": ["GeneA", "GeneB", "GeneC"],
            "fc": [1.0, 2.0, 3.0],
            "log2FC": [1.0, 2.0, 3.0],
            "p": [0.04, 0.01, 0.2],
            "q": [0.05, 0.02, 0.5],
            "gsea": [5.0, 10.0, 2.0],
        },
        index=["ENSG1", "ENSG2", "ENSG3"],
    )
    infile = tmp_path / "deg.csv"
    outfile = "deg.rnk"
    df.to_csv(infile)

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "deg2gs.py",
            "-i",
            str(infile),
            "-o",
            outfile,
            "-n",
            "2",
            "-p",
            "0.05",
            "-q",
            "0.1",
            "-m",
            "gsea",
            "-f",
            "pipeliner",
        ],
    )
    deg2gs.main()

    output_lines = (tmp_path / outfile).read_text(encoding="utf-8").strip().splitlines()
    assert output_lines[0].startswith("GeneB\t")
    assert output_lines[1].startswith("GeneA\t")


def test_deg2gs_toppfun_top_table(tmp_path, monkeypatch):
    df = pd.DataFrame(
        {
            "log2FC": [1.5, 2.5],
            "AveExpr": [10.0, 11.0],
            "gsea": [1.0, 2.0],
            "p": [0.01, 0.02],
            "q": [0.02, 0.03],
            "B": [0.0, 0.1],
        },
        index=["ENSG0001|TP53", "ENSG0002|BRCA1"],
    )
    infile = tmp_path / "top.csv"
    outfile = "top.rnk"
    df.to_csv(infile)

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(
        sys,
        "argv",
        [
            "deg2gs.py",
            "-i",
            str(infile),
            "-o",
            outfile,
            "-m",
            "toppfun",
            "-f",
            "topTable",
            "-n",
            "10",
            "-p",
            "0.05",
            "-q",
            "0.1",
        ],
    )
    deg2gs.main()

    output = (tmp_path / outfile).read_text(encoding="utf-8")
    assert "TP53" in output
    assert "BRCA1" in output


def test_multitext2excel_writes_sheets(tmp_path, monkeypatch):
    pytest.importorskip("openpyxl")

    input_dir = tmp_path / "inputs"
    input_dir.mkdir()
    (input_dir / "a.txt").write_text("col1\tcol2\n1\t2\n", encoding="utf-8")
    (input_dir / "b.txt").write_text("col1\tcol2\n3\t4\n", encoding="utf-8")

    outfile = tmp_path / "out.xlsx"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "multitext2excel.py",
            "-o",
            str(outfile),
            "-d",
            str(input_dir),
            "-p",
            ".txt",
            "-k",
            "\t",
            "-s",
            ".",
        ],
    )
    mt2excel.main()

    xls = pd.ExcelFile(outfile)
    assert set(xls.sheet_names) == {"a", "b"}
