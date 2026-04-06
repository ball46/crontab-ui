#!/usr/bin/env python3
"""
crontab-ui — Interactive TUI for managing crontab
Usage:
  python3 crontab_ui.py            # auto-detect language from system locale
  python3 crontab_ui.py --lang en  # force English
  python3 crontab_ui.py --lang th  # force Thai
  CRONTAB_UI_LANG=en crontab-ui   # via environment variable
"""

# ── Auto-install dependency ───────────────────────────────────────────────────
import sys, subprocess, os, argparse, glob, shutil

VENV_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "crontab-ui", "venv")


def _activate_venv():
    """Add venv site-packages to sys.path so imports work without activating."""
    for pattern in [os.path.join(VENV_DIR, "lib", "python*", "site-packages"),
                    os.path.join(VENV_DIR, "Lib", "site-packages")]:
        for sp in glob.glob(pattern):
            if sp not in sys.path:
                sys.path.insert(0, sp)


def _ensure_textual():
    # 1. Already importable (system or active venv)?
    try:
        import textual  # noqa: F401
        return
    except ImportError:
        pass

    # 2. Our managed venv already has it?
    _activate_venv()
    try:
        import textual  # noqa: F401
        return
    except ImportError:
        pass

    # 3. Create venv and install textual inside it
    print("📦 Setting up crontab-ui environment...")
    os.makedirs(os.path.dirname(VENV_DIR), exist_ok=True)

    if not os.path.isdir(VENV_DIR):
        try:
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR],
                           check=True, capture_output=True)
        except subprocess.CalledProcessError:
            # python3-venv may not be installed
            print("📦 Installing python3-venv...")
            subprocess.run(["sudo", "apt-get", "install", "-y",
                            "python3-venv", "-qq"],
                           capture_output=True)
            subprocess.run([sys.executable, "-m", "venv", VENV_DIR],
                           check=True)

    # Find python inside venv
    venv_py = os.path.join(VENV_DIR, "bin", "python3")
    if not os.path.exists(venv_py):
        venv_py = os.path.join(VENV_DIR, "bin", "python")

    print("📦 Installing textual...")
    subprocess.run([venv_py, "-m", "pip", "install", "textual", "--quiet"],
                   check=True)

    _activate_venv()
    print("✅ textual installed — launching crontab-ui...\n")

_ensure_textual()
# ─────────────────────────────────────────────────────────────────────────────

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.widgets import Header, Footer, Button, Label, Input, Select, DataTable, Static
from textual.screen import Screen, ModalScreen
from textual.reactive import reactive
from textual import on


# ── i18n strings ─────────────────────────────────────────────────────────────

