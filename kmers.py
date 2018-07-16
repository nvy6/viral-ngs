#!/usr/bin/env python

"""Commands for working with sets of kmers"""


from __future__ import print_function
__author__ = "ilya@broadinstitute.org"

__commands__ = []

import argparse
import logging
import functools

import util.cmd
import util.file
import util.misc
import tools
import tools.picard
import tools.samtools
import tools.kmc

log = logging.getLogger(__name__)  # pylint: disable=invalid-name

# =================================

def build_kmer_db(seq_files, kmer_db, kmer_size=tools.kmc.DEFAULT_KMER_SIZE, min_occs=None, max_occs=None,
                  counter_cap=tools.kmc.DEFAULT_COUNTER_CAP, single_strand=False, mem_limit_gb=8, mem_limit_laxness=0,
                  threads=None):
    """Build a database of kmers occurring in given sequences."""
    tools.kmc.KmcTool().build_kmer_db(**locals())

def parser_build_kmer_db(parser=argparse.ArgumentParser()):
    """Create parser for build_kmer_db"""
    parser.add_argument('seq_files', nargs='+',
                        help='Files from which to extract kmers (fasta/fastq/bam, fasta/fastq may be .gz or .bz2)')
    parser.add_argument('kmer_db', help='kmer database (with or without .kmc_pre/.kmc_suf suffix)')
    parser.add_argument('--kmerSize', '-k', dest='kmer_size', type=int, default=tools.kmc.DEFAULT_KMER_SIZE,
                        help='kmer size')
    parser.add_argument('--minOccs', '-ci', dest='min_occs', type=int, default=1,
                        help='drop kmers with fewer than this many occurrences')
    parser.add_argument('--maxOccs', '-cx', dest='max_occs', type=int, default=util.misc.MAX_INT32,
                        help='drop kmers with more than this many occurrences')
    parser.add_argument('--counterCap', '-cs', dest='counter_cap', type=int,
                        default=tools.kmc.DEFAULT_COUNTER_CAP, help='cap kmer counts at this value')
    parser.add_argument('--singleStrand', '-b', dest='single_strand', default=False, action='store_true',
                        help='do not add kmers from reverse complements of input sequences')
    parser.add_argument('--memLimitGb', dest='mem_limit_gb', default=8, type=int, help='Max memory to use, in GB')
    parser.add_argument('--memLimitLaxness', dest='mem_limit_laxness', default=0, type=int, choices=(0, 1, 2),
                        help='How strict is --memLimitGb?  0=strict, 1=lax, 2=even more lax')
    util.cmd.common_args(parser, (('threads', None), ('loglevel', None), ('version', None), ('tmp_dir', None)))
    util.cmd.attach_main(parser, build_kmer_db, split_args=True)
    return parser

__commands__.append(('build_kmer_db', parser_build_kmer_db))

# =========================

def dump_kmer_counts(kmer_db, out_kmers, min_occs=1, max_occs=util.misc.MAX_INT32, threads=None):
    """Dump kmers and their counts from kmer database to a text file"""
    tools.kmc.KmcTool().dump_kmer_counts(**locals())

def parser_dump_kmer_counts(parser=argparse.ArgumentParser()):
    """Create parser for dump_kmer_counts"""
    parser.add_argument('kmer_db', help='kmer database (with or without .kmc_pre/.kmc_suf suffix)')
    parser.add_argument('out_kmers', help='text file to which to write the kmers')
    parser.add_argument('--minOccs', '-ci', dest='min_occs', type=int, default=1,
                        help='drop kmers with fewer than this many occurrences')
    parser.add_argument('--maxOccs', '-cx', dest='max_occs', type=int, default=util.misc.MAX_INT32,
                        help='drop kmers with more than this many occurrences')

    util.cmd.common_args(parser, (('threads', None), ('loglevel', None), ('version', None), ('tmp_dir', None)))
    util.cmd.attach_main(parser, dump_kmer_counts, split_args=True)
    return parser

__commands__.append(('dump_kmer_counts', parser_dump_kmer_counts))

# =========================

