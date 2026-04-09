#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Build hub index with run + prompt provenance.")
    p.add_argument("--reports-dir", default="hub/reports")
    p.add_argument("--runs-dir", default="kb_runs")
    p.add_argument("--kb-pages-dir", default="hub/kb")
    p.add_argument("--ladder-index", default="hub/rungs/index.html")
    p.add_argument("--output", default="hub/index.html")
    p.add_argument("--title", default="Prethinker Report Hub")
    return p.parse_args()


def _resolve(path_text: str) -> Path:
    p = Path(path_text)
    return p.resolve() if p.is_absolute() else (ROOT / p).resolve()


def _rel_path(path: Path, base: Path) -> str:
    return Path(os.path.relpath(str(path), str(base))).as_posix()


def _publish_prompt_snapshot(snapshot_path: Path, hub_root: Path) -> str:
    prompts_dir = (hub_root / "prompts").resolve()
    prompts_dir.mkdir(parents=True, exist_ok=True)
    target = (prompts_dir / snapshot_path.name).resolve()
    if not target.exists():
        shutil.copy2(snapshot_path, target)
    else:
        try:
            src_text = snapshot_path.read_text(encoding="utf-8-sig")
            dst_text = target.read_text(encoding="utf-8-sig")
            if src_text != dst_text:
                shutil.copy2(snapshot_path, target)
        except Exception:
            shutil.copy2(snapshot_path, target)
    return _rel_path(target, hub_root)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        v = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception:
        return None
    return v if isinstance(v, dict) else None


def _score(num: Any, den: Any) -> float:
    try:
        n, d = float(num), float(den)
    except (TypeError, ValueError):
        return 0.0
    return 0.0 if d <= 0 else max(0.0, min(1.0, n / d))


def _fmt_iso(value: str) -> str:
    t = (value or "").strip()
    if not t:
        return "-"
    try:
        d = dt.datetime.fromisoformat(t.replace("Z", "+00:00"))
        return d.astimezone(dt.timezone.utc).strftime("%Y-%m-%d %H:%M")
    except ValueError:
        return t