STRINGS = {
    "en": {
        "app_subtitle":     "Manage crontab without memorizing syntax",
        "main_topbar":      "📋 Crontab Manager",
        "main_hints":       "  [dim]n=New  e=Edit  Del=Delete  r=Reload  q=Quit[/]",
        "col_minute":       "Minute",
        "col_hour":         "Hour",
        "col_dom":          "Day(M)",
        "col_month":        "Month",
        "col_dow":          "Day(W)",
        "col_command":      "Command",
        "col_desc":         "Description",
        "no_jobs":          "[dim](no cron jobs yet)[/]",
        "loaded":           "Loaded — {n} job(s)",
        "job_added":        "Job added: {cmd}",
        "job_edited":       "Job updated",
        "job_deleted":      "Job deleted",
        "save_failed":      "Save failed: {msg}",
        "bind_new":         "New job",
        "bind_edit":        "Edit",
        "bind_delete":      "Delete",
        "bind_reload":      "Reload",
        "bind_quit":        "Quit",
        "bind_save":        "Save",
        "bind_cancel":      "Cancel",
        "sec_presets":      "── Presets ─────────────────────────────",
        "sec_custom":       "── Custom ──────────────────────────────",
        "sec_command":      "── Command ─────────────────────────────",
        "lbl_minute":       "Minute (0-59)",
        "lbl_hour":         "Hour (0-23)",
        "lbl_dom":          "Day (1-31)",
        "lbl_month":        "Month",
        "lbl_dow":          "Day of week",
        "lbl_command":      "Command",
        "ph_minute":        "* or 0-59 or */5",
        "ph_hour":          "* or 0-23 or */2",
        "ph_dom":           "* or 1-31",
        "ph_command":       "/path/to/script.sh  or  python3 /home/user/task.py",
        "btn_cancel":       "Cancel",
        "btn_save":         "💾 Save",
        "err_no_cmd":       "Please enter a command",
        "confirm_msg":      "Delete this job?\n{cmd}",
        "btn_delete":       "Delete",
        "desc_every_min":   "Every minute",
        "desc_every_hr":    "Every hour",
        "desc_midnight":    "Every day at midnight",
        "desc_workday":     "Weekdays at 09:00",
        "desc_every_n_min": "Every {n} minutes",
        "desc_every_n_hr":  "Every {n} hours",
        "desc_at_min":      "at min {v}",
        "desc_at_hr":       "hour {v}",
        "desc_on_day":      "day {v}",
        "desc_in_month":    "month {v}",
        "desc_on_dow":      "on {v}",
        "desc_custom":      "Custom schedule",
        "dow_every":        "Every day (*)",
        "dow_mon": "Monday (1)",   "dow_tue": "Tuesday (2)",  "dow_wed": "Wednesday (3)",
        "dow_thu": "Thursday (4)", "dow_fri": "Friday (5)",
        "dow_sat": "Saturday (6)", "dow_sun": "Sunday (0)",
        "dow_weekdays": "Mon-Fri (1-5)", "dow_weekend": "Sat-Sun (6,0)",
        "dow_short": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
        "dow_btn_all": "✱ All", "dow_btn_weekdays": "Weekdays", "dow_btn_weekend": "Weekend",
        "mo_btn_all": "✱ All",
        "mo_every": "Every month (*)",
        "mo_names": ["Jan","Feb","Mar","Apr","May","Jun",
                     "Jul","Aug","Sep","Oct","Nov","Dec"],
        "pre_every_min": "Every minute",   "pre_5min":    "Every 5 minutes",
        "pre_15min":     "Every 15 min",   "pre_hourly":  "Every hour",
        "pre_daily":     "Daily 00:00",    "pre_daily8":  "Daily 08:00",
        "pre_workday":   "Weekdays 09:00", "pre_weekly":  "Weekly Sun 02:00",
        "pre_monthly":   "1st of month",
        "bind_copy":     "Copy",
        "bind_paste":    "Paste",
        "job_copied":    "Copied: {cmd}",
        "job_pasted":    "Pasted: {cmd}",
        "no_job_copied": "No job copied yet",
        "cmd_not_found":  "Command not found: {cmd}\nSave anyway?",
        "btn_save_anyway": "Save anyway",
    },
    "th": {
        "app_subtitle":     "จัดการ crontab อย่างง่ายดาย",
        "main_topbar":      "📋 Crontab Manager",
        "main_hints":       "  [dim]n=เพิ่ม  e=แก้ไข  Del=ลบ  r=reload  q=ออก[/]",
        "col_minute":       "นาที",
        "col_hour":         "ชั่วโมง",
        "col_dom":          "วันที่",
        "col_month":        "เดือน",
        "col_dow":          "วันสัปดาห์",
        "col_command":      "คำสั่ง",
        "col_desc":         "ความหมาย",
        "no_jobs":          "[dim](ยังไม่มี cron job)[/]",
        "loaded":           "โหลดแล้ว — {n} งาน",
        "job_added":        "เพิ่มงานสำเร็จ: {cmd}",
        "job_edited":       "แก้ไขสำเร็จ",
        "job_deleted":      "ลบงานสำเร็จ",
        "save_failed":      "บันทึกล้มเหลว: {msg}",
        "bind_new":         "เพิ่มงานใหม่",
        "bind_edit":        "แก้ไข",
        "bind_delete":      "ลบ",
        "bind_reload":      "โหลดใหม่",
        "bind_quit":        "ออก",
        "bind_save":        "บันทึก",
        "bind_cancel":      "ยกเลิก",
        "sec_presets":      "── Presets ─────────────────────────────",
        "sec_custom":       "── กำหนดเอง ────────────────────────────",
        "sec_command":      "── คำสั่ง ──────────────────────────────",
        "lbl_minute":       "นาที (0-59)",
        "lbl_hour":         "ชั่วโมง (0-23)",
        "lbl_dom":          "วันที่ (1-31)",
        "lbl_month":        "เดือน",
        "lbl_dow":          "วันในสัปดาห์",
        "lbl_command":      "Command",
        "ph_minute":        "* หรือ 0-59 หรือ */5",
        "ph_hour":          "* หรือ 0-23 หรือ */2",
        "ph_dom":           "* หรือ 1-31",
        "ph_command":       "/path/to/script.sh  หรือ  python3 /home/user/task.py",
        "btn_cancel":       "ยกเลิก",
        "btn_save":         "💾 บันทึก",
        "err_no_cmd":       "กรุณาใส่คำสั่ง (command)",
        "confirm_msg":      "ลบงานนี้?\n{cmd}",
        "btn_delete":       "ลบ",
        "desc_every_min":   "ทุกนาที",
        "desc_every_hr":    "ทุกชั่วโมง",
        "desc_midnight":    "ทุกวัน เที่ยงคืน",
        "desc_workday":     "วันทำงาน 09:00",
        "desc_every_n_min": "ทุก {n} นาที",
        "desc_every_n_hr":  "ทุก {n} ชั่วโมง",
        "desc_at_min":      "นาที {v}",
        "desc_at_hr":       "ชั่วโมง {v}",
        "desc_on_day":      "วันที่ {v}",
        "desc_in_month":    "เดือน {v}",
        "desc_on_dow":      "วัน {v}",
        "desc_custom":      "กำหนดเอง",
        "dow_every":        "ทุกวัน (*)",
        "dow_mon": "จันทร์ (1)",  "dow_tue": "อังคาร (2)", "dow_wed": "พุธ (3)",
        "dow_thu": "พฤหัส (4)",  "dow_fri": "ศุกร์ (5)",
        "dow_sat": "เสาร์ (6)",  "dow_sun": "อาทิตย์ (0)",
        "dow_weekdays": "จ-ศ (1-5)", "dow_weekend": "ส-อา (6,0)",
        "dow_short": ["อา.", "จ.", "อ.", "พ.", "พฤ.", "ศ.", "ส."],
        "dow_btn_all": "✱ ทั้งหมด", "dow_btn_weekdays": "วันทำงาน", "dow_btn_weekend": "วันหยุด",
        "mo_btn_all": "✱ ทั้งหมด",
        "mo_every": "ทุกเดือน (*)",
        "mo_names": ["ม.ค.","ก.พ.","มี.ค.","เม.ย.","พ.ค.","มิ.ย.",
                     "ก.ค.","ส.ค.","ก.ย.","ต.ค.","พ.ย.","ธ.ค."],
        "pre_every_min": "ทุกนาที",      "pre_5min":    "ทุก 5 นาที",
        "pre_15min":     "ทุก 15 นาที",  "pre_hourly":  "ทุกชั่วโมง",
        "pre_daily":     "ทุกวัน 00:00", "pre_daily8":  "ทุกวัน 08:00",
        "pre_workday":   "วันทำงาน 09:00","pre_weekly": "ทุกอาทิตย์ 02:00",
        "pre_monthly":   "ต้นเดือน 00:00",
        "bind_copy":     "คัดลอก",
        "bind_paste":    "วาง",
        "job_copied":    "คัดลอกแล้ว: {cmd}",
        "job_pasted":    "วางแล้ว: {cmd}",
        "no_job_copied": "ยังไม่ได้คัดลอกงาน",
        "cmd_not_found":  "ไม่พบคำสั่ง: {cmd}\nบันทึกต่อหรือไม่?",
        "btn_save_anyway": "บันทึกต่อ",
    },
}


