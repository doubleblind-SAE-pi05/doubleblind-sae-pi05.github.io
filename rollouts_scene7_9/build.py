"""Build a self-contained, downloadable page with every layer-5 swap rollout in the mirror scenes 7 and 9.

Per scene: the unchanged policy (10 rollouts) and the layer-5 BatchTopK swap (20 rollouts), each video labelled
with the graded outcome. Copies the videos next to the page and zips the folder:

    python reports/rollouts_scene7_9/build.py        # from the repo root -> reports/rollouts_scene7_9.zip

Conditions (the best-working layer-5 selection in each scene, Table 1 of the paper):
  scene 7: word-selected 16 + 16 swap (ws3b_n20)                  15/20 do prompt B's task
  scene 9: contrastive 64-feature swap (ws3e + top-up, states 0-19) 18/20
"""
import html
import json
import pathlib
import shutil

P = pathlib.Path("/path/to/data")
OUT = pathlib.Path(__file__).resolve().parent
VID = OUT / "videos"

SCENES = [
    {
        "id": 7, "own": "stove", "other": "wooden cabinet",
        "prompt": "pick up the black bowl on the <b>stove</b> and place it on the plate",
        "base": P / "ablation_multilayer_memorized/libero_spatial_task7_5893633",
        "edit": "16 SAE “stove” features ablated, 16 “cabinet” features added, layer 5",
        "runs": [(P / "ws3b_n20/libero_spatial_task7_5972884", "batchtopk_swap_k16+16_L5", P / "ws3b_n20/graded_b_success.json")],
        "random": "16 random features: 2, 1, 0 of 20 (3 seeds)",
    },
    {
        "id": 9, "own": "wooden cabinet", "other": "stove",
        "prompt": "pick up the black bowl on the <b>wooden cabinet</b> and place it on the plate",
        "base": P / "ablation_multilayer_memorized/libero_spatial_task9_5893456",
        "edit": "64 SAE features moved from “cabinet” to “stove” levels (contrastive selection), layer 5",
        "runs": [(P / "ws3e_contrastive/libero_spatial_task9_5973532", "batchtopk_contrastive_k64_L5", P / "ws3e_contrastive/graded_b_success.json"),
                 (P / "ws3e_contrastive_topup/libero_spatial_task9_5999029", "batchtopk_contrastive_k64_L5", P / "ws3e_contrastive_topup/graded_b_success.json")],
        "random": "16 random features: 0, 0, 0 of 20 (3 seeds)",
    },
]


def video(run, cond, ep):
    return next((run / cond).glob(f"ep{ep}_*.mp4"))


def tile(src, label, cls):
    return (f'<figure class="t {cls}"><video src="{src}" muted loop playsinline preload="metadata" controls></video>'
            f"<figcaption>{label}</figcaption></figure>")


if VID.exists():
    shutil.rmtree(VID)
