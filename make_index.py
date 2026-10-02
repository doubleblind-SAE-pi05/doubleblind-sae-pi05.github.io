"""Generate index.html from the rollout videos in rollouts_scene7_9/videos (run from the repo root).

All wording is taken from the paper "Editing the Goal: Per-Token SAE Steering and Its Depth Limits in pi0.5".
"""
import pathlib

V = "rollouts_scene7_9/videos"
SCENES = [
    dict(id=7, own="stove", other="wooden cabinet", feat=2, n_base=10,
         prompt="pick up the black bowl on the <b>stove</b> and place it on the plate",
         setting="Layer 5, word-selected",
         edit="Swap top-16 “stove” SAE features for top-16 “cabinet” SAE features at the goal word.",
         swap_ok=15, random="16 random features: 2, 1, 0 of 20 (three random draws)",
         own_ids={1, 9, 14, 18}, none_ids={7}, base_ok=10),
    dict(id=9, own="wooden cabinet", other="stove", feat=1, n_base=10,
         prompt="pick up the black bowl on the <b>wooden cabinet</b> and place it on the plate",
         setting="Layer 5, contrastive",
         edit="The 64 latents whose codes at the goal word change most between prompts A and B, set to their mean under prompt B.",
         swap_ok=18, random="16 random features: 0, 0, 0 of 20 (three random draws)",
         own_ids={0}, none_ids={13}, base_ok=10),
]

COMING = [
    ("Layer 0", "BatchTopK feature swaps redirect behavior in up to 20/20 rollouts in a scene where random-feature swaps redirect none."),
    ("LIBERO-Object", "Four scenes where the instructions differ only in the object to be placed in the basket: soup → dressing, cream cheese → soup, ketchup → BBQ sauce, butter → tomato sauce."),
    ("Difference vector", "Adding a fixed difference-in-means vector at twice its natural magnitude redirects 8–10/10 rollouts."),
    ("Activation patching", "Goal-word edits remain effective up to layer 6 for object location and layer 2 for object identity, and up to layer 13 when patching also covers camera tokens."),
    ("Matryoshka", "Word-selected Matryoshka edits largely do not outperform random ones."),
    ("Single-feature ablation", "Single goal-word features show little causal effect when ablated."),
]


def outcome(sc, i):
    if i in sc["none_ids"]:
        return "neither task completed", "none"
    if i in sc["own_ids"]:
        return f"bowl on the {sc['own']}", "own"
    return f"bowl on the {sc['other']}", "other"


def tile(src, tid, label, cls):
    return (f'<figure class="t {cls}" id="{tid}"><video src="{src}#t=0.1" muted loop playsinline preload="metadata"></video>'
            f"<figcaption>{label}</figcaption></figure>")


def strip(sc, s):
    chips = "".join(
        f'<a class="chip {outcome(sc, i)[1]}" href="#s{s}swap{i}" data-open title="#{i} · {outcome(sc, i)[0]}"></a>'
        for i in range(20))
    return f'<div class="strip" aria-label="Outcome of each rollout">{chips}</div>'


sections = []
for sc in SCENES:
    s, f = sc["id"], sc["feat"]
    fl = outcome(sc, f)[0]
    all_base = "".join(tile(f"{V}/s{s}_unchanged_{i}.mp4", f"s{s}base{i}", f"#{i} · bowl on the {sc['own']}", "own") for i in range(10))
    all_swap = "".join(tile(f"{V}/s{s}_swap_{i}.mp4", f"s{s}swap{i}", f"#{i} · {outcome(sc, i)[0]}" + (" ✓" if outcome(sc, i)[1] == "other" else ""), outcome(sc, i)[1]) for i in range(20))
    sections.append(f"""
<section class="scene" id="scene{s}">
  <div class="head"><h2>Scene {s}</h2><span class="setting">{sc['setting']}</span></div>
  <p class="prompt">LIBERO-Spatial, scene {s}: “{sc['prompt']}”</p>
  <div class="pair" data-pair>
    <figure class="hero"><video src="{V}/s{s}_unchanged_{f}.mp4#t=0.1" muted loop playsinline preload="auto"></video>
      <figcaption><span class="tag">π<sub>0.5</sub>-LIBERO unchanged</span>Picks up the bowl on the {sc['own']}</figcaption></figure>
    <figure class="hero swap"><video src="{V}/s{s}_swap_{f}.mp4#t=0.1" muted loop playsinline preload="auto"></video>
      <figcaption><span class="tag">SAE swap</span>Picks up the {fl} instead</figcaption></figure>
  </div>
  <div class="bar"><button class="play" data-play>▶ Play both</button><span class="muted">Both runs see scene {s} and read the same instruction (#{f}).</span></div>
  <div class="stats">
    <div><b>{sc['base_ok']}/{sc['n_base']}</b><span>rollouts: bowl on the {sc['own']}</span></div>
    <div class="hl"><b>{sc['swap_ok']}/20</b><span>rollouts: bowl on the {sc['other']} instead</span></div>
    <div><b>control</b><span>{sc['random']}</span></div>
  </div>
  <p class="edit"><b>{sc['setting']}.</b> {sc['edit']}</p>
  <details id="d{s}">
    <summary>All rollouts <span>{sc['base_ok']} unchanged · 20 swapped</span></summary>
    <div class="legend"><i class="chip other"></i>completes prompt B’s task <i class="chip own"></i>completes prompt A’s task <i class="chip none"></i>neither</div>
    <h3>π<sub>0.5</sub>-LIBERO unchanged <span>· {sc['base_ok']}/{sc['n_base']} on the {sc['own']}</span></h3>
    <div class="grid">{all_base}</div>
    <h3>SAE swap <span>· {sc['swap_ok']}/20 on the {sc['other']}</span></h3>
    <div class="grid">{all_swap}</div>
    <div class="bar"><button data-all>Play all</button><button data-stop>Pause all</button></div>
  </details>
  <div class="striprow"><span class="muted">SAE swap, rollouts #0–#19</span>{strip(sc, s)}</div>
</section>""")