def detect_lang() -> str:
    """Priority: --lang arg > CRONTAB_UI_LANG env > system LANG > default en"""
    parser = argparse.ArgumentParser(
        prog="crontab-ui",
        description="Interactive TUI for managing crontab — no need to memorize cron syntax.",
        epilog="""
Supported languages (--lang):
  en    English (default)
  th    Thai / ภาษาไทย

  Language is auto-detected from system locale.
  Override with --lang, or set CRONTAB_UI_LANG environment variable.

Keybindings inside the TUI:
  n          Create a new cron job
  e          Edit the selected job
  Delete     Delete the selected job
  Ctrl+C     Copy the selected job
  Ctrl+V     Paste a copied job
  r          Reload crontab from system
  q          Quit
  Ctrl+S     Save (in editor)
  Escape     Cancel / go back

Examples:
  crontab-ui                  # auto-detect language
  crontab-ui --lang th        # force Thai
  crontab-ui --lang en        # force English
  CRONTAB_UI_LANG=th crontab-ui
""",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--lang", choices=["en", "th"], default=None,
                        help="UI language (en=English, th=Thai)")
    args, _ = parser.parse_known_args()
    if args.lang:
        return args.lang
    env = os.environ.get("CRONTAB_UI_LANG", "").lower()
    if env in ("en", "th"):
        return env
    if os.environ.get("LANG", "").lower().startswith("th"):
        return "th"
    return "en"


LANG = detect_lang()
T    = STRINGS[LANG]


# ── Crontab helpers ───────────────────────────────────────────────────────────

def load_crontab() -> list[dict]:
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
        lines  = result.stdout.splitlines()
    except FileNotFoundError:
        return []
    jobs = []
    for line in lines:
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = s.split(None, 5)
        if len(parts) >= 6:
            jobs.append({"raw": s,
                         "min": parts[0], "hr":  parts[1], "dom": parts[2],
                         "mo":  parts[3], "dow": parts[4], "cmd": parts[5]})
        else:
            jobs.append({"raw": s, "min":"?","hr":"?","dom":"?",
                         "mo":"?","dow":"?","cmd": s})
    return jobs


