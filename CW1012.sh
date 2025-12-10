set -euo pipefail

if [ $# -lt 1 ]; then
    echo "Użycie: $0 DIR1 [DIR2 ...]"
    exit 1
fi

COMPRESSORS=("gzip" "bzip2" "xz" "zstd" "lz4" "7z")

measure_time() {
    local start end
    start=$(date +%s.%N)
    "$@" >/dev/null 2>&1
    end=$(date +%s.%N)
    echo "$(echo "$end - $start" | bc -l)"
}

for DIR in "$@"; do
    echo "$DIR"

    tmp_dir=$(mktemp -d)
    tarfile="$tmp_dir/archive.tar"
    tar cf "$tarfile" "$DIR"

    orig_size=$(stat -c "%s" "$tarfile")

    echo -e "name\tcompress\tdecompress\tratio"

    for prog in "${COMPRESSORS[@]}"; do
        comp_file="$tarfile.$prog"

        case "$prog" in
            gzip)
                COMP_CMD=(gzip -k "$tarfile")           
                DECOMP_CMD=(gzip -dk "$comp_file")        
                ;;
            bzip2)
                COMP_CMD=(bzip2 -k "$tarfile")
                DECOMP_CMD=(bzip2 -dk "$comp_file")
                ;;
            xz)
                COMP_CMD=(xz -k "$tarfile")
                DECOMP_CMD=(xz -dk "$comp_file")
                ;;
            zstd)
                COMP_CMD=(zstd -k -q "$tarfile")
                DECOMP_CMD=(zstd -d -q "$comp_file")
                ;;
            lz4)
                COMP_CMD=(lz4 -q -f "$tarfile" "$comp_file")
                DECOMP_CMD=(lz4 -d -q "$comp_file" "$tarfile")
                ;;
            7z)
                COMP_CMD=(7z a -bd -y "$comp_file" "$tarfile")
                DECOMP_CMD=(7z x -bd -y "$comp_file" -o"$tmp_dir/decomp")
                ;;
        esac

        comp_time=$(measure_time "${COMP_CMD[@]}")

        if [ "$prog" != "lz4" ] && [ "$prog" != "7z" ]; then
            comp_file="$tarfile.$prog"
        fi

        comp_size=$(stat -c "%s" "$comp_file")

        decomp_time=$(measure_time "${DECOMP_CMD[@]}")

        ratio=$(echo "scale=3; 100 * $comp_size / $orig_size" | bc -l)

        printf "%s\t%f\t%f\t%.1f%%\n" "$prog" "$comp_time" "$decomp_time" "$ratio"

        rm -f "$comp_file"
        rm -rf "$tmp_dir/decomp" 2>/dev/null || true
        rm -f "$tarfile" 2>/dev/null || true

        [ ! -f "$tarfile" ] && tar cf "$tarfile" "$DIR"
    done

    rm -rf "$tmp_dir"
    echo
done
