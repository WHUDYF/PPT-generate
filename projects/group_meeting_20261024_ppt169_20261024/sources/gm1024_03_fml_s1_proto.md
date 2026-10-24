# Minimal prototype: curryGPU S1 head FIFO as an FML structure IR (2026-10-23)

Goal: check that FML can carry the executable structure IR in curryGPU's `document/2026-10-14-structure-ir-spec.md`, using the smallest real case: the G2 first-round failure. This is §6 of the spec, with FML as the carrier.

Scope: control logic of S1 (`subcore_decode.v`) only. The work is done in this directory. curryGPU's working tree and `.build` are not touched (other sessions are working there).

## Materials

| Item | Source |
|---|---|
| G1 RTL | curryGPU `8c17f5d73:rtl/src/subcore_decode.v` (single-entry head) |
| G2a RTL | curryGPU `6e71a8d31:rtl/src/subcore_decode.v` (2-entry FIFO + one-cycle mask of the warp just issued) |
| G2 RTL | **Derived**: G2a with the mask line removed (`rtl/g2`). The original G2 first-round file (sha `af7096db…`) no longer exists. This file has the same behaviour but is not the same file |
| Other RTL | `ctx_hold_reg` / `ctx_reg_scan` / `subcore_decode_field` / `rtl/include` from `8c17f5d73`. `rtl/gen` (generated decode headers, not in git) is copied from the current curryGPU |
| ITS delayed advance | `subcore_top.v` `sched_issue_valid_q` → `its_cbu_advance_*` → `its_min_pc_tree.v` `selected_pc_q` (`8c17f5d73`) |

## Files