def save_crontab(jobs: list[dict]) -> tuple[bool, str]:
    lines = ["# Managed by crontab-ui\n"]
    for j in jobs:
        lines.append(f"{j['min']} {j['hr']} {j['dom']} {j['mo']} {j['dow']} {j['cmd']}\n")
    try:
        proc = subprocess.run(["crontab", "-"], input="".join(lines),
                               capture_output=True, text=True)
        return (True, "") if proc.returncode == 0 else (False, proc.stderr.strip())
    except FileNotFoundError:
        return False, "crontab command not found"


def describe(min_: str, hr: str, dom: str, mo: str, dow: str) -> str:
    expr = f"{min_} {hr} {dom} {mo} {dow}"
    if expr == "* * * * *":   return T["desc_every_min"]
    if expr == "0 * * * *":   return T["desc_every_hr"]
    if expr == "0 0 * * *":   return T["desc_midnight"]
    if expr == "0 9 * * 1-5": return T["desc_workday"]
    if min_.startswith("*/"): return T["desc_every_n_min"].format(n=min_[2:])
    if hr.startswith("*/"):   return T["desc_every_n_hr"].format(n=hr[2:])
    parts = []
    if min_ != "*": parts.append(T["desc_at_min"].format(v=min_))
    if hr   != "*": parts.append(T["desc_at_hr"].format(v=hr))
    if dom  != "*": parts.append(T["desc_on_day"].format(v=dom))
    if mo   != "*": parts.append(T["desc_in_month"].format(v=mo))
    if dow  != "*": parts.append(T["desc_on_dow"].format(v=dow))
    return " ".join(parts) if parts else T["desc_custom"]


def get_presets():
    return [
        (T["pre_every_min"], "* * * * *"),
        (T["pre_5min"],      "*/5 * * * *"),
        (T["pre_15min"],     "*/15 * * * *"),
        (T["pre_hourly"],    "0 * * * *"),
        (T["pre_daily"],     "0 0 * * *"),
        (T["pre_daily8"],    "0 8 * * *"),
        (T["pre_workday"],   "0 9 * * 1-5"),
        (T["pre_weekly"],    "0 2 * * 0"),
        (T["pre_monthly"],   "0 0 1 * *"),
    ]


def validate_cron_field(value: str, min_val: int, max_val: int) -> tuple[bool, str]:
    """Validate a single cron field value. Returns (ok, error_message)."""
    v = value.strip()
    if not v:
        return False, "Field cannot be empty"
    if " " in v:
        return False, f"Invalid value: {v}"
    if v == "*":
        return True, ""

    def _check_number(s: str) -> tuple[bool, str]:
        try:
            n = int(s)
        except ValueError:
            return False, f"Invalid value: {s}"
        if n < min_val or n > max_val:
            return False, f"{s} out of range ({min_val}-{max_val})"
        return True, ""

    def _check_step(s: str) -> tuple[bool, str]:
        try:
            step = int(s)
        except ValueError:
            return False, f"Invalid step: {s}"
        if step <= 0:
            return False, f"Step must be positive: {s}"
        return True, ""

    def _check_range_part(part: str) -> tuple[bool, str]:
        if "/" in part:
            base, step = part.split("/", 1)
            ok, msg = _check_step(step)
            if not ok:
                return ok, msg
            if base == "*":
                return True, ""
            # base is a range like "1-30"
            if "-" in base:
                lo_s, hi_s = base.split("-", 1)
                ok, msg = _check_number(lo_s)
                if not ok:
                    return ok, msg
                ok, msg = _check_number(hi_s)
                if not ok:
                    return ok, msg
                if int(lo_s) > int(hi_s):
                    return False, f"Invalid range: {lo_s}-{hi_s}"
                return True, ""
            return _check_number(base)
        if "-" in part:
            lo_s, hi_s = part.split("-", 1)
            ok, msg = _check_number(lo_s)
            if not ok:
                return ok, msg
            ok, msg = _check_number(hi_s)
            if not ok:
                return ok, msg
            if int(lo_s) > int(hi_s):
                return False, f"Invalid range: {lo_s}-{hi_s}"
            return True, ""
        return _check_number(part)

    for part in v.split(","):
        ok, msg = _check_range_part(part.strip())
        if not ok:
            return ok, msg
    return True, ""


# ── Confirm Modal ─────────────────────────────────────────────────────────────

class ConfirmModal(ModalScreen):
    CSS = """
    ConfirmModal { align: center middle; }
    #dialog {
        width: 52; height: 11;
        border: thick $error 80%;
        background: $surface; padding: 1 2;
    }
    #dialog Label { margin-bottom: 1; }
    #btn-row { margin-top: 1; align: center middle; }
    """
    def __init__(self, message: str, ok_label: str | None = None):
        super().__init__()
        self._message = message
        self._ok_label = ok_label

    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label(self._message)
            with Horizontal(id="btn-row"):
                yield Button(self._ok_label or T["btn_delete"], variant="error",   id="confirm-yes")
                yield Button(T["btn_cancel"], variant="default", id="confirm-no")

    @on(Button.Pressed, "#confirm-yes")
    def yes(self): self.dismiss(True)
    @on(Button.Pressed, "#confirm-no")
    def no(self):  self.dismiss(False)


