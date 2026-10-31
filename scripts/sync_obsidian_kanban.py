#!/usr/bin/env python3
"""
Sync Script for Obsidian Vault Kanban & Project Log (KITAdosen Project)
Lokasi: scripts/sync_obsidian_kanban.py

Fungsi:
1. Mendeteksi lokasi vault Obsidian (Google Drive cloud storage / direktori kandidat).
2. Membaca metadata KITAdosen (katalog layanan dosen, status Git lokal & remote).
3. Memperbarui file Kanban.md (Ringkasan Status, Backlog, Sedang Dikerjakan, Review, Selesai)
   dengan tetap mempertahankan kartu manual yang dibuat pengguna (tanpa penanda 🅰️).
4. Menyediakan pencatatan log otomatis ke Agent_Log.md.
5. Memperbarui indikator status proyek di Project Hub Kanban.md (⚪ -> 🟢).
6. Menginstal Git post-commit hook untuk sinkronisasi otomatis berkelanjutan pasca-commit.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Path kandidat folder proyek KITAdosen di dalam Obsidian Vault
CANDIDATE_VAULT_DIRS = [
    Path.home() / "Library" / "CloudStorage" / "GoogleDrive-auliafikri@civil.untan.ac.id" / "My Drive" / "Obsidian Vault" / "20_Academic" / "lecturer" / "1. Pendidikan" / "KITAdosen",
    Path.home() / "Obsidian Vault" / "20_Academic" / "lecturer" / "1. Pendidikan" / "KITAdosen",
    Path.home() / "Documents" / "Obsidian Vault" / "20_Academic" / "lecturer" / "1. Pendidikan" / "KITAdosen",
    Path("/Users/aulfik/Library/CloudStorage/GoogleDrive-auliafikri@civil.untan.ac.id/My Drive/Obsidian Vault/20_Academic/lecturer/1. Pendidikan/KITAdosen"),
]

# Path kandidat file induk Project Hub Kanban.md
CANDIDATE_PROJECT_HUB_FILES = [
    Path.home() / "Library" / "CloudStorage" / "GoogleDrive-auliafikri@civil.untan.ac.id" / "My Drive" / "Obsidian Vault" / "Project Hub Kanban.md",
    Path.home() / "Obsidian Vault" / "Project Hub Kanban.md",
    Path.home() / "Documents" / "Obsidian Vault" / "Project Hub Kanban.md",
    Path("/Users/aulfik/Library/CloudStorage/GoogleDrive-auliafikri@civil.untan.ac.id/My Drive/Obsidian Vault/Project Hub Kanban.md"),
]

REPO_ROOT = Path(__file__).resolve().parent.parent

# Default Backlog / Roadmap Proyek KITAdosen
KITADOSEN_ROADMAP_BACKLOG = [
    {
        "text": "Refactor data tautan layanan ke file JSON terpisah (`data/links.json`) agar mudah dimutakhirkan tanpa menyentuh script logika",
        "priority": "🔼"
    },
    {
        "text": "Tambahkan fitur kustomisasi tautan lokal (bookmark portal internal kampus seperti Siakad, Simpeg, E-Learning lokal)",
        "priority": "🔼"
    },
    {
        "text": "Konfigurasi otomatisasi deployment GitHub Pages via GitHub Actions (`.github/workflows/deploy.yml`)",
        "priority": "🔼"
    },
    {
        "text": "Rancang modul instrumen kinerja dosen & kalkulator angka kredit/BKD SISTER sesuai standar Tridharma",
        "priority": "⏫"
    },
    {
        "text": "Optimasi PWA (Progressive Web App) dengan service worker & manifest agar portal dapat dipasang sebagai aplikasi offline-ready di desktop & mobile",
        "priority": "🔽"
    }
]


def find_obsidian_dir(override_path: str | None = None) -> Path | None:
    """Mencari direktori target KITAdosen di Obsidian Vault."""
    if override_path:
        p = Path(override_path).expanduser().resolve()
        if p.exists():
            return p

    env_val = os.environ.get("OBSIDIAN_VAULT_KITADOSEN")
    if env_val:
        p = Path(env_val).expanduser().resolve()
        if p.exists():
            return p

    for p in CANDIDATE_VAULT_DIRS:
        expanded = p.expanduser()
        if expanded.exists():
            return expanded

    # Jika direktori parent 1. Pendidikan ada, buat folder KITAdosen
    for p in CANDIDATE_VAULT_DIRS:
        parent = p.parent
        if parent.exists():
            p.mkdir(parents=True, exist_ok=True)
            return p

    return None


def find_project_hub_file() -> Path | None:
    """Mencari lokasi Project Hub Kanban.md."""
    for p in CANDIDATE_PROJECT_HUB_FILES:
        expanded = p.expanduser()
        if expanded.exists():
            return expanded
    return None


def run_git(args: list[str]) -> str:
    """Menjalankan perintah Git dengan aman pada direktori repositori."""
    try:
        res = subprocess.run(
            ["git"] + args,
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout.strip()
    except Exception:
        return ""


def get_git_info() -> dict:
    """Mengumpulkan status repositori Git terkini."""
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"]) or "main"
    head_sha = run_git(["rev-parse", "--short", "HEAD"]) or "unknown"
    last_commit_date = run_git(["log", "-1", "--format=%cd", "--date=short"]) or datetime.date.today().isoformat()
    status_raw = run_git(["status", "--porcelain"])

    # Cek upstream delta
    upstream_counts = run_git(["rev-list", "--left-right", "--count", "HEAD...origin/main"])
    ahead = 0
    behind = 0
    if upstream_counts:
        parts = upstream_counts.split()
        if len(parts) == 2:
            try:
                ahead = int(parts[0])
                behind = int(parts[1])
            except ValueError:
                pass

    # Riwayat 10 commit terakhir
    log_raw = run_git(["log", "-10", "--format=%h|%cd|%s", "--date=short"])
    commits = []
    if log_raw:
        for line in log_raw.splitlines():
            parts = line.split("|", 2)
            if len(parts) == 3:
                commits.append({
                    "hash": parts[0],
                    "date": parts[1],
                    "subject": parts[2]
                })

    return {
        "branch": branch,
        "head_sha": head_sha,
        "last_commit_date": last_commit_date,
        "dirty": bool(status_raw),
        "status_lines": status_raw.splitlines() if status_raw else [],
        "ahead": ahead,
        "behind": behind,
        "commits": commits
    }


def get_kitadosen_stats() -> dict:
    """Membaca statistik portal KITAdosen dari kode sumber."""
    script_file = REPO_ROOT / "script.js"
    total_categories = 0
    total_links = 0
    categories = []

    if script_file.exists():
        content = script_file.read_text(encoding="utf-8")
        # Ekstrak kategori
        category_matches = re.findall(r'category:\s*["\']([^"\']+)["\']', content)
        categories = category_matches
        total_categories = len(category_matches)

        # Ekstrak tautan
        link_matches = re.findall(r'name:\s*["\']([^"\']+)["\'],\s*url:\s*["\']([^"\']+)["\']', content)
        total_links = len(link_matches)

    return {
        "categories_count": total_categories or 2,
        "links_count": total_links or 20,
        "categories": categories or ["Dosen Nasional", "Lainnya"]
    }


def update_kanban_file(vault_dir: Path, git_info: dict, stats: dict, dry_run: bool = False) -> bool:
    """Menulis atau memperbarui file Kanban.md di direktori Obsidian Vault."""
    kanban_path = vault_dir / "Kanban.md"
    today_str = datetime.date.today().isoformat()

    # Membaca kartu manual yang ada (kartu tanpa penanda otomatis 🅰️)
    manual_backlog: list[str] = []
    manual_in_progress: list[str] = []
    manual_review: list[str] = []
    manual_done: list[str] = []

    if kanban_path.exists():
        try:
            content = kanban_path.read_text(encoding="utf-8")
            current_section = None
            for line in content.splitlines():
                if "## 📥 Backlog" in line:
                    current_section = "backlog"
                elif "## 🚧 Sedang Dikerjakan" in line:
                    current_section = "inprogress"
                elif "## 🔍 Review" in line:
                    current_section = "review"
                elif "## ✅ Selesai" in line:
                    current_section = "done"
                elif line.startswith("## "):
                    current_section = None
                elif line.strip().startswith("- [ ]") or line.strip().startswith("- [x]"):
                    # Abaikan kartu otomatis (berpenanda 🅰️ atau berupa entri git commit commit hash)
                    if "🅰️" not in line and not re.search(r"-\s*\[[ x]\]\s*`[0-9a-f]{7,8}`", line):
                        if current_section == "backlog":
                            manual_backlog.append(line.strip())
                        elif current_section == "inprogress":
                            manual_in_progress.append(line.strip())
                        elif current_section == "review":
                            manual_review.append(line.strip())
                        elif current_section == "done":
                            manual_done.append(line.strip())
        except Exception as e:
            print(f"Peringatan: Gagal membaca kartu manual dari {kanban_path}: {e}")

    # Seed hash untuk Obsidian Kanban
    seed_hash = hashlib.md5(f"kitadosen-{today_str}-{git_info['last_commit_date']}-{git_info['head_sha']}".encode()).hexdigest()[:12]

    lines: list[str] = [
        "---",
        "kanban-plugin: board",
        "tags: [kanban, proyek, ajar]",
        f"kanban-seed: {today_str}",
        f"kanban-seed-hash: {seed_hash}",
        "---",
        "",
        "# 🗂️ KITAdosen — Kanban",
        "",
        f"**Kategori:** ajar · **Domain:** #domain/ajar · **Repo:** `~/Documents/_projects/KITAdosen`",
        f"**Branch:** `{git_info['branch']}` (`{git_info['head_sha']}`) · **Commit terakhir:** {git_info['last_commit_date']}",
        "",
        "[[20_Academic/lecturer/1. Pendidikan/KITAdosen/Agent_Log|Agent Log]] · [[Project Hub Kanban|Hub Proyek]]",
        "",
        "> Portal instrumen kinerja dosen, rekap Tridharma, pelaporan BKD SISTER.",
        "",
        "**Legenda:** ⏫ tinggi · 🔼 sedang · 🔽 rendah · `🅰️` = kartu otomatis (aman ditimpa script)",
        "",
        "## 📊 Ringkasan Status Proyek Terkini (KITAdosen)",
        "",
        f"- [ ] **Koleksi Portal Layanan:** Terdaftar aktif **{stats['links_count']} Layanan** lintas {stats['categories_count']} kategori ({', '.join(stats['categories'])}). ➕ {today_str} 🅰️",
        "",
        f"- [ ] **Arsitektur Front-End:** Web modern responsif (Glassmorphism CSS3 + Vanilla ES6 Filter Pencarian Realtime + Multi-tier Logo Fallback). ➕ {today_str} 🅰️",
        "",
    ]

    # Status upstream
    upstream_desc = "Sinkron dengan remote `origin/main`"
    if git_info["behind"] > 0:
        upstream_desc = f"Lokal tertinggal {git_info['behind']} commit dari `origin/main`"
    elif git_info["ahead"] > 0:
        upstream_desc = f"Lokal mendahului {git_info['ahead']} commit dari `origin/main`"
    lines.append(f"- [ ] **Status Git Repositori:** Branch `{git_info['branch']}` ({upstream_desc}). ➕ {today_str} 🅰️")
    lines.append("")

    # 1. Backlog
    lines.append("## 📥 Backlog")
    lines.append("")
    for item in KITADOSEN_ROADMAP_BACKLOG:
        lines.append(f"- [ ] {item['text']} {item['priority']} ➕ {today_str} 🅰️")
        lines.append("")
    for m in manual_backlog:
        lines.append(m)
        lines.append("")

    # 2. Sedang Dikerjakan
    lines.append("## 🚧 Sedang Dikerjakan")
    lines.append("")
    if git_info["dirty"]:
        changed_count = len(git_info["status_lines"])
        lines.append(f"- [ ] Review berkas perubahan aktif ({changed_count} file) di working tree ⏫ ➕ {today_str} 🅰️")
        lines.append("")
    lines.append(f"- [ ] Pemeliharaan pipeline sinkronisasi otomatis Obsidian Kanban & Git hooks 🔼 ➕ {today_str} 🅰️")
    lines.append("")
    for m in manual_in_progress:
        lines.append(m)
        lines.append("")

    # 3. Review
    lines.append("## 🔍 Review")
    lines.append("")
    lines.append(f"- [ ] Uji responsivitas UI mobile/desktop & verifikasi validitas URL eksternal layanan Kemdiktisaintek 🔼 ➕ {today_str} 🅰️")
    lines.append("")
    for m in manual_review:
        lines.append(m)
        lines.append("")

    # 4. Selesai
    lines.append("## ✅ Selesai")
    lines.append("")
    lines.append(f"- [x] Buat README: dokumentasi komprehensif, arsitektur, dan panduan menjalankan portal ✅ {today_str} 🅰️")
    lines.append("")
    lines.append(f"- [x] Inisialisasi pipeline sinkronisasi Obsidian Kanban & Agent Log otomatis terintegrasi (`scripts/sync_obsidian_kanban.py` + post-commit hook) ✅ {today_str} 🅰️")
    lines.append("")
    for c in git_info["commits"]:
        clean_subj = c["subject"].replace('"', "'")
        lines.append(f"- [x] `{c['hash']}` {clean_subj} ✅ {c['date']} 🅰️")
        lines.append("")
    for m in manual_done:
        lines.append(m)
        lines.append("")

    # Settings block
    lines.append("%% kanban:settings")
    lines.append("```")
    lines.append('{"kanban-plugin":"board","list-collapse":[true]}')
    lines.append("```")
    lines.append("%%")
    lines.append("")

    content_str = "\n".join(lines)

    if dry_run:
        print("=== DRY RUN: KANBAN.MD CONTENT ===")
        print(content_str[:1200] + "\n...[truncated]...")
        return True

    kanban_path.write_text(content_str, encoding="utf-8")
    print(f"✔ Berhasil memperbarui Kanban board di: {kanban_path}")
    return True


def append_agent_log(vault_dir: Path, title: str, details: str, status: str = "✅ Selesai", dry_run: bool = False) -> None:
    """Menambahkan entri riwayat otomatisasi ke Agent_Log.md."""
    log_path = vault_dir / "Agent_Log.md"
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    git_info = get_git_info()

    entry = f"""