| Path | Content |
|---|---|
| `model/src/s1.rs` | FML S1: all three variants. Registers `S1Regs` are written only by `commit`. Outputs `HeadView`/`IbReq` are written only by `view`, from the registers as they were (curr) and this cycle's inputs (`'latest`) |
| `model/src/closed.rs` | Experiment A: closed loop of S1 + abstract S2 (greedy, random stalls) + IB + ITS PC registers, plus the contract monitor |
| `model/src/replay.rs` | Experiment B: replays the boundary inputs recorded from the RTL into the FML S1 and compares outputs cycle by cycle |
| `model/src/comb.rs` | Experiment C: two ways to write the G2 first-round "`refill_req` uses `issue_sel` combinationally" |
| `rules/stage_rules.py` | Experiment C: the structure rule "a backward signal must go through a register", checked on the FML IR (`.fasm`) |
| `tb/tb.cpp`, `tb/build.sh` | Verilator testbench running S1 alone (random IB occupancy, flush, ctx_hold, an S2 that prefers back-to-back issue). Records every input and output each cycle |
| `run_lockstep.sh` | Experiment B: 3×3 matrix |
| `runs/lockstep-matrix.txt` | Raw output of experiment B |

## Experiment A: contracts on the IR

Two contracts are checked by a read-only monitor at every issue:

- **C1** (structure-specific, implicit in G1, never written down): the same warp issues at most once every 2 cycles.
- **C2** (what C1 protects): at issue, ITS `selected_pc` equals the PC of the instruction being issued. The PC is a ghost field carried by the head; the RTL does not have it.

10⁶ cycles, 1 worker, about 3 s per run (self-checks and trace check enabled):

| ctx_hold rate | G1 C1/C2 | **G2 C1** | **G2 C2** | G2a C1/C2 |
|---|---|---|---|---|
| 0% | 0 / 0 | 328177 | 328177 | 0 / 0 |
| 1% | 0 / 0 | 317871 | 321244 | 0 / 0 |
| 5% | 0 / 0 | 281464 | 296490 | 0 / 0 |

- G2 is caught at **cycle 48**: warp 15 issues at cycles 47 and 48, the instruction issued is pc 2, and ITS still says pc 1. This is the same kind of event as the RTL waveform evidence (`refill-fixed/issue-summary.json`: cycles 328288/328289 both at PC 8).
- For comparison, the G2 first round in RTL: model build 623 s, iadd3 end-to-end **PASS** (missed); mix / control_flow showed only output mismatches at the end, with no first faulty instruction.
- **New finding: the hand-written C1 is imprecise.** With no hold, C1 ≡ C2. With hold, C2 catches more. Cause: an issue followed by a ctx_hold freezes ITS, so even with a gap of 2 cycles the PC is still stale. The precise contract is "a gap of at least 2 **non-hold** cycles", or C2 directly. G2a's mask uses `issue_valid_q`, which also freezes during hold, so G2a is correct in both cases.
- Determinism: 8 workers and 1 worker give identical counts (8 workers are slower on this tiny model: 8.4 s vs 3.1 s).

## Experiment B: FML vs RTL lockstep

The Verilator testbench records the RTL's boundary inputs each cycle. The FML S1 replays them and compares `ib_issue_valid_o`, `ib_issue_warp_o`, `head_valid_o`, the issued head's `head_instr_o`, and `trap_valid/cause/warp_o`. The decoder is datapath and is not ported: `refill_cause` is supplied from the RTL as an oracle.

5 seeds × 200,000 cycles. Each run covers about 160k issues, flushes, ctx_holds and about 30k traps:

| FML \ RTL | g1 | g2 | g2a |
|---|---|---|---|
| G1 | **5/5 identical** | diverges at cycles 10–49 | diverges at cycles 10–49 |
| G2 | diverges at cycles 10–49 | **5/5 identical** | diverges at cycles 14–54 |
| G2a | diverges at cycles 10–49 | diverges at cycles 14–54 | **5/5 identical** |

Off-diagonal runs report the first diverging cycle and signal, for example `cycle 30: head_valid_o: model 7609, RTL 5609`. The difference is exactly the masked warp.

## Experiment C: what the load-time check catches, and what it doesn't

The G2 first round had a second defect: `refill_req` used this cycle's `issue_sel`, which violates the spec rule "rdy may only come from the next stage's ena, a constant or a register".

| Way of writing it | FML load | `stage_rules.py` |
|---|---|---|
| S1 outputs in one task | **Rejected**: `dependency cycle … S1.view → S2.pick → S1.view` | — |
| Split into `view_heads` + `view_refill` (true to the RTL's wiring) | Loads | **VIOLATION**: `Split.view_refill drives Split.ib_req from S2.issue of stage 2 ('latest)` |
| G1/G2/G2a closed loop | Loads | 0 violations |

Conclusion: FML's built-in check is a **combinational loop check at task granularity**. Putting unrelated outputs in one task can cause false positives. Stage rules are not checked automatically, but the IR has everything they need (each column read curr/latest, plus writers). A 40-line rule layer is enough.

## What this shows and what it doesn't

Shows:
1. FML can write S1's control as **cycle-exact with the RTL**: 15 × 200k cycles fully identical, in about 250 lines (the RTL is 536 lines, most of it decode datapath). The register/wire mapping comes directly from curr/`'latest`.
2. Contracts can be written as read-only monitors. They catch the G2 failure on the IR at **cycle 48, within a second**, and pin it to the warp and PC.
3. Lockstep can localize a diverging RTL change to the first cycle and signal.
4. Writing contracts down exposes imprecise ones (C1 under hold).

Doesn't show:
- S2, ITS and IB in experiment A are abstract. They are not cycle-exact with the RTL; ITS keeps only the PC advance path.
- Stimuli are random, not real kernels. G2 RTL is derived (see Materials).
- Decoded fields (target/opcode/…) are not compared. The decoder is an oracle.
- No RTL is generated from FML. Only "FML as an executable spec + lockstep against RTL" is verified.

## Friction (input for the "RTL-able subset" rules)

- The eval/commit split ("view tasks write wires, commit writes registers") is a manual convention. It should become a checkable subset rule.
- Fixed-length arrays in module fields are treated as columns. They have to be wrapped in a `Plain` struct (`PerWarp`, `S1Regs`).
- No bit widths: `u8`/`u16`/`u128` are only containers. Field widths (HEAD_BITS) are not exact.
- Ghost fields (`Entry::pc`) need a marker so they never lower to RTL.
- Stage information is not in the IR. Right now it is passed on the command line (`Split=1 S2=2`) and should become an annotation.

## Reproducing

```sh
export PATH=$HOME/.cargo/bin:$PATH CC=/home/dyf/miniconda3/envs/pytorchsim-build/bin/x86_64-conda-linux-gnu-gcc
for v in g1 g2 g2a; do tb/build.sh $v; done
(cd model && cargo build --release)
M=model/target/release/s1-proto
$M closed g2 1000000 1 1 1          # A: variant, cycles, seed, workers, hold %
./run_lockstep.sh 200000 1 2 3 4 5  # B
$M comb                              # C: load checks
$M program split > runs/split.fasm && python3 -I rules/stage_rules.py runs/split.fasm Split=1 S2=2
```

The Rust toolchain was installed for this experiment with `rustup --no-modify-path` (`~/.rustup`, `~/.cargo`, 1.99.1). FML builds with one deprecation warning.
