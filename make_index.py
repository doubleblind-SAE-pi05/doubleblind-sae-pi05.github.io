"""Generate index.html from the rollout videos in rollouts_scene7_9/videos (run from the repo root)."""
import pathlib

V = "rollouts_scene7_9/videos"
SCENES = [
    dict(id=7, own="stove", other="wooden cabinet", feat=2, n_base=10,
         prompt="pick up the black bowl on the <b>stove</b> and place it on the plate",
         edit="Ablate 16 “stove” SAE features and add 16 “wooden cabinet” features (word-selected)",
         swap_ok=15, random="16 random features: 2, 1, 0 of 20 (3 seeds)",
         own_ids={1, 9, 14, 18}, none_ids={7}, base_ok=10),
    dict(id=9, own="wooden cabinet", other="stove", feat=1, n_base=10,
         prompt="pick up the black bowl on the <b>wooden cabinet</b> and place it on the plate",
         edit="Move 64 SAE features from “wooden cabinet” to “stove” levels (contrastive selection)",
         swap_ok=18, random="16 random features: 0, 0, 0 of 20 (3 seeds)",
         own_ids={0}, none_ids={13}, base_ok=10),
]


def tile(src, label, cls, cap_extra=""):
    return (f'<figure class="t {cls}"><video src="{src}" muted playsinline preload="metadata" controls></video>'
            f"<figcaption>{label}</figcaption></figure>")


def swap_label(sc, i):
    if i in sc["none_ids"]:
        return "neither bowl placed", "none"
    if i in sc["own_ids"]:
        return f"bowl on the {sc['own']}", "own"
    return f"bowl on the {sc['other']} ✓", "other"