# ── Editor Screen ─────────────────────────────────────────────────────────────

class EditorScreen(Screen):
    DOW_ORDER = [1, 2, 3, 4, 5, 6, 0]  # Mon → Sun display order

    CSS = """
    EditorScreen { background: #1e1e2e; }
    #editor-container { padding: 1 2; height: 1fr; }
    .section-title {
        color: #89b4fa; text-style: bold;
        margin-top: 1; margin-bottom: 0;
    }
    .row { height: auto; margin-bottom: 1; }
    .field-label { width: 16; content-align: left middle; padding-top: 1; color: #cdd6f4; }
    .field-input { width: 1fr; }
    #preview-box {
        background: #313244; border: round #89b4fa 60%;
        padding: 0 1; height: 3; margin-top: 1;
    }
    #preview-cron  { color: #89b4fa; text-style: bold; }
    #preview-human { color: #a6adc8; }
    #preset-grid {
        layout: grid;
        grid-size: 3;
        grid-gutter: 1;
        height: auto;
        margin-bottom: 1;
    }
    .preset-btn { min-width: 18; }
    .toggle-row { height: auto; margin-bottom: 1; }
    .toggle-btn { min-width: 6; margin: 0 1 0 0; }
    .quick-btn  { min-width: 12; margin: 0 1 0 0; }
    #btn-row-editor { height: 3; align: right middle; margin-top: 1; }
    """
    BINDINGS = [
        Binding("escape", "cancel", T["bind_cancel"]),
        Binding("ctrl+s", "save",   T["bind_save"]),
    ]

    def __init__(self, job: dict | None = None):
        super().__init__()
        self.editing_job = job

    def compose(self) -> ComposeResult:
        j = self.editing_job or {}
        yield Header(show_clock=True)
        with ScrollableContainer(id="editor-container"):
            # ── Presets (3-column grid) ──
            yield Static(T["sec_presets"], classes="section-title")
            with Container(id="preset-grid"):
                for label, expr in get_presets():
                    safe_id = expr.replace("*","X").replace("/","S").replace(" ","_")
                    yield Button(label, classes="preset-btn", id=f"preset-{safe_id}")

            # ── Custom fields ──
            yield Static(T["sec_custom"], classes="section-title")
            with Horizontal(classes="row"):
                yield Label(T["lbl_minute"], classes="field-label")
                yield Input(value=j.get("min","*"), placeholder=T["ph_minute"],
                            id="f-min", classes="field-input")
            with Horizontal(classes="row"):
                yield Label(T["lbl_hour"], classes="field-label")
                yield Input(value=j.get("hr","*"), placeholder=T["ph_hour"],
                            id="f-hr", classes="field-input")
            with Horizontal(classes="row"):
                yield Label(T["lbl_dom"], classes="field-label")
                yield Input(value=j.get("dom","*"), placeholder=T["ph_dom"],
                            id="f-dom", classes="field-input")

            # ── Day of Week (toggle buttons) ──
            yield Static(T["lbl_dow"], classes="section-title")
            with Horizontal(classes="toggle-row"):
                yield Button(T["dow_btn_all"], id="dow-all", classes="quick-btn", variant="success")
                yield Button(T["dow_btn_weekdays"], id="dow-weekdays", classes="quick-btn")
                yield Button(T["dow_btn_weekend"], id="dow-weekend", classes="quick-btn")
            with Horizontal(classes="toggle-row"):
                for dv in self.DOW_ORDER:
                    yield Button(T["dow_short"][dv], id=f"dow-v-{dv}", classes="toggle-btn")
            with Horizontal(classes="row"):
                yield Input(value=j.get("dow","*"), id="f-dow", classes="field-input")

            # ── Month (toggle buttons) ──
            yield Static(T["lbl_month"], classes="section-title")
            with Horizontal(classes="toggle-row"):
                yield Button(T["mo_btn_all"], id="mo-all", classes="quick-btn", variant="success")
            with Horizontal(classes="toggle-row"):
                for i in range(6):
                    yield Button(T["mo_names"][i], id=f"mo-v-{i+1}", classes="toggle-btn")
            with Horizontal(classes="toggle-row"):
                for i in range(6, 12):
                    yield Button(T["mo_names"][i], id=f"mo-v-{i+1}", classes="toggle-btn")
            with Horizontal(classes="row"):
                yield Input(value=j.get("mo","*"), id="f-mo", classes="field-input")

            # ── Command ──
            yield Static(T["sec_command"], classes="section-title")
            with Horizontal(classes="row"):
                yield Label(T["lbl_command"], classes="field-label")
                yield Input(value=j.get("cmd",""), placeholder=T["ph_command"],
                            id="f-cmd", classes="field-input")

            with Container(id="preview-box"):
                yield Static("", id="preview-cron")
                yield Static("", id="preview-human")

            with Horizontal(id="btn-row-editor"):
                yield Button(T["btn_cancel"], variant="default", id="btn-cancel")
                yield Button(T["btn_save"],   variant="primary",  id="btn-save")
        yield Footer()

    def on_mount(self):
        self._sync_dow_toggles()
        self._sync_mo_toggles()
        self.update_preview()
        self.query_one("#f-min").focus()

    # ── Toggle helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _parse_values(value: str) -> set[int] | None:
        """Parse cron field → set of ints, or None if '*'."""
        v = value.strip()
        if v == "*":
            return None
        result = set()
        for part in v.split(","):
            part = part.strip()
            if "-" in part and "/" not in part:
                try:
                    lo, hi = part.split("-", 1)
                    result.update(range(int(lo), int(hi) + 1))
                except ValueError:
                    pass
            else:
                try:
                    result.add(int(part))
                except ValueError:
                    pass
        return result

    def _sync_dow_toggles(self):
        """Set DOW toggle button states from the Input value."""
        val = self.query_one("#f-dow", Input).value.strip()
        if val == "*":
            for dv in range(7):
                try: self.query_one(f"#dow-v-{dv}", Button).variant = "default"
                except Exception: pass
        else:
            parsed = self._parse_values(val) or set()
            for dv in range(7):
                try:
                    self.query_one(f"#dow-v-{dv}", Button).variant = (
                        "success" if dv in parsed else "default")
                except Exception: pass
        self.query_one("#dow-all", Button).variant = "success" if val == "*" else "default"
        self.query_one("#dow-weekdays", Button).variant = (
            "success" if val in ("1-5", "1,2,3,4,5") else "default")
        self.query_one("#dow-weekend", Button).variant = (
            "success" if val in ("0,6", "6,0") else "default")

    def _sync_mo_toggles(self):
        """Set Month toggle button states from the Input value."""
        val = self.query_one("#f-mo", Input).value.strip()
        if val == "*":
            for mv in range(1, 13):
                try: self.query_one(f"#mo-v-{mv}", Button).variant = "default"
                except Exception: pass
        else:
            parsed = self._parse_values(val) or set()
            for mv in range(1, 13):
                try:
                    self.query_one(f"#mo-v-{mv}", Button).variant = (
                        "success" if mv in parsed else "default")
                except Exception: pass
        self.query_one("#mo-all", Button).variant = "success" if val == "*" else "default"

    def _dow_from_toggles(self):
        """Compute DOW value from toggle states → update Input."""
        active = [dv for dv in range(7)
                  if self.query_one(f"#dow-v-{dv}", Button).variant == "success"]
        if not active or len(active) == 7:
            val = "*"
            if len(active) == 7:
                for dv in range(7):
                    self.query_one(f"#dow-v-{dv}", Button).variant = "default"
        else:
            val = ",".join(str(v) for v in sorted(active))
        self.query_one("#f-dow", Input).value = val
        self.query_one("#dow-all", Button).variant = "success" if val == "*" else "default"
        self.query_one("#dow-weekdays", Button).variant = (
            "success" if sorted(active) == [1,2,3,4,5] else "default")
        self.query_one("#dow-weekend", Button).variant = (
            "success" if sorted(active) == [0,6] else "default")

    def _mo_from_toggles(self):
        """Compute Month value from toggle states → update Input."""
        active = [mv for mv in range(1, 13)
                  if self.query_one(f"#mo-v-{mv}", Button).variant == "success"]
        if not active or len(active) == 12:
            val = "*"
            if len(active) == 12:
                for mv in range(1, 13):
                    self.query_one(f"#mo-v-{mv}", Button).variant = "default"
        else:
            val = ",".join(str(v) for v in sorted(active))
        self.query_one("#f-mo", Input).value = val
        self.query_one("#mo-all", Button).variant = "success" if val == "*" else "default"

    # ── Event handlers ────────────────────────────────────────────────────────

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id or ""
        # Preset buttons
        if bid.startswith("preset-"):
            expr = bid[7:].replace("X","*").replace("S","/").replace("_"," ")
            parts = expr.split()
            if len(parts) == 5:
                self.query_one("#f-min", Input).value = parts[0]
                self.query_one("#f-hr",  Input).value = parts[1]
                self.query_one("#f-dom", Input).value = parts[2]
                self.query_one("#f-mo",  Input).value = parts[3]
                self.query_one("#f-dow", Input).value = parts[4]
                self._sync_dow_toggles()
                self._sync_mo_toggles()
                self.update_preview()
        # DOW quick buttons
        elif bid == "dow-all":
            self.query_one("#f-dow", Input).value = "*"
            self._sync_dow_toggles()
            self.update_preview()
        elif bid == "dow-weekdays":
            self.query_one("#f-dow", Input).value = "1-5"
            self._sync_dow_toggles()
            self.update_preview()
        elif bid == "dow-weekend":
            self.query_one("#f-dow", Input).value = "0,6"
            self._sync_dow_toggles()
            self.update_preview()
        # DOW individual toggle
        elif bid.startswith("dow-v-"):
            dv = int(bid[6:])
            current = self.query_one("#f-dow", Input).value.strip()
            if current == "*":
                for d in range(7):
                    self.query_one(f"#dow-v-{d}", Button).variant = "default"
            btn = self.query_one(f"#dow-v-{dv}", Button)
            btn.variant = "default" if btn.variant == "success" else "success"
            self._dow_from_toggles()
            self.update_preview()
        # Month quick button
        elif bid == "mo-all":
            self.query_one("#f-mo", Input).value = "*"
            self._sync_mo_toggles()
            self.update_preview()
        # Month individual toggle
        elif bid.startswith("mo-v-"):
            mv = int(bid[5:])
            current = self.query_one("#f-mo", Input).value.strip()
            if current == "*":
                for m in range(1, 13):
                    self.query_one(f"#mo-v-{m}", Button).variant = "default"
            btn = self.query_one(f"#mo-v-{mv}", Button)
            btn.variant = "default" if btn.variant == "success" else "success"
            self._mo_from_toggles()
            self.update_preview()
        # Save / Cancel
        elif bid == "btn-save":
            self.action_save()
        elif bid == "btn-cancel":
            self.action_cancel()

    @on(Input.Changed)
    def _ic(self, event: Input.Changed):
        if event.input.id == "f-dow":
            self._sync_dow_toggles()
        elif event.input.id == "f-mo":
            self._sync_mo_toggles()
        self.update_preview()

    def get_fields(self):
        return (
            self.query_one("#f-min", Input).value.strip() or "*",
            self.query_one("#f-hr",  Input).value.strip() or "*",
            self.query_one("#f-dom", Input).value.strip() or "*",
            self.query_one("#f-mo",  Input).value.strip() or "*",
            self.query_one("#f-dow", Input).value.strip() or "*",
            self.query_one("#f-cmd", Input).value.strip(),
        )

    def update_preview(self):
        min_, hr, dom, mo, dow, cmd = self.get_fields()
        cron = f"{min_} {hr} {dom} {mo} {dow}"
        self.query_one("#preview-cron",  Static).update(
            f"[bold #89b4fa]{cron}[/] {cmd or '/your/command'}")
        self.query_one("#preview-human", Static).update(describe(min_, hr, dom, mo, dow))

    def action_save(self):
        min_, hr, dom, mo, dow, cmd = self.get_fields()
        if not cmd:
            self.notify(T["err_no_cmd"], severity="error")
            return
        # extract executable from command
        parts = cmd.split()
        exe = parts[0]
        found = shutil.which(exe) is not None or os.path.isfile(exe)
        if not found:
            def on_confirm(confirmed):
                if confirmed:
                    self.dismiss({"min": min_, "hr": hr, "dom": dom, "mo": mo, "dow": dow,
                                  "cmd": cmd, "raw": f"{min_} {hr} {dom} {mo} {dow} {cmd}"})
            self.app.push_screen(
                ConfirmModal(T["cmd_not_found"].format(cmd=exe),
                             ok_label=T["btn_save_anyway"]), on_confirm)
            return
        self.dismiss({"min": min_, "hr": hr, "dom": dom, "mo": mo, "dow": dow,
                      "cmd": cmd, "raw": f"{min_} {hr} {dom} {mo} {dow} {cmd}"})

    def action_cancel(self):
        self.dismiss(None)