def _collect_runs(runs_dir: Path, reports_dir: Path, out: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for p in sorted(runs_dir.rglob("*.json"), key=lambda x: x.name.lower()):
        if p.name.lower().endswith(".dialog.json"):
            continue
        r = _read_json(p)
        if not r:
            continue
        pm = r.get("prompt_provenance", {}) if isinstance(r.get("prompt_provenance"), dict) else {}
        stem = p.stem
        run_finished = str(r.get("run_finished_utc", "")).strip() or str(r.get("run_started_utc", "")).strip()
        if not run_finished:
            run_finished = dt.datetime.fromtimestamp(p.stat().st_mtime, tz=dt.timezone.utc).replace(microsecond=0).isoformat()
        snap = str(pm.get("snapshot_path", "")).strip()
        snap_rel = ""
        if snap and Path(snap).exists():
            snap_rel = _publish_prompt_snapshot(Path(snap).resolve(), out.parent)
        html = (reports_dir / f"{stem}.html").resolve()
        rows.append(
            {
                "run_id": str(r.get("run_id", "")).strip() or f"legacy-{stem}",
                "scenario": str(r.get("scenario", stem)),
                "kb_name": str(r.get("ontology_kb_name", "default")),
                "backend": str(r.get("backend", "unknown")),
                "model": str(r.get("model", "unknown")),
                "status": str(r.get("overall_status", "unknown")),
                "validation_total": int(r.get("validation_total", 0) or 0),
                "validation_passed": int(r.get("validation_passed", 0) or 0),
                "validation_rate": round(_score(r.get("validation_passed", 0), r.get("validation_total", 0)), 3),
                "finished_utc": run_finished,
                "prompt_id": str(pm.get("prompt_id", "")).strip() or ("legacy-file-only" if str(r.get("prompt_file", "")).strip() else "legacy-unknown"),
                "prompt_sha256": str(pm.get("prompt_sha256", "")).strip(),
                "prompt_snapshot_rel": snap_rel,
                "report_json_rel": _rel_path(p, out.parent),
                "report_html_rel": _rel_path(html, out.parent) if html.exists() else "",
            }
        )
    rows.sort(key=lambda x: (x["finished_utc"], x["run_id"]), reverse=True)
    return rows


def _collect_prompts(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    b: dict[str, dict[str, Any]] = {}
    for r in rows:
        k = str(r["prompt_id"])
        x = b.get(k) or {"prompt_id": k, "prompt_sha256": r["prompt_sha256"], "prompt_snapshot_rel": r["prompt_snapshot_rel"], "runs_total": 0, "runs_passed": 0, "val_sum": 0.0, "last_seen_utc": "", "scenarios": set(), "models": set()}
        x["runs_total"] += 1
        x["runs_passed"] += 1 if r["status"] == "passed" else 0
        x["val_sum"] += float(r["validation_rate"])
        x["last_seen_utc"] = max(str(x["last_seen_utc"]), str(r["finished_utc"]))
        x["scenarios"].add(str(r["scenario"]))
        x["models"].add(str(r["model"]))
        b[k] = x
    out: list[dict[str, Any]] = []
    for v in b.values():
        n = int(v["runs_total"])
        out.append(
            {
                "prompt_id": v["prompt_id"],
                "prompt_sha256": v["prompt_sha256"],
                "prompt_snapshot_rel": v["prompt_snapshot_rel"],
                "runs_total": n,
                "pass_rate": round(_score(v["runs_passed"], n), 3),
                "avg_validation_rate": round((float(v["val_sum"]) / n) if n else 0.0, 3),
                "last_seen_utc": v["last_seen_utc"],
                "scenario_count": len(v["scenarios"]),
                "model_count": len(v["models"]),
            }
        )
    out.sort(key=lambda x: (x["last_seen_utc"], x["prompt_id"]), reverse=True)
    return out


def _options(values: list[str], label: str) -> str:
    vals = sorted({v for v in values if v})
    return "\n".join([f"<option value=\"\">{label}</option>"] + [f"<option value=\"{v}\">{v}</option>" for v in vals])


def main() -> int:
    a = parse_args()
    reports_dir, runs_dir = _resolve(a.reports_dir), _resolve(a.runs_dir)
    kb_dir, ladder_idx, out = _resolve(a.kb_pages_dir), _resolve(a.ladder_index), _resolve(a.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    runs = _collect_runs(runs_dir, reports_dir, out)
    prompts = _collect_prompts(runs)
    data_dir = (out.parent / "data").resolve()
    data_dir.mkdir(parents=True, exist_ok=True)
    rp, pp = data_dir / "runs_manifest.json", data_dir / "prompt_versions.json"
    rp.write_text(json.dumps({"generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(), "runs_total": len(runs), "runs": runs}, indent=2), encoding="utf-8")
    pp.write_text(json.dumps({"generated_at_utc": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(), "prompt_versions_total": len(prompts), "prompt_versions": prompts}, indent=2), encoding="utf-8")

    pass_total = sum(1 for r in runs if r["status"] == "passed")
    stats = f"runs={len(runs)} passed={pass_total} pass_rate={int(_score(pass_total, len(runs))*100)}% prompts={len(prompts)}"
    s_opts = _options([str(r["scenario"]) for r in runs], "All scenarios")
    m_opts = _options([str(r["model"]) for r in runs], "All models")
    st_opts = _options([str(r["status"]) for r in runs], "All statuses")
    p_opts = _options([str(r["prompt_id"]) for r in runs], "All prompts")
    run_rows = "\n".join(
        [
            "<tr data-status=\"{status}\" data-scenario=\"{scenario}\" data-model=\"{model}\" data-prompt=\"{prompt}\" data-search=\"{search}\"><td>{finished}</td><td>{scenario}</td><td>{kb}</td><td>{backend}/{model}</td><td>{status}</td><td>{vp}/{vt}</td><td>{prompt_cell}</td><td>{report}</td><td><a href=\"{json}\">json</a></td></tr>".format(
                status=r["status"],
                scenario=r["scenario"],
                model=r["model"],
                prompt=r["prompt_id"],
                search=(" ".join([r["run_id"], r["scenario"], r["kb_name"], r["backend"], r["model"], r["prompt_id"], r["status"]])).lower(),
                finished=_fmt_iso(r["finished_utc"]),
                kb=r["kb_name"],
                backend=r["backend"],
                vp=r["validation_passed"],
                vt=r["validation_total"],
                prompt_cell=(f"<a href=\"{r['prompt_snapshot_rel']}\">{r['prompt_id']}</a>" if r["prompt_snapshot_rel"] else r["prompt_id"]),
                report=(f"<a href=\"{r['report_html_rel']}\">report</a>" if r["report_html_rel"] else "-"),
                json=r["report_json_rel"],
            )
            for r in runs
        ]
    ) or "<tr><td colspan=\"9\">No runs found.</td></tr>"
    prompt_rows = "\n".join(
        [
            "<tr><td>{pid}</td><td>{runs}</td><td>{pr}%</td><td>{vr}%</td><td>{last}</td><td>{sc}</td><td>{mc}</td><td><button class=\"pbtn\" data-prompt=\"{pid_text}\">show runs</button></td></tr>".format(
                pid=(f"<a href=\"{p['prompt_snapshot_rel']}\">{p['prompt_id']}</a>" if p["prompt_snapshot_rel"] else p["prompt_id"]),
                pid_text=p["prompt_id"],
                runs=p["runs_total"],
                pr=int(float(p["pass_rate"]) * 100),
                vr=int(float(p["avg_validation_rate"]) * 100),
                last=_fmt_iso(str(p["last_seen_utc"])),
                sc=p["scenario_count"],
                mc=p["model_count"],
            )
            for p in prompts
        ]
    ) or "<tr><td colspan=\"8\">No prompt versions.</td></tr>"
    kb_rows = "\n".join(
        [f"<tr><td><a href=\"{p.relative_to(out.parent).as_posix()}\">{p.name}</a></td><td>{dt.datetime.fromtimestamp(p.stat().st_mtime).strftime('%Y-%m-%d %H:%M')}</td><td>{max(1,int(p.stat().st_size/1024))} KB</td></tr>" for p in sorted([x for x in kb_dir.rglob('*.html') if x.is_file() and x.name.lower()!='index.html'], key=lambda x: x.name.lower())]
    ) or "<tr><td colspan=\"3\">No KB snapshots.</td></tr>"
    ladder = f"<a href=\"{ladder_idx.relative_to(out.parent).as_posix()}\">View Test Ladder</a>" if ladder_idx.exists() else ""

    html = f"""<!doctype html><html lang="en" data-theme="light"><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width, initial-scale=1"/><title>{a.title}</title><style>
    :root{{--bg:#f6f8fb;--p:#fff;--i:#172336;--m:#607089;--b:#d8e0ea;--h:#f8fbff;--l:#0a62c6}} html[data-theme="dark"]{{--bg:#111821;--p:#1a2430;--i:#e8eef6;--m:#aab6c8;--b:#314152;--h:#212d3a;--l:#7bb6ff}} body{{margin:0;background:var(--bg);color:var(--i);font-family:Segoe UI,Arial,sans-serif}} .w{{max-width:1200px;margin:0 auto;padding:20px}} .t{{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}} .nav a,.nav button{{border:1px solid var(--b);background:var(--p);padding:7px 11px;border-radius:999px;color:var(--i);text-decoration:none;cursor:pointer}} .m{{color:var(--m);font-size:13px}} .p{{background:var(--p);border:1px solid var(--b);border-radius:12px;overflow:hidden;margin:12px 0}} .ph{{padding:10px 12px;border-bottom:1px solid var(--b);background:var(--h);display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap}} .c{{display:grid;grid-template-columns:1.6fr 1fr 1fr 1fr 1fr;gap:8px;padding:10px;border-bottom:1px solid var(--b)}} .c input,.c select{{border:1px solid var(--b);background:var(--p);color:var(--i);border-radius:8px;padding:7px}} table{{width:100%;border-collapse:collapse}} th,td{{padding:9px 11px;border-bottom:1px solid var(--b);font-size:13px;text-align:left;vertical-align:top}} th{{background:var(--h);color:var(--m)}} a{{color:var(--l);text-decoration:none}} a:hover{{text-decoration:underline}} .tw{{max-height:540px;overflow:auto}} .k{{display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px}} .s{{background:var(--p);border:1px solid var(--b);border-radius:10px;padding:8px 10px}} .s b{{font-size:20px}} .hint{{padding:8px 10px;color:var(--m);font-size:12px}}
    @media (max-width:900px){{.c{{grid-template-columns:1fr 1fr}}}} @media (max-width:620px){{.c{{grid-template-columns:1fr}}}}
    </style></head><body><div class="w">
    <div class="t"><div><h1 style="margin:0">{a.title}</h1><div class="m">generated {dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')} | {stats} | <a href="{rp.relative_to(out.parent).as_posix()}">runs manifest</a> | <a href="{pp.relative_to(out.parent).as_posix()}">prompt versions</a></div></div><div class="nav">{ladder} <a href="#prompts">Prompt Evolution</a> <button id="theme">theme</button></div></div>
    <div class="k"><div class="s">Runs<br/><b>{len(runs)}</b></div><div class="s">Passed<br/><b>{pass_total}</b></div><div class="s">Pass Rate<br/><b>{int(_score(pass_total, len(runs))*100)}%</b></div><div class="s">Scenarios<br/><b>{len(set([r['scenario'] for r in runs]))}</b></div><div class="s">Prompts<br/><b>{len(prompts)}</b></div></div>
    <div class="p"><div class="ph"><b>Run Explorer</b><span id="count" class="m"></span></div><div class="c"><input id="q" placeholder="Search run/scenario/model/prompt..."/><select id="fstatus">{st_opts}</select><select id="fscenario">{s_opts}</select><select id="fmodel">{m_opts}</select><select id="fprompt">{p_opts}</select></div><div class="tw"><table><thead><tr><th>Finished</th><th>Scenario</th><th>KB</th><th>Backend/Model</th><th>Status</th><th>Validation</th><th>Prompt</th><th>Report</th><th>JSON</th></tr></thead><tbody id="runs">{run_rows}</tbody></table></div><div class="hint">Use prompt filter to compare the same rung across prompt versions.</div></div>
    <div id="prompts" class="p"><div class="ph"><b>Prompt Evolution</b></div><div class="tw"><table><thead><tr><th>Prompt ID</th><th>Runs</th><th>Pass %</th><th>Avg Validation %</th><th>Last Seen</th><th>Scenarios</th><th>Models</th><th>Action</th></tr></thead><tbody>{prompt_rows}</tbody></table></div></div>
    <div class="p"><div class="ph"><b>KB Snapshots</b></div><table><thead><tr><th>KB</th><th>Updated</th><th>Size</th></tr></thead><tbody>{kb_rows}</tbody></table></div>
    </div><script>(()=>{{const r=document.documentElement,t=document.getElementById('theme'),k='hub_theme_pref',s=localStorage.getItem(k);r.setAttribute('data-theme',(s==='dark'||s==='light')?s:((matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches)?'dark':'light'));const sync=()=>t.textContent='theme: '+(r.getAttribute('data-theme')==='dark'?'dark':'light');sync();t.onclick=()=>{{const n=r.getAttribute('data-theme')==='dark'?'light':'dark';r.setAttribute('data-theme',n);localStorage.setItem(k,n);sync();}};const q=document.getElementById('q'),fs=document.getElementById('fstatus'),fc=document.getElementById('fscenario'),fm=document.getElementById('fmodel'),fp=document.getElementById('fprompt'),rows=[...document.querySelectorAll('#runs tr')],count=document.getElementById('count');const run=()=>{{const s=(q.value||'').toLowerCase().trim(),a=(fs.value||''),c=(fc.value||''),m=(fm.value||''),p=(fp.value||'');let n=0;for(const row of rows){{const ok=(!a||row.dataset.status===a)&&(!c||row.dataset.scenario===c)&&(!m||row.dataset.model===m)&&(!p||row.dataset.prompt===p)&&(!s||(row.dataset.search||'').includes(s));row.style.display=ok?'':'none';if(ok)n++;}}count.textContent=`showing ${{n}} / ${{rows.length}} runs`;}};[q,fs,fc,fm,fp].forEach(x=>x&&x.addEventListener('input',run));[fs,fc,fm,fp].forEach(x=>x&&x.addEventListener('change',run));for(const b of document.querySelectorAll('.pbtn')){{b.addEventListener('click',()=>{{fp.value=b.dataset.prompt||'';run();window.scrollTo({{top:0,behavior:'smooth'}});}});}}run();}})();</script></body></html>"""
    out.write_text(html, encoding="utf-8")
    print(f"Wrote {out}")
    print(f"Wrote {rp}")
    print(f"Wrote {pp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())