VID.mkdir(parents=True)
sections = []
for sc in SCENES:
    s = sc["id"]
    # unchanged policy: its own task (the baseline run logs no second bowl, so it is graded by LIBERO's own success)
    res = json.load(open(sc["base"] / "results.json"))
    eps = next(c for c in res["conditions"] if c["name"] == "baseline")["episodes"]
    base_tiles = []
    for e in eps:
        name = f"s{s}_unchanged_{e['episode']}.mp4"
        shutil.copy(video(sc["base"], "baseline", e["episode"]), VID / name)
        ok = e["success"]
        base_tiles.append(tile(f"videos/{name}", f"#{e['episode']} · {'bowl on the ' + sc['own'] if ok else 'failed'}", "own" if ok else "none"))
    n_base = sum(e["success"] for e in eps)

    swap_tiles, n_b, n = [], 0, 0
    for run, cond, graded in sc["runs"]:
        g = json.load(open(graded))[run.name][cond]
        for e in g["episodes"]:
            ep = str(e["ep"])
            idx = int(ep.split("_")[0])
            name = f"s{s}_swap_{idx}.mp4"
            shutil.copy(video(run, cond, ep), VID / name)
            if e["b_success"]:
                lab, cls = f"bowl on the {sc['other']} ✓", "other"
            elif e["a_success"]:
                lab, cls = f"bowl on the {sc['own']}", "own"
            else:
                lab, cls = "neither bowl placed", "none"
            swap_tiles.append((idx, tile(f"videos/{name}", f"#{idx} · {lab}", cls)))
            n_b += bool(e["b_success"])
            n += 1
    swap_tiles = [t for _, t in sorted(swap_tiles)]

    sections.append(f"""
  <section>
    <h2>Scene {s}</h2>
    <p class="prompt">Prompt: “{sc['prompt']}”</p>
    <h3>π<sub>0.5</sub>-LIBERO unchanged <span>· picks up the bowl on the {sc['own']}: <b>{n_base}/{len(eps)}</b></span></h3>
    <div class="grid">{''.join(base_tiles)}</div>
    <h3><em>{html.escape(sc['edit'])}</em> <span>· picks up the bowl on the {sc['other']} instead: <b>{n_b}/{n}</b> · {sc['random']}</span></h3>
    <div class="grid">{''.join(swap_tiles)}</div>
  </section>""")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Layer-5 Swap Rollouts</title>
<style>
:root{{color-scheme:light;--bg:#fbfbfa;--ink:#1c1f24;--muted:#5d6470;--rule:#d9dce1;--hl:#667396;--ok:#2f7d5b;--own:#8a6d2c}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;padding:32px 16px 64px}}
main{{max-width:1180px;margin:0 auto}}
h1{{font-size:24px;margin:0 0 6px}}
.lede{{color:var(--muted);margin:0 0 8px;max-width:820px}}
.bar{{display:flex;gap:10px;align-items:center;margin:14px 0 8px}}
button{{font:inherit;padding:5px 12px;border:1px solid var(--rule);background:#fff;border-radius:5px;cursor:pointer}}
button:hover{{border-color:var(--muted)}}
section{{border-top:1px solid var(--rule);margin-top:26px;padding-top:6px}}
h2{{font-size:20px;margin:12px 0 2px}}
.prompt{{margin:0 0 10px}}
h3{{font-size:15px;font-weight:600;margin:18px 0 8px}}
h3 em{{font-style:normal;color:var(--hl)}}
h3 span{{font-weight:400;color:var(--muted)}}
h3 b{{color:var(--ink)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}}
.t{{margin:0}}
.t video{{display:block;width:100%;aspect-ratio:1;background:#000;border-radius:4px;border:2px solid transparent}}
.t figcaption{{font-size:12.5px;color:var(--muted);margin-top:3px}}
.t.other video{{border-color:var(--hl)}}
.t.other figcaption{{color:var(--hl);font-weight:600}}
.t.none figcaption{{color:#a33}}
</style></head><body><main>
<h1>Layer-5 word swap: every rollout, scenes 7 and 9</h1>
<p class="lede">π<sub>0.5</sub> fine-tuned on LIBERO-Spatial. In each scene the robot reads its own prompt; in the swap runs, SAE features at the
landmark word are edited after PaliGemma layer 5 so that the word looks like the other scene's landmark. The instruction
text is never changed. Outcomes are graded from logged object positions (bowl on the plate); blue borders mark rollouts
that took the other bowl. Same start states across runs (numbers are LIBERO initial-state ids).</p>
<div class="bar"><button id="play">Play all</button><button id="pause">Pause all</button></div>
{''.join(sections)}
</main>
<script>
const vids = [...document.querySelectorAll("video")];
document.getElementById("play").onclick = () => vids.forEach(v => v.play().catch(() => {{}}));
document.getElementById("pause").onclick = () => vids.forEach(v => v.pause());
</script>
</body></html>"""
(OUT / "index.html").write_text(page)
zip_path = shutil.make_archive(str(OUT.parent / OUT.name), "zip", OUT.parent, OUT.name)
print("wrote", OUT / "index.html", "and", zip_path, f"({len(list(VID.iterdir()))} videos)")