# ── Main Screen ───────────────────────────────────────────────────────────────

class MainScreen(Screen):
    CSS = """
    MainScreen { background: #1e1e2e; }
    #job-table { height: 1fr; }
    #bottom-bar {
        height: 3; background: #313244;
        border-top: solid #a6e3a1 40%; padding: 0 2; align: left middle;
    }
    """
    BINDINGS = [
        Binding("n",      "new_job",    T["bind_new"]),
        Binding("e",      "edit_job",   T["bind_edit"]),
        Binding("delete", "delete_job", T["bind_delete"]),
        Binding("r",      "reload",     T["bind_reload"]),
        Binding("ctrl+c", "copy_job",   T["bind_copy"]),
        Binding("ctrl+v", "paste_job",  T["bind_paste"]),
        Binding("q",      "quit",       T["bind_quit"]),
    ]

    def __init__(self):
        super().__init__()
        self.jobs: list[dict] = []
        self._clipboard: dict | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield DataTable(id="job-table", zebra_stripes=True, cursor_type="row")
        with Horizontal(id="bottom-bar"):
            yield Static("", id="status-msg")
        yield Footer()

    def on_mount(self):
        tbl = self.query_one(DataTable)
        tbl.add_column(T["col_minute"],  width=8)
        tbl.add_column(T["col_hour"],    width=10)
        tbl.add_column(T["col_dom"],     width=8)
        tbl.add_column(T["col_month"],   width=8)
        tbl.add_column(T["col_dow"],     width=12)
        tbl.add_column(T["col_command"], width=40)
        tbl.add_column(T["col_desc"],    width=24)
        self.action_reload()

    def action_reload(self):
        self.jobs = load_crontab()
        tbl = self.query_one(DataTable)
        tbl.clear()
        if not self.jobs:
            tbl.add_row("—","—","—","—","—", T["no_jobs"], "")
        else:
            for j in self.jobs:
                tbl.add_row(j["min"], j["hr"], j["dom"], j["mo"], j["dow"],
                            j["cmd"], describe(j["min"], j["hr"], j["dom"], j["mo"], j["dow"]))
        self._status(T["loaded"].format(n=len(self.jobs)))

    def _status(self, msg: str, error: bool = False):
        color = "red" if error else "green"
        self.query_one("#status-msg", Static).update(f"[{color}]{msg}[/]")

    def action_new_job(self):
        def done(job):
            if job is None: return
            self.jobs.append(job)
            ok, msg = save_crontab(self.jobs)
            if ok:
                self.action_reload()
                self._status(T["job_added"].format(cmd=job["cmd"][:40]))
            else:
                self.jobs.pop()
                self._status(T["save_failed"].format(msg=msg), error=True)
        self.app.push_screen(EditorScreen(), done)

    def action_edit_job(self):
        tbl = self.query_one(DataTable)
        if not self.jobs or tbl.cursor_row is None: return
        idx = tbl.cursor_row
        if idx >= len(self.jobs): return
        job = self.jobs[idx]
        def done(new_job):
            if new_job is None: return
            self.jobs[idx] = new_job
            ok, msg = save_crontab(self.jobs)
            if ok:
                self.action_reload()
                self._status(T["job_edited"])
            else:
                self._status(T["save_failed"].format(msg=msg), error=True)
        self.app.push_screen(EditorScreen(job=job), done)

    def action_copy_job(self):
        tbl = self.query_one(DataTable)
        if not self.jobs or tbl.cursor_row is None: return
        idx = tbl.cursor_row
        if idx >= len(self.jobs): return
        self._clipboard = dict(self.jobs[idx])
        self._status(T["job_copied"].format(cmd=self._clipboard["cmd"][:40]))

    def action_paste_job(self):
        if self._clipboard is None:
            self._status(T["no_job_copied"], error=True)
            return
        new_job = dict(self._clipboard)
        self.jobs.append(new_job)
        ok, msg = save_crontab(self.jobs)
        if ok:
            self.action_reload()
            self._status(T["job_pasted"].format(cmd=new_job["cmd"][:40]))
        else:
            self.jobs.pop()
            self._status(T["save_failed"].format(msg=msg), error=True)

    def action_delete_job(self):
        tbl = self.query_one(DataTable)
        if not self.jobs or tbl.cursor_row is None: return
        idx = tbl.cursor_row
        if idx >= len(self.jobs): return
        job = self.jobs[idx]
        def done(confirmed):
            if not confirmed: return
            self.jobs.pop(idx)
            ok, msg = save_crontab(self.jobs)
            if ok:
                self.action_reload()
                self._status(T["job_deleted"])
            else:
                self._status(T["save_failed"].format(msg=msg), error=True)
        self.app.push_screen(
            ConfirmModal(T["confirm_msg"].format(cmd=job["cmd"][:50])), done)

    def action_quit(self):
        self.app.exit()


# ── App ───────────────────────────────────────────────────────────────────────

class CrontabUI(App):
    TITLE     = "crontab-ui"
    SUB_TITLE = T["app_subtitle"]

    CSS       = """
    Screen { background: #1e1e2e; }
    Header { background: #313244; }
    Footer { background: #313244; }
    DataTable > .datatable--header { background: #45475a; color: #cdd6f4; text-style: bold; }
    DataTable > .datatable--cursor { background: #585b70; }
    Input { background: #313244; border: tall #585b70; }
    Input:focus { border: tall #89b4fa; }
    """
    BINDINGS  = [Binding("q", "quit", T["bind_quit"])]

    def on_mount(self):
        self.push_screen(MainScreen())


if __name__ == "__main__":
    CrontabUI().run()