sections = []
for sc in SCENES:
    s, f = sc["id"], sc["feat"]
    fl, fc = swap_label(sc, f)
    all_base = "".join(tile(f"{V}/s{s}_unchanged_{i}.mp4", f"#{i} · bowl on the {sc['own']}", "own") for i in range(10))
    all_swap = "".join(tile(f"{V}/s{s}_swap_{i}.mp4", f"#{i} · {swap_label(sc, i)[0]}", swap_label(sc, i)[1]) for i in range(20))
    sections.append(f"""
<section class="scene" id="scene{s}">
  <h2>Scene {s}</h2>
  <p class="prompt">Instruction (never changed): “{sc['prompt']}”</p>
  <div class="pair" data-pair>
    <figure class="hero"><video src="{V}/s{s}_unchanged_{f}.mp4" muted playsinline preload="auto"></video>
      <figcaption><span class="tag">Unchanged</span>Follows its instruction: bowl on the {sc['own']}</figcaption></figure>
    <figure class="hero swap"><video src="{V}/s{s}_swap_{f}.mp4" muted playsinline preload="auto"></video>
      <figcaption><span class="tag">SAE edit</span>{fl.replace(' ✓', '')} instead</figcaption></figure>
  </div>
  <div class="bar"><button class="play" data-play>▶ Play both</button><span class="muted">Same start state (#{f}) in both videos.</span></div>
  <div class="stats">
    <div><b>{sc['base_ok']}/{sc['n_base']}</b><span>unchanged policy picks the {sc['own']} bowl</span></div>
    <div class="hl"><b>{sc['swap_ok']}/20</b><span>with the edit, picks the {sc['other']} bowl instead</span></div>
    <div><b>control</b><span>{sc['random']}</span></div>
  </div>
  <p class="edit"><b>Edit:</b> {sc['edit']}, applied at the landmark word after PaliGemma layer 5.</p>
  <details>
    <summary>Show all rollouts (10 unchanged + 20 edited)</summary>
    <h3>Unchanged <span>· {sc['base_ok']}/{sc['n_base']} on the {sc['own']}</span></h3>
    <div class="grid">{all_base}</div>
    <h3>SAE edit <span>· {sc['swap_ok']}/20 on the {sc['other']} (blue border)</span></h3>
    <div class="grid">{all_swap}</div>
    <div class="bar"><button data-all>Play all in this scene</button><button data-stop>Pause all</button></div>
  </details>
</section>""")

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAE Word Swap Rollouts</title>
<style>
:root{{--bg:#fbfbfa;--card:#fff;--ink:#1c1f24;--muted:#5d6470;--rule:#d9dce1;--hl:#4b5d9a;--hlbg:#eef1fa;--bad:#a33}}
@media(prefers-color-scheme:dark){{:root{{--bg:#14161a;--card:#1c1f25;--ink:#e8eaee;--muted:#98a0ad;--rule:#2f343d;--hl:#8ea2e6;--hlbg:#222a44;--bad:#e58a8a}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;padding:40px 16px 72px}}
main{{max-width:1040px;margin:0 auto}}
h1{{font-size:28px;line-height:1.2;margin:0 0 10px}}
.lede{{color:var(--muted);max-width:780px;margin:0 0 20px}}
.method{{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:16px 20px;margin:0 0 8px}}
.method h2{{margin:0 0 6px;font-size:16px}}
.method ul{{margin:0;padding-left:20px}}
.method li{{margin:4px 0}}
.scene{{margin-top:36px;padding-top:8px;border-top:1px solid var(--rule)}}
h2{{font-size:22px;margin:14px 0 2px}}
.prompt{{margin:0 0 14px;color:var(--muted)}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:14px}}
.hero{{margin:0}}
.hero video{{display:block;width:100%;aspect-ratio:1;background:#000;border-radius:8px;border:3px solid transparent}}
.hero.swap video{{border-color:var(--hl)}}
.hero figcaption{{margin-top:6px;font-size:14px}}
.tag{{display:inline-block;margin-right:8px;padding:1px 9px;border-radius:99px;background:var(--rule);font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em}}
.swap .tag{{background:var(--hlbg);color:var(--hl)}}
.bar{{display:flex;gap:12px;align-items:center;margin:14px 0}}
button{{font:inherit;font-weight:600;padding:8px 18px;border:1px solid var(--hl);background:var(--hl);color:#fff;border-radius:8px;cursor:pointer}}
button[data-all],button[data-stop]{{background:var(--card);color:var(--ink);border-color:var(--rule);font-weight:500;padding:5px 12px}}
button:hover{{filter:brightness(1.1)}}
.muted{{color:var(--muted);font-size:14px}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:6px 0 10px}}
.stats div{{background:var(--card);border:1px solid var(--rule);border-radius:8px;padding:10px 14px}}
.stats .hl{{background:var(--hlbg);border-color:var(--hl)}}
.stats b{{display:block;font-size:22px}}
.stats span{{font-size:13px;color:var(--muted)}}
.edit{{font-size:14px;color:var(--muted);margin:8px 0 14px}}
details{{border:1px solid var(--rule);border-radius:8px;background:var(--card);padding:0 16px}}
summary{{cursor:pointer;padding:12px 0;font-weight:600}}
details[open] summary{{border-bottom:1px solid var(--rule);margin-bottom:4px}}
h3{{font-size:15px;margin:16px 0 8px}}
h3 span{{font-weight:400;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:10px}}
.t{{margin:0}}
.t video{{display:block;width:100%;aspect-ratio:1;background:#000;border-radius:5px;border:2px solid transparent}}
.t figcaption{{font-size:12px;color:var(--muted);margin-top:3px}}
.t.other video{{border-color:var(--hl)}}
.t.other figcaption{{color:var(--hl);font-weight:600}}
.t.none figcaption{{color:var(--bad)}}
@media(max-width:640px){{.stats{{grid-template-columns:1fr}}.pair{{gap:8px}}}}
</style></head><body><main>
<h1>Swapping a landmark word inside π<sub>0.5</sub> with sparse autoencoder features</h1>
<p class="lede">The robot is told to pick up a black bowl and place it on the plate. We never change the instruction. Instead we edit
the model’s internal representation of one landmark word, so “stove” looks like “wooden cabinet” (or the reverse),
and check whether the robot goes for the other bowl.</p>
<div class="method"><h2>What is being edited</h2><ul>
<li><b>Model:</b> π<sub>0.5</sub> fine-tuned on LIBERO-Spatial; the edit is inside its PaliGemma language backbone.</li>
<li><b>SAE:</b> a BatchTopK sparse autoencoder trained on the <b>layer-5</b> residual stream. Its features are the units we ablate or add.</li>
<li><b>Where:</b> only at the token positions of the landmark word, after layer 5. Other tokens and the instruction text are untouched.</li>
<li><b>Grading:</b> from logged object positions (bowl on the plate). Blue borders mark rollouts where the robot took the other bowl. Numbers like #7 are LIBERO initial-state ids and match across conditions.</li>
</ul></div>
{''.join(sections)}
</main>
<script>
const wait = v => new Promise(r => v.readyState >= 2 ? r() : v.addEventListener("loadeddata", r, {{once: true}}));
document.querySelectorAll("[data-pair]").forEach(pair => {{
  const vids = [...pair.querySelectorAll("video")], btn = pair.parentElement.querySelector("[data-play]");
  btn.onclick = async () => {{
    vids.forEach(v => {{ v.pause(); v.currentTime = 0; }});
    await Promise.all(vids.map(wait));
    vids.forEach(v => v.play().catch(() => {{}}));
    btn.textContent = "↻ Replay both";
  }};
}});
document.querySelectorAll("details").forEach(d => {{
  const vids = () => [...d.querySelectorAll("video")];
  d.querySelector("[data-all]").onclick = () => vids().forEach(v => v.play().catch(() => {{}}));
  d.querySelector("[data-stop]").onclick = () => vids().forEach(v => v.pause());
}});
</script>
</body></html>"""
pathlib.Path("index.html").write_text(page)
missing = [p for p in __import__("re").findall(r'src="([^"]+)"', page) if not pathlib.Path(p).exists()]
print("missing:", missing)
