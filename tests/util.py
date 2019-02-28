import os
import subprocess

import pysam

def make_bam(sam_path):
    sam_file = os.path.basename(sam_path)
    sam_base, sam_ext = os.path.splitext(sam_file)
    sam_dir = os.path.dirname(sam_path)
    bam_file = sam_base + '.bam'
    bam_path = os.path.join(sam_dir, bam_file)

    with open(sam_path, 'r') as f_in:
        infile = pysam.AlignmentFile(f_in, "r", check_sq=False)
        with open(bam_path, 'wb') as f_out:
            outfile = pysam.AlignmentFile(bam_path, "wb", template=infile)
            for line in infile:
                outfile.write(line)
    return bam_path

def make_bam_view(sam_path):
    sam_file = os.path.basename(sam_path)
    sam_base, sam_ext = os.path.splitext(sam_file)
    sam_dir = os.path.dirname(sam_path)
    bam_file = sam_base + '.bam'
    bam_path = os.path.join(sam_dir, bam_file)

    pysam.view('-o', bam_path, '-bh', sam_path, save_stdout=bam_file)
    return bam_path

def subprocess_make_bam(sam_path, logger):
    sam_file = os.path.basename(sam_path)
    sam_base, sam_ext = os.path.splitext(sam_file)
    sam_dir = os.path.dirname(sam_path)
    bam_file = sam_base + '.bam'
    bam_path = os.path.join(sam_dir, bam_file)

    runcmd = ['samtools', 'view','-bh', '-o', bam_path, sam_path]
    try:
        subprocess.check_output(runcmd)
    except subprocess.CalledProcessError as e:
        logger.info('`samtools view` warning is:\n\t{}'.format(e))
    return bam_path