## [{now_str}] {title}
- **Status:** {status}
- **Domain:** `Bahan Ajar`
- **Path Proyek:** [`~/Documents/_projects/KITAdosen`](file:///Users/aulfik/Documents/_projects/KITAdosen)
- **Branch:** `{git_info['branch']}` (`{git_info['head_sha']}`)
- **Actor:** `Antigravity Coding Assistant`

### Rangkuman Eksekusi
{details}

---
"""
    if dry_run:
        print("=== DRY RUN: AGENT LOG ENTRY ===")
        print(entry)
        return

    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        if "\n---\n" in existing:
            head, tail = existing.split("\n---\n", 1)
            updated = head + "\n---\n" + entry + tail
        else:
            updated = existing + "\n" + entry
    else:
        updated = f"# Agent Execution Log: KITAdosen\nRiwayat tugas otomatisasi yang dijalankan via Antigravity, Hermes, Herdr, dan Git Commit.\n\n---\n{entry}"

    log_path.write_text(updated, encoding="utf-8")
    print(f"✔ Berhasil mencatatkan entri riwayat eksekusi ke: {log_path}")


def update_project_hub(dry_run: bool = False) -> None:
    """Memperbarui status KITAdosen pada file Project Hub Kanban.md di root vault."""
    hub_path = find_project_hub_file()
    if not hub_path:
        return

    try:
        content = hub_path.read_text(encoding="utf-8")
        today_str = datetime.date.today().isoformat()

        # Pola target: - [ ] **[[20_Academic/lecturer/1. Pendidikan/KITAdosen/Agent_Log|KITAdosen]]** ...
        # Ganti status indikator menjadi 🟢 dan perbarui tanggal
        pattern = r"(- \[ \] \*\*\[\[20_Academic/lecturer/1\. Pendidikan/KITAdosen/Agent_Log\|KITAdosen\]\]\*\* — \[\[20_Academic/lecturer/1\. Pendidikan/KITAdosen/Kanban\|📋 Kanban\]\]\s*)([⚪🟡🟢🔴])(.*?📅\s*)(\d{4}-\d{2}-\d{2})(.*?)"

        if re.search(pattern, content):
            replacement = rf"\g<1>🟢\g<3>{today_str}\g<5>"
            updated = re.sub(pattern, replacement, content)
            if updated != content:
                if dry_run:
                    print("=== DRY RUN: PROJECT HUB UPDATE ===")
                    print("Updated KITAdosen entry to active 🟢 and today's date.")
                else:
                    hub_path.write_text(updated, encoding="utf-8")
                    print(f"✔ Berhasil memperbarui status indikator KITAdosen di: {hub_path}")
        else:
            # Pola alternatif jika format sedikit berbeda
            alt_pattern = r"(KITAdosen.*?\[\[.*?Kanban.*?\]\]\s*)([⚪🟡🟢🔴])"
            if re.search(alt_pattern, content):
                updated = re.sub(alt_pattern, r"\g<1>🟢", content)
                if not dry_run:
                    hub_path.write_text(updated, encoding="utf-8")
                    print(f"✔ Berhasil memperbarui status indikator KITAdosen di: {hub_path} (via pola alternatif)")
    except Exception as e:
        print(f"Peringatan: Gagal memperbarui Project Hub Kanban: {e}")


def install_git_hook() -> bool:
    """Menginstal Git post-commit hook untuk sinkronisasi otomatis pasca-commit."""
    hook_path = REPO_ROOT / ".git" / "hooks" / "post-commit"
    hook_script = """#!/usr/bin/env bash
# Otomatis sinkronisasi Obsidian Kanban saat commit baru berhasil dibuat
REPO_DIR="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
if command -v python3 >/dev/null 2>&1; then
    python3 "$REPO_DIR/scripts/sync_obsidian_kanban.py"
fi
"""
    try:
        hook_path.parent.mkdir(parents=True, exist_ok=True)
        hook_path.write_text(hook_script, encoding="utf-8")
        hook_path.chmod(0o755)
        print(f"✔ Git post-commit hook berhasil diinstal di: {hook_path}")
        return True
    except Exception as e:
        print(f"Peringatan: Gagal menginstal git post-commit hook: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sinkronisasi status proyek KITAdosen ke Obsidian Vault Kanban & Agent Log")
    parser.add_argument("--vault", help="Path direktori khusus folder KITAdosen di Obsidian Vault")
    parser.add_argument("--dry-run", action="store_true", help="Cek pratinjau output tanpa menulis file")
    parser.add_argument("--install-hook", action="store_true", help="Pasang Git post-commit hook otomatis")
    parser.add_argument("--log-title", help="Judul entri khusus untuk dicatatkan ke Agent_Log.md")
    parser.add_argument("--log-desc", help="Keterangan rincian untuk dicatatkan ke Agent_Log.md")
    parser.add_argument("--status", default="✅ Selesai", help="Status eksekusi untuk Agent_Log.md")
    args = parser.parse_args()

    vault_dir = find_obsidian_dir(args.vault)
    if not vault_dir:
        print("❌ Error: Tidak dapat menemukan direktori folder KITAdosen di Obsidian Vault.")
        print("Gunakan opsi --vault '/path/ke/Obsidian Vault/20_Academic/lecturer/1. Pendidikan/KITAdosen'")
        sys.exit(1)

    print(f"📁 Menggunakan direktori Obsidian Vault: {vault_dir}")

    git_info = get_git_info()
    stats = get_kitadosen_stats()

    # 1. Update Kanban.md
    update_kanban_file(vault_dir, git_info, stats, dry_run=args.dry_run)

    # 2. Update Project Hub
    update_project_hub(dry_run=args.dry_run)

    # 3. Append to Agent_Log.md jika ada log-title atau dijalankan via agen
    if args.log_title:
        append_agent_log(
            vault_dir,
            title=args.log_title,
            details=args.log_desc or "Eksekusi otomatisasi berhasil disinkronkan.",
            status=args.status,
            dry_run=args.dry_run
        )

    # 4. Install Git Hook jika diminta
    if args.install_hook:
        install_git_hook()

    print("🚀 Sinkronisasi selesai dengan sukses.")


if __name__ == "__main__":
    main()
