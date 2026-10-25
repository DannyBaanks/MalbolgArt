/* Malbolge Classic Trace & Geometry Extractor
 * Compatible with Ben Olmstead specification and BolgeForge mb_ref.c
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>
#include <openssl/sha.h>
#include <sys/time.h>

#define N 59049
#define NONE 65535

static const char xlat1[] = "+b(29e*j1VMEKLyC})8&m#~W>qxdRp0wkrUo[D7,XTcA\"lI.v%{gJh4G\\-=O@5`_3i<?Z';FNQuY]szf$!BS/|t:Pn6^Ha";
static const char xlat2[] = "5z]&gqtyfr$(we4{WP)H-Zn,[%\\3dL+Q;>U!pJS72FhOA1CB6v^=I_0/8|jsb9m<.TVac`uY*MK'X~xDl}REokN:#?G\"i@";

static inline unsigned short op(unsigned short x, unsigned short y) {
    unsigned short i = 0;
    static const unsigned short p9[5] = { 1, 9, 81, 729, 6561 };
    static const unsigned short o[9][9] = {
        { 4, 3, 3, 1, 0, 0, 1, 0, 0 },
        { 4, 3, 5, 1, 0, 2, 1, 0, 2 },
        { 5, 5, 4, 2, 2, 1, 2, 2, 1 },
        { 4, 3, 3, 1, 0, 0, 7, 6, 6 },
        { 4, 3, 5, 1, 0, 2, 7, 6, 8 },
        { 5, 5, 4, 2, 2, 1, 8, 8, 7 },
        { 7, 6, 6, 7, 6, 6, 4, 3, 3 },
        { 7, 6, 8, 7, 6, 8, 4, 3, 5 },
        { 8, 8, 7, 8, 8, 7, 5, 5, 4 },
    };
    for (int j = 0; j < 5; j++)
        i += o[y / p9[j] % 9][x / p9[j] % 9] * p9[j];
    return i;
}

typedef struct {
    uint64_t c_visits;
    uint64_t d_visits;
    uint64_t writes;
    uint64_t reads;
    uint64_t encryptions;
    uint64_t first_c_step;
    uint64_t first_d_step;
    uint16_t initial_val;
    uint16_t final_val;
} CellStat;

static CellStat cell_stats[N];
static uint16_t mem[N];
static uint16_t initial_mem[N];

static void hash_to_hex(const unsigned char *hash, char *out) {
    for (int i = 0; i < 32; i++) {
        sprintf(out + (i * 2), "%02x", hash[i]);
    }
    out[64] = 0;
}

int main(int argc, char **argv) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <program.mal> <max_steps> <out_dir> [sample_target_count]\n", argv[0]);
        return 1;
    }

    const char *prog_path = argv[1];
    unsigned long long max_steps = strtoull(argv[2], NULL, 10);
    const char *out_dir = argv[3];
    unsigned long long target_samples = 4000;
    if (argc >= 5) {
        target_samples = strtoull(argv[4], NULL, 10);
    }

    /* Compute program SHA256 */
    FILE *f_prog = fopen(prog_path, "rb");
    if (!f_prog) {
        fprintf(stderr, "Cannot open %s\n", prog_path);
        return 1;
    }
    SHA256_CTX prog_sha_ctx;
    SHA256_Init(&prog_sha_ctx);
    unsigned char prog_buf[4096];
    size_t nr;
    size_t prog_file_size = 0;
    while ((nr = fread(prog_buf, 1, sizeof(prog_buf), f_prog)) > 0) {
        SHA256_Update(&prog_sha_ctx, prog_buf, nr);
        prog_file_size += nr;
    }
    fclose(f_prog);
    unsigned char prog_hash[32];
    SHA256_Final(prog_hash, &prog_sha_ctx);
    char prog_sha256[65];
    hash_to_hex(prog_hash, prog_sha256);

    /* Load program into mem */
    FILE *f = fopen(prog_path, "rb");
    unsigned int loaded_len = 0;
    int x;
    while ((x = fgetc(f)) != EOF) {
        if (isspace(x)) continue;
        if (x < 33 || x > 126) {
            fprintf(stderr, "INVALID_CHAR: 0x%02x\n", x);
            fclose(f);
            return 1;
        }
        if (loaded_len == N) {
            fprintf(stderr, "PROGRAM_TOO_LONG\n");
            fclose(f);
            return 1;
        }
        char dec = xlat1[(x - 33 + loaded_len) % 94];
        if (!strchr("ji*p</vo", dec)) {
            fprintf(stderr, "INVALID_OPCODE: cell %u char %c\n", loaded_len, x);
            fclose(f);
            return 1;
        }
        mem[loaded_len++] = (unsigned short)x;
    }
    fclose(f);

    if (loaded_len < 2) {
        fprintf(stderr, "TOO_SHORT\n");
        return 1;
    }

    for (unsigned int i = loaded_len; i < N; i++) {
        mem[i] = op(mem[i - 1], mem[i - 2]);
    }
    for (unsigned int i = 0; i < N; i++) {
        initial_mem[i] = mem[i];
        cell_stats[i].initial_val = mem[i];
    }

    /* Allocate pair bitset: 59049 * 59049 / 8 = 435,827,851 bytes */
    uint64_t total_pairs = (uint64_t)N * N;
    size_t bitset_size = (total_pairs + 7) / 8;
    unsigned char *pair_bitset = (unsigned char *)calloc(bitset_size, 1);
    if (!pair_bitset) {
        fprintf(stderr, "WARNING: failed to allocate pair bitset, pair tracking disabled\n");
    }

    char out_path[4096];
    snprintf(out_path, sizeof(out_path), "%s/stdout.bin", out_dir);
    FILE *f_stdout = fopen(out_path, "wb");
    if (!f_stdout) {
        fprintf(stderr, "Cannot open %s for writing\n", out_path);
        if (pair_bitset) free(pair_bitset);
        return 1;
    }

    snprintf(out_path, sizeof(out_path), "%s/trace_sample.json", out_dir);
    FILE *f_sample = fopen(out_path, "w");
    if (!f_sample) {
        fprintf(stderr, "Cannot open %s for writing\n", out_path);
        fclose(f_stdout);
        if (pair_bitset) free(pair_bitset);
        return 1;
    }
    fprintf(f_sample, "[\n");

    /* Execution state */
    unsigned short a = 0, c = 0, d = 0;
    unsigned long long step = 0;
    const char *status = "RUNNING";
    unsigned long long op_counts[94] = {0};
    unsigned long long opcode_named_counts[256] = {0};

    uint64_t breaks_i = 0, breaks_j = 0, breaks_other = 0;
    uint64_t diagonal_steps = 0;
    uint64_t cur_seglen = 0, max_seglen = 0, total_segments = 1;
    uint64_t unique_pairs = 0, pair_revisits = 0;
    uint64_t simultaneous_c_eq_d = 0;
    uint64_t c_wrap_count = 0, d_wrap_count = 0;
    uint64_t total_reads = 0, total_writes = 0, total_encryptions = 0;
    uint64_t inputs_count = 0, outputs_count = 0;
    uint64_t delta_freq[N] = {0};

    /* Event stream hashing */
    SHA256_CTX event_sha_ctx;
    SHA256_Init(&event_sha_ctx);
    unsigned char event_buf[32 * 1024];
    size_t event_bp = 0;

    /* Stdout hashing */
    SHA256_CTX stdout_sha_ctx;
    SHA256_Init(&stdout_sha_ctx);

    /* Sample interval determination */
    /* If max_steps > 100000, we sample periodically so we get ~target_samples,
     * plus always sampling first 500 steps, last steps, and all output steps. */
    unsigned long long sample_interval = 1;
    if (max_steps > target_samples) {
        sample_interval = max_steps / target_samples;
        if (sample_interval == 0) sample_interval = 1;
    }
    int sample_comma = 0;
    uint64_t emitted_samples = 0;

    struct timeval tv_start, tv_end;
    gettimeofday(&tv_start, NULL);

    while (step < max_steps) {
        if (mem[c] < 33 || mem[c] > 126) {
            status = "NONPRINTABLE_PC";
            break;
        }

        uint16_t olda = a;
        uint16_t oldc = c;
        uint16_t oldd = d;
        uint16_t cell_val = mem[c];
        char instr = xlat1[(cell_val - 33 + c) % 94];
        unsigned int op_idx = (cell_val + c) % 94;
        op_counts[op_idx]++;
        opcode_named_counts[(unsigned char)instr]++;

        if (cell_stats[c].c_visits++ == 0) cell_stats[c].first_c_step = step + 1;
        if (cell_stats[d].d_visits++ == 0) cell_stats[d].first_d_step = step + 1;
        if (c == d) simultaneous_c_eq_d++;

        if (pair_bitset) {
            uint64_t pi = (uint64_t)c * N + d;
            unsigned char mask = 1u << (pi % 8);
            if (pair_bitset[pi / 8] & mask) {
                pair_revisits++;
            } else {
                pair_bitset[pi / 8] |= mask;
                unique_pairs++;
            }
        }

        uint16_t operand = mem[d];
        uint16_t direct_write = NONE;

        if (instr == 'j' || instr == 'i' || instr == '*' || instr == 'p') {
            total_reads++;
            cell_stats[d].reads++;
        }

        if (instr == 'j') {
            d = mem[d];
        } else if (instr == 'i') {
            c = mem[d];
        } else if (instr == '*') {
            direct_write = operand / 3 + (operand % 3) * 19683;
            a = mem[d] = direct_write;
        } else if (instr == 'p') {
            direct_write = op(a, operand);
            a = mem[d] = direct_write;
        } else if (instr == '<') {
            int byte_out = (int)(a & 255);
            fputc(byte_out, f_stdout);
            unsigned char ch = (unsigned char)byte_out;
            SHA256_Update(&stdout_sha_ctx, &ch, 1);
            outputs_count++;
        } else if (instr == '/') {
            int in_ch = getchar();
            a = (in_ch == EOF) ? 59048 : (unsigned short)in_ch;
            inputs_count++;
        } else if (instr == 'v') {
            status = "HALTED";
            /* Record sample of HALT step */
            if (sample_comma) fprintf(f_sample, ",\n");
            fprintf(f_sample, "  {\"step\": %llu, \"a\": %u, \"c\": %u, \"d\": %u, \"op\": \"%c\", \"cell\": %u, \"operand\": %u, \"write\": null, \"enc_addr\": null, \"enc_val\": null, \"next_c\": %u, \"next_d\": %u, \"delta\": %u}",
                    step, olda, oldc, oldd, instr, cell_val, operand, oldc, oldd, (oldc + N - oldd) % N);
            emitted_samples++;
            break;
        }

        if (direct_write != NONE) {
            total_writes++;
            cell_stats[oldd].writes++;
        }

        /* Encryption step */
        if (mem[c] < 33 || mem[c] > 126) {
            status = "INVALID_ENCRYPTION";
            break;
        }
        uint16_t enc_addr = c;
        uint16_t enc_before = mem[c];
        uint16_t enc_after = (unsigned short)xlat2[enc_before - 33];
        mem[c] = enc_after;
        cell_stats[c].encryptions++;
        total_encryptions++;

        if (c == N - 1) c_wrap_count++;
        if (d == N - 1) d_wrap_count++;

        uint16_t next_c = (c == 59048) ? 0 : c + 1;
        uint16_t next_d = (d == 59048) ? 0 : d + 1;
        c = next_c;
        d = next_d;
        step++;

        unsigned int cur_delta = (oldc + N - oldd) % N;
        unsigned int next_delta = (c + N - d) % N;
        delta_freq[cur_delta]++;

        if (next_delta == cur_delta) {
            diagonal_steps++;
            cur_seglen++;
        } else {
            if (instr == 'i') breaks_i++;
            else if (instr == 'j') breaks_j++;
            else breaks_other++;
            total_segments++;
            if (cur_seglen > max_seglen) max_seglen = cur_seglen;
            cur_seglen = 0;
        }

        /* Canonical 32-byte event digest update */
        /* Record: u64 step, u16 olda, oldc, oldd, cell_val, instr, operand, direct_write, enc_addr, enc_before, enc_after, c, d */
        unsigned char rec[32];
        for (int b = 0; b < 8; b++) rec[b] = (unsigned char)(step >> (8 * b));
        uint16_t rvals[12] = {olda, oldc, oldd, cell_val, (uint16_t)instr, operand, direct_write, enc_addr, enc_before, enc_after, c, d};
        for (int j = 0; j < 12; j++) {
            rec[8 + 2 * j] = (unsigned char)(rvals[j] & 0xFF);
            rec[9 + 2 * j] = (unsigned char)(rvals[j] >> 8);
        }
        memcpy(event_buf + event_bp, rec, 32);
        event_bp += 32;
        if (event_bp == sizeof(event_buf)) {
            SHA256_Update(&event_sha_ctx, event_buf, event_bp);
            event_bp = 0;
        }

        /* Sampling decision */
        int do_sample = 0;
        if (step <= 1000) do_sample = 1;
        else if (instr == '<') do_sample = 1;
        else if (step % sample_interval == 0 && emitted_samples < target_samples * 2) do_sample = 1;

        if (do_sample) {
            if (sample_comma) fprintf(f_sample, ",\n");
            if (direct_write == NONE) {
                fprintf(f_sample, "  {\"step\": %llu, \"a\": %u, \"c\": %u, \"d\": %u, \"op\": \"%c\", \"cell\": %u, \"operand\": %u, \"write\": null, \"enc_addr\": %u, \"enc_val\": %u, \"next_c\": %u, \"next_d\": %u, \"delta\": %u}",
                        step - 1, olda, oldc, oldd, instr, cell_val, operand,
                        enc_addr, enc_after, c, d, cur_delta);
            } else {
                fprintf(f_sample, "  {\"step\": %llu, \"a\": %u, \"c\": %u, \"d\": %u, \"op\": \"%c\", \"cell\": %u, \"operand\": %u, \"write\": %u, \"enc_addr\": %u, \"enc_val\": %u, \"next_c\": %u, \"next_d\": %u, \"delta\": %u}",
                        step - 1, olda, oldc, oldd, instr, cell_val, operand, direct_write,
                        enc_addr, enc_after, c, d, cur_delta);
            }
            sample_comma = 1;
            emitted_samples++;
        }
    }

    gettimeofday(&tv_end, NULL);
    double elapsed_sec = (tv_end.tv_sec - tv_start.tv_sec) + (tv_end.tv_usec - tv_start.tv_usec) / 1000000.0;

    if (strcmp(status, "HALTED") != 0 && step >= max_steps) {
        status = "MAX_STEPS";
    }

    if (cur_seglen > max_seglen) max_seglen = cur_seglen;

    /* Flush event SHA */
    if (event_bp > 0) {
        SHA256_Update(&event_sha_ctx, event_buf, event_bp);
    }
    unsigned char event_hash[32];
    SHA256_Final(event_hash, &event_sha_ctx);
    char event_sha256[65];
    hash_to_hex(event_hash, event_sha256);

    /* Flush stdout SHA */
    fclose(f_stdout);
    unsigned char stdout_hash[32];
    SHA256_Final(stdout_hash, &stdout_sha_ctx);
    char stdout_sha256[65];
    hash_to_hex(stdout_hash, stdout_sha256);

    /* Close sample JSON */
    fprintf(f_sample, "\n]\n");
    fclose(f_sample);

    /* Record final cell memory values */
    for (unsigned int i = 0; i < N; i++) {
        cell_stats[i].final_val = mem[i];
    }

    /* Compute set memberships and counts */
    uint64_t vc = 0, vd = 0, v_inter = 0, v_union = 0;
    uint64_t unvisited_count = 0;
    uint64_t d_minus_c_count = 0;
    uint64_t c_minus_d_count = 0;
    uint64_t mutated_cells = 0;

    unsigned char c_visited[N] = {0};
    for (unsigned int i = 0; i < N; i++) {
        int has_c = (cell_stats[i].c_visits > 0);
        int has_d = (cell_stats[i].d_visits > 0);
        c_visited[i] = has_c;
        if (has_c) vc++;
        if (has_d) vd++;
        if (has_c && has_d) v_inter++;
        if (has_c || has_d) v_union++;
        else unvisited_count++;
        if (has_d && !has_c) d_minus_c_count++;
        if (has_c && !has_d) c_minus_d_count++;
        if (cell_stats[i].initial_val != cell_stats[i].final_val) mutated_cells++;
    }

    /* Compute cyclic period of C footprint */
    unsigned int c_period = N;
    for (unsigned int p = 1; p <= N; p *= 3) {
        int matches = 1;
        for (unsigned int j = p; j < N; j++) {
            if (c_visited[j] != c_visited[j % p]) {
                matches = 0;
                break;
            }
        }
        if (matches) {
            c_period = p;
            break;
        }
    }

    /* Write linear_memory.csv */
    snprintf(out_path, sizeof(out_path), "%s/linear_memory.csv", out_dir);
    FILE *f_linear = fopen(out_path, "w");
    if (f_linear) {
        fprintf(f_linear, "address,c_visits,d_visits,writes,reads,encryptions,initial_val,final_val,mutated,first_c_step,first_d_step\n");
        for (unsigned int i = 0; i < N; i++) {
            fprintf(f_linear, "%u,%llu,%llu,%llu,%llu,%llu,%u,%u,%d,%llu,%llu\n",
                    i, cell_stats[i].c_visits, cell_stats[i].d_visits,
                    cell_stats[i].writes, cell_stats[i].reads, cell_stats[i].encryptions,
                    cell_stats[i].initial_val, cell_stats[i].final_val,
                    (cell_stats[i].initial_val != cell_stats[i].final_val ? 1 : 0),
                    cell_stats[i].first_c_step, cell_stats[i].first_d_step);
        }
        fclose(f_linear);
    }

    /* Write geometry_metrics.json */
    snprintf(out_path, sizeof(out_path), "%s/geometry_metrics.json", out_dir);
    FILE *f_geom = fopen(out_path, "w");
    if (f_geom) {
        double diag_frac = (step > 0) ? (double)diagonal_steps / (double)step : 0.0;
        double theoretical_diag_frac = (step > 1) ? (double)(step - 1 - breaks_i - breaks_j) / (double)step : 0.0;
        fprintf(f_geom, "{\n");
        fprintf(f_geom, "  \"status\": \"%s\",\n", status);
        fprintf(f_geom, "  \"steps\": %llu,\n", step);
        fprintf(f_geom, "  \"wall_time_sec\": %.6f,\n", elapsed_sec);
        fprintf(f_geom, "  \"program_sha256\": \"%s\",\n", prog_sha256);
        fprintf(f_geom, "  \"event_sha256\": \"%s\",\n", event_sha256);
        fprintf(f_geom, "  \"stdout_sha256\": \"%s\",\n", stdout_sha256);
        fprintf(f_geom, "  \"loaded_len\": %u,\n", loaded_len);
        fprintf(f_geom, "  \"output_len\": %llu,\n", outputs_count);
        fprintf(f_geom, "  \"input_len\": %llu,\n", inputs_count);
        fprintf(f_geom, "  \"visited_c\": %llu,\n", vc);
        fprintf(f_geom, "  \"visited_d\": %llu,\n", vd);
        fprintf(f_geom, "  \"intersection_c_d\": %llu,\n", v_inter);
        fprintf(f_geom, "  \"union_c_d\": %llu,\n", v_union);
        fprintf(f_geom, "  \"unvisited\": %llu,\n", unvisited_count);
        fprintf(f_geom, "  \"d_minus_c\": %llu,\n", d_minus_c_count);
        fprintf(f_geom, "  \"c_minus_d\": %llu,\n", c_minus_d_count);
        fprintf(f_geom, "  \"mutated_cells\": %llu,\n", mutated_cells);
        fprintf(f_geom, "  \"total_reads\": %llu,\n", total_reads);
        fprintf(f_geom, "  \"total_writes\": %llu,\n", total_writes);
        fprintf(f_geom, "  \"total_encryptions\": %llu,\n", total_encryptions);
        fprintf(f_geom, "  \"diagonal_steps\": %llu,\n", diagonal_steps);
        fprintf(f_geom, "  \"diagonal_fraction\": %.12f,\n", diag_frac);
        fprintf(f_geom, "  \"theoretical_diagonal_fraction\": %.12f,\n", theoretical_diag_frac);
        fprintf(f_geom, "  \"breaks_i\": %llu,\n", breaks_i);
        fprintf(f_geom, "  \"breaks_j\": %llu,\n", breaks_j);
        fprintf(f_geom, "  \"breaks_other\": %llu,\n", breaks_other);
        fprintf(f_geom, "  \"delta_segments\": %llu,\n", total_segments);
        fprintf(f_geom, "  \"max_segment_length\": %llu,\n", max_seglen);
        fprintf(f_geom, "  \"unique_pairs\": %llu,\n", unique_pairs);
        fprintf(f_geom, "  \"pair_revisits\": %llu,\n", pair_revisits);
        fprintf(f_geom, "  \"simultaneous_c_eq_d\": %llu,\n", simultaneous_c_eq_d);
        fprintf(f_geom, "  \"c_wrap_count\": %llu,\n", c_wrap_count);
        fprintf(f_geom, "  \"d_wrap_count\": %llu,\n", d_wrap_count);
        fprintf(f_geom, "  \"c_min_cyclic_period\": %u,\n", c_period);
        fprintf(f_geom, "  \"emitted_samples\": %llu,\n", emitted_samples);
        fprintf(f_geom, "  \"named_opcodes\": {\n");
        int op_comma = 0;
        const char *op_names = "ji*p</vo";
        for (int i = 0; i < 8; i++) {
            char ch = op_names[i];
            if (op_comma) fprintf(f_geom, ",\n");
            fprintf(f_geom, "    \"%c\": %llu", ch, opcode_named_counts[(unsigned char)ch]);
            op_comma = 1;
        }
        fprintf(f_geom, "\n  }\n");
        fprintf(f_geom, "}\n");
        fclose(f_geom);
    }

    /* Write provenance.json */
    snprintf(out_path, sizeof(out_path), "%s/provenance.json", out_dir);
    FILE *f_prov = fopen(out_path, "w");
    if (f_prov) {
        fprintf(f_prov, "{\n");
        fprintf(f_prov, "  \"program_path\": \"%s\",\n", prog_path);
        fprintf(f_prov, "  \"program_file_size\": %zu,\n", prog_file_size);
        fprintf(f_prov, "  \"program_sha256\": \"%s\",\n", prog_sha256);
        fprintf(f_prov, "  \"max_steps\": %llu,\n", max_steps);
        fprintf(f_prov, "  \"status\": \"%s\",\n", status);
        fprintf(f_prov, "  \"steps_executed\": %llu,\n", step);
        fprintf(f_prov, "  \"wall_time_sec\": %.6f,\n", elapsed_sec);
        fprintf(f_prov, "  \"environment\": \"Ubuntu 24.04 x86_64, GCC 13.x -O3\"\n");
        fprintf(f_prov, "}\n");
        fclose(f_prov);
    }

    /* Write oracle_verdict.json */
    snprintf(out_path, sizeof(out_path), "%s/oracle_verdict.json", out_dir);
    FILE *f_verd = fopen(out_path, "w");
    if (f_verd) {
        int quine_match = 0;
        if (prog_file_size == outputs_count && strcmp(status, "HALTED") == 0) {
            /* Check if byte-exact match */
            FILE *f_in = fopen(prog_path, "rb");
            FILE *f_out = fopen(out_path, "rb"); // will read stdout.bin
            snprintf(out_path, sizeof(out_path), "%s/stdout.bin", out_dir);
            f_out = fopen(out_path, "rb");
            if (f_in && f_out) {
                int same = 1;
                int b1, b2;
                while ((b1 = fgetc(f_in)) != EOF) {
                    b2 = fgetc(f_out);
                    if (b1 != b2) { same = 0; break; }
                }
                if (same && fgetc(f_out) == EOF) quine_match = 1;
                fclose(f_in);
                fclose(f_out);
            }
        }
        fprintf(f_verd, "{\n");
        fprintf(f_verd, "  \"oracle\": \"trace_extractor (Classic Olmstead strict)\",\n");
        fprintf(f_verd, "  \"status\": \"%s\",\n", status);
        fprintf(f_verd, "  \"exit_code\": %d,\n", (strcmp(status, "HALTED") == 0 ? 0 : 2));
        fprintf(f_verd, "  \"steps\": %llu,\n", step);
        fprintf(f_verd, "  \"output_bytes\": %llu,\n", outputs_count);
        fprintf(f_verd, "  \"quine_self_reproduction\": %s\n", (quine_match ? "true" : "false"));
        fprintf(f_verd, "}\n");
        fclose(f_verd);
    }

    /* Write trace_index.json */
    snprintf(out_path, sizeof(out_path), "%s/trace_index.json", out_dir);
    FILE *f_idx = fopen(out_path, "w");
    if (f_idx) {
        fprintf(f_idx, "{\n");
        fprintf(f_idx, "  \"sample_file\": \"trace_sample.json\",\n");
        fprintf(f_idx, "  \"sample_count\": %llu,\n", emitted_samples);
        fprintf(f_idx, "  \"total_steps\": %llu,\n", step);
        fprintf(f_idx, "  \"sampling_rate\": %.6f,\n", (step > 0 ? (double)emitted_samples / (double)step : 1.0));
        fprintf(f_idx, "  \"linear_memory_file\": \"linear_memory.csv\"\n");
        fprintf(f_idx, "}\n");
        fclose(f_idx);
    }

    if (pair_bitset) free(pair_bitset);

    fprintf(stderr, "%s steps=%llu output=%llu union=%llu inter=%llu diag_frac=%.6f time=%.3fs\n",
            status, step, outputs_count, v_union, v_inter,
            (step > 0 ? (double)diagonal_steps / (double)step : 0.0), elapsed_sec);

    return (strcmp(status, "HALTED") == 0 ? 0 : 2);
}
