
task downsample_bams {
  Array[File] reads_bam
  Int?         readCount
  Boolean?     deduplicateBefore=false
  Boolean?     deduplicateAfter=false

  command {
    if [[ "${deduplicateBefore}" == "true" ]]; then
      DEDUP_OPTION="--deduplicateBefore"
    elif [[ "${deduplicateAfter}" == "true" ]]; then
      DEDUP_OPTION="--deduplicateAfter"
    fi

    if [[ "${deduplicateBefore}" == "true" && "${deduplicateBefore}" == "true" ]]; then
      echo "deduplicateBefore and deduplicateAfter are mutually exclusive. Only one can be used."
      exit 1
    fi
    
    read_utils.py downsample_bams \
        ${sep=' ' reads_bam} \
        --outPath downsampled \
        ${'--readCount' + readCount} \
        $DEDUP_OPTION \
  }

  output {
    Array[File] downsampled_bam = glob("downsampled/*.bam")
  }
  runtime {
    docker: "quay.io/broadinstitute/viral-ngs"
    memory: "3 GB"
    cpu: 2
    dx_instance_type: "mem1_ssd1_x2"
  }
}