coming = "".join(f'<li><b>{t}</b><span>{d}</span></li>' for t, d in COMING)

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Editing the Goal</title>
<style>
:root{{--bg:#fbfbfa;--card:#fff;--ink:#1c1f24;--muted:#5d6470;--rule:#d9dce1;--hl:#4b5d9a;--hlbg:#eef1fa;--own:#b9a063;--bad:#b3433f}}
@media(prefers-color-scheme:dark){{:root{{--bg:#14161a;--card:#1c1f25;--ink:#e8eaee;--muted:#98a0ad;--rule:#2f343d;--hl:#8ea2e6;--hlbg:#222a44;--own:#a68f55;--bad:#e58a8a}}}}
*{{box-sizing:border-box}}
html{{scroll-behavior:smooth}}
body{{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif;padding:32px 16px 72px}}
main{{max-width:1040px;margin:0 auto}}
.status{{display:inline-block;font-size:12px;font-weight:600;letter-spacing:.05em;text-transform:uppercase;padding:3px 11px;border-radius:99px;background:var(--hlbg);color:var(--hl);border:1px solid var(--hl)}}
h1{{font-size:34px;line-height:1.15;margin:14px 0 6px;letter-spacing:-.01em}}
.by{{margin:0 0 18px;color:var(--muted)}}
.lede{{font-size:18px;max-width:800px;margin:0 0 22px}}
.method{{background:var(--card);border:1px solid var(--rule);border-radius:12px;padding:16px 22px}}
.method h2{{margin:0 0 6px;font-size:16px}}
.method ul{{margin:0;padding-left:20px}}
.method li{{margin:5px 0}}
.scene{{margin-top:44px;padding-top:10px;border-top:1px solid var(--rule)}}
.head{{display:flex;flex-wrap:wrap;align-items:baseline;gap:12px;margin-top:14px}}
h2{{font-size:24px;margin:0}}
.setting{{font-size:13px;font-weight:600;color:var(--hl);background:var(--hlbg);padding:2px 10px;border-radius:99px}}
.prompt{{margin:4px 0 16px;color:var(--muted)}}
.pair{{display:grid;grid-template-columns:1fr 1fr;gap:16px}}
.hero{{margin:0}}
.hero video{{display:block;width:100%;aspect-ratio:1;background:#000;border-radius:12px;border:3px solid var(--rule)}}
.hero.swap video{{border-color:var(--hl);box-shadow:0 6px 24px -10px var(--hl)}}
.hero figcaption{{margin-top:8px;font-size:15px}}
.tag{{display:block;margin-bottom:2px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}}
.swap .tag{{color:var(--hl)}}
.bar{{display:flex;flex-wrap:wrap;gap:12px;align-items:center;margin:14px 0}}
button{{font:inherit;font-weight:600;padding:8px 18px;border:1px solid var(--hl);background:var(--hl);color:#fff;border-radius:8px;cursor:pointer}}
button[data-all],button[data-stop]{{background:var(--card);color:var(--ink);border-color:var(--rule);font-weight:500;padding:5px 12px}}
button:hover{{filter:brightness(1.1)}}
.muted{{color:var(--muted);font-size:14px}}
.stats{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin:6px 0 10px}}
.stats div{{background:var(--card);border:1px solid var(--rule);border-radius:10px;padding:12px 16px}}
.stats .hl{{background:var(--hlbg);border-color:var(--hl)}}
.stats b{{display:block;font-size:26px;line-height:1.2}}
.stats .hl b{{color:var(--hl)}}
.stats span{{font-size:13px;color:var(--muted)}}
.edit{{font-size:14px;color:var(--muted);margin:8px 0 14px}}
.edit b{{color:var(--ink)}}
.striprow{{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;margin-top:12px}}
.strip{{display:flex;gap:4px;flex-wrap:wrap}}
.chip{{display:inline-block;width:16px;height:16px;border-radius:4px;border:1px solid transparent;vertical-align:-3px;margin-right:2px}}
.strip .chip{{margin:0}}
a.chip:hover{{transform:scale(1.25)}}
.chip.other{{background:var(--hl)}}
.chip.own{{background:var(--own)}}
.chip.none{{background:transparent;border-color:var(--bad)}}
.legend{{font-size:13px;color:var(--muted);margin:12px 0 0;display:flex;flex-wrap:wrap;gap:4px 8px;align-items:center}}
.legend .chip{{margin-left:10px}}
details{{border:1px solid var(--rule);border-radius:10px;background:var(--card);padding:0 18px}}
summary{{cursor:pointer;padding:13px 0;font-weight:600}}
summary span{{font-weight:400;color:var(--muted);margin-left:8px;font-size:14px}}
details[open] summary{{border-bottom:1px solid var(--rule)}}
h3{{font-size:15px;margin:18px 0 8px}}
h3 span{{font-weight:400;color:var(--muted)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
.t{{margin:0;scroll-margin-top:20px}}
.t video{{display:block;width:100%;aspect-ratio:1;background:#000;border-radius:8px;border:2px solid transparent;cursor:pointer}}
.t figcaption{{font-size:12px;color:var(--muted);margin-top:4px}}
.t.other video{{border-color:var(--hl)}}
.t.own video{{border-color:var(--own)}}
.t.none video{{border-color:var(--bad)}}
.t.other figcaption{{color:var(--hl);font-weight:600}}
.t.none figcaption{{color:var(--bad)}}
.t:target video{{outline:3px solid var(--ink);outline-offset:2px}}
.details-pad{{height:12px}}
.coming{{margin-top:56px;padding-top:12px;border-top:1px solid var(--rule)}}
.coming h2{{margin-bottom:4px}}
.coming ul{{list-style:none;margin:14px 0 0;padding:0;display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:12px}}
.coming li{{border:1.5px dashed var(--rule);border-radius:12px;padding:14px 18px;background:var(--card)}}
.coming li b{{display:block;margin-bottom:2px}}
.coming li span{{font-size:14px;color:var(--muted)}}
footer{{margin-top:48px;font-size:13px;color:var(--muted)}}
@media(max-width:640px){{h1{{font-size:26px}}.stats{{grid-template-columns:1fr}}.pair{{gap:8px}}.hero figcaption{{font-size:13px}}}}
</style></head><body><main>
<span class="status">Website being built</span>
<h1>Editing the Goal: Per-Token SAE Steering and Its Depth Limits in π<sub>0.5</sub></h1>
<p class="by">Anonymous Author(s)</p>
<p class="lede">Replacing the SAE features of a single goal word with those of an alternative goal word, leaving the instruction text unchanged, steers π<sub>0.5</sub>-LIBERO into completing the alternative task.</p>
<div class="method"><h2>Setup</h2><ul>
<li><b>Scenes:</b> LIBERO-Spatial, where the policy must pick the correct one of two black bowls and place it on the plate. Scenes 7 (“on the stove”) and 9 (“on the wooden cabinet”) form a mirror pair.</li>
<li><b>SAE swap:</b> encode the residual stream at A’s goal word, set latent codes, and add the change back through the decoder, leaving other latents and the reconstruction error unchanged. The edit is reapplied at every policy call.</li>
<li><b>Layer L</b> is the output of PaliGemma block L. These rollouts use BatchTopK SAEs at layer 5.</li>
<li><b>Success:</b> an edit counts as successful only if the robot completes prompt B’s task. Each swap is run with a control edit of random latents.</li>
</ul></div>
{''.join(sections)}
<section class="coming" id="more">
  <h2>More rollouts and examples to come</h2>
  <p class="muted">Results from the paper that will get their own rollouts here.</p>
  <ul>{coming}</ul>
</section>
<footer>Submitted to the 10th Conference on Robot Learning (CoRL 2026).</footer>
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
document.querySelectorAll(".t video").forEach(v => v.onclick = () => v.paused ? v.play() : v.pause());
document.querySelectorAll("[data-open]").forEach(a => a.addEventListener("click", e => {{
  const t = document.querySelector(a.getAttribute("href"));
  t.closest("details").open = true;
}}));
</script>
</body></html>"""
pathlib.Path("index.html").write_text(page)
missing = [p.split("#")[0] for p in __import__("re").findall(r'src="([^"]+)"', page) if not pathlib.Path(p.split("#")[0]).exists()]
print("missing:", missing)
