from gtfparse import read_gtf
import itertools
import sys
from plotly.colors import DEFAULT_PLOTLY_COLORS as plcolors


class Transcript(object):
    def __init__(self, transcript_id, name, exon_tuples, strand):
        self.transcript_id = transcript_id
        self.name = name
        self.exon_tuples = list(exon_tuples)
        self.strand = strand
        self.begin = min(list(itertools.chain.from_iterable(self.exon_tuples)))
        self.end = max(list(itertools.chain.from_iterable(self.exon_tuples)))
        self.color = ""


def parse_gtf(gtff, window):
    """
    Parse the gtff using read_gtf and select the relevant region
    as determined by the window

    """
    gtf = read_gtf(gtff)
    columns = ["start", "end", "strand", "transcript_id", "gene_name"]
    gtf_f = gtf.loc[(gtf["feature"] == "exon") & (gtf["seqname"] == window.chromosome), columns]
    transcript_slice = (gtf_f.groupby("transcript_id")["start"].max() > window.begin) & (
        gtf_f.groupby("transcript_id")["end"].min() < window.end)
    transcripts = transcript_slice[transcript_slice].index
    region = gtf_f.loc[gtf_f["transcript_id"].isin(transcripts)]
    result = []
    for t in transcripts:
        tr = region.loc[region["transcript_id"] == t]
        result.append(
            Transcript(transcript_id=t,
                       name=tr["gene_name"].tolist()[0],
                       exon_tuples=tr.loc[:, ["start", "end"]]
                                     .sort_values("start")
                                     .itertuples(index=False, name=None),
                       strand=tr["strand"].tolist()[0])
        )
    sys.stderr.write("Found {} transcripts in the region.\n".format(len(result)))
    genes = set([t.name for t in result])
    colordict = {g: c for g, c in zip(genes, plcolors * 100)}
    for t in result:
        t.color = colordict[t.name]
    return result