def filter_by_kmers(kmer_db, in_reads, out_reads, db_min_occs=1, db_max_occs=util.misc.MAX_INT32,
                    read_min_occs=None, read_max_occs=None, hard_mask=False, threads=None):
    """Filter sequences based on their kmer contents.

       Note that 'occurrence of a kmer' means 'occurrence of the kmer or its reverse complement' if kmer_db was built
       without the --singleStrand flag.
    """
    tools.kmc.KmcTool().filter_reads(**locals())

def parser_filter_by_kmers(parser=argparse.ArgumentParser()):
    """Create parser for filter_by_kmers"""
    parser.add_argument('kmer_db', help='kmer database (with or without .kmc_pre/.kmc_suf suffix)')
    parser.add_argument('in_reads', help='input reads, as fasta/fastq/bam')
    parser.add_argument('out_reads', help='output reads')
    parser.add_argument('--dbMinOccs', dest='db_min_occs', type=int, default=1,
                        help='ignore datatbase kmers with count below this')
    parser.add_argument('--dbMaxOccs', dest='db_max_occs', type=int, default=util.misc.MAX_INT32,
                        help='ignore datatbase kmers with count above this')
    int_or_float = functools.partial(util.misc.as_type, **dict(types=(int, float)))
    parser.add_argument('--readMinOccs', dest='read_min_occs', type=int_or_float,
                        help='filter out reads with fewer than this many db kmers; '
                        'if a float, interpreted as fraction of read length')
    parser.add_argument('--readMaxOccs', dest='read_max_occs', type=int_or_float,
                        help='filter out reads with more than this many db kmers; '
                        'if a float, interpreted as fraction of read length')
    parser.add_argument('--hardMask', dest='hard_mask', default=False,
                        action='store_true',
                        help='In the output reads, mask the invalid kmers')
    util.cmd.common_args(parser, (('threads', None), ('loglevel', None), ('version', None), ('tmp_dir', None)))
    util.cmd.attach_main(parser, filter_by_kmers, split_args=True)
    return parser

__commands__.append(('filter_by_kmers', parser_filter_by_kmers))

# =========================

def kmers_binary_op(op, kmer_db1, kmer_db2, kmer_db_out, threads=None):  # pylint: disable=invalid-name
    """Perform a simple binary operation on kmer sets."""

    tools.kmc.KmcTool().kmers_binary_op(op, kmer_db1, kmer_db2, kmer_db_out, threads=threads)

def parser_kmers_binary_op(parser=argparse.ArgumentParser()):
    """Create parser forkmers_binary_op"""
    parser.add_argument('op', choices=('intersect', 'union', 'kmers_subtract', 'counters_subtract'),
                        help='binary operation to perform')
    parser.add_argument('kmer_db1', help='first kmer set')
    parser.add_argument('kmer_db2', help='second kmer set')
    parser.add_argument('kmer_db_out', help='output kmer db')
    util.cmd.common_args(parser, (('threads', None), ('loglevel', None), ('version', None), ('tmp_dir', None)))
    util.cmd.attach_main(parser, kmers_binary_op, split_args=True)
    return parser

__commands__.append(('kmers_binary_op', parser_kmers_binary_op))

# =========================

def kmers_set_counts(kmer_db_in, value, kmer_db_out, threads=None):
    """Copy the kmer database, setting all kmer counts in the output to the given value."""

    tools.kmc.KmcTool().set_kmer_counts(kmer_db_in, value, kmer_db_out, threads=threads)

def parser_kmers_set_counts(parser=argparse.ArgumentParser()):
    """Create parser for kmers_set_counts"""
    parser.add_argument('kmer_db_in', help='input kmer db')
    parser.add_argument('value', type=int, help='all kmer counts in the output will be set to this value')
    parser.add_argument('kmer_db_out', help='output kmer db')
    util.cmd.common_args(parser, (('threads', None), ('loglevel', None), ('version', None), ('tmp_dir', None)))
    util.cmd.attach_main(parser, kmers_set_counts, split_args=True)
    return parser

__commands__.append(('kmers_set_counts', parser_kmers_set_counts))

# ========================

def full_parser():
    """Create parser for all commands in kmers.py"""
    return util.cmd.make_parser(__commands__, __doc__)


if __name__ == '__main__':
    util.cmd.main_argparse(__commands__, __doc__)
