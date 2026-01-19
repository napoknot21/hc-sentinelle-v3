from __future__ import annotations

import os
import re
import sys
import time
import subprocess

import datetime as dt

from typing import Optional

from src.config.paths import TRADE_RECAP_ABS_PATH, TREADE_RECAP_DATA_RAW_DIR_ABS_PATH
from src.config.parameters import TRADE_RECAP_LAUNCHER_FILE, TRADE_RECAP_RAW_FILE_REGEX

from src.utils.formatters import date_to_str
from src.utils.logger import log


def trade_recap_launcher (

        date : Optional[str | dt.datetime | dt.date] = None,
        
        regex : Optional[re.Pattern] = None,

        launcher_file : Optional[str] = None,
        root_dir_abs : Optional[str] = None,

        raw_dir_abs : Optional[str] = None,

        loopback : int = 3,
        timeout_s : int = 30000,
        retry_sleep_s: float = 5.0,

    ) -> bool :
    """
    Runs: python main.py --start-date <date> --end-date <date> --no-draft
    Retries up to loopback times if it fails.
    """

    if loopback <= 0 :

        log("[-] Impossible to run trade recap after retries", "error")
        return False

    date_str = date_to_str(date)
    regex = TRADE_RECAP_RAW_FILE_REGEX if regex is None else regex

    launcher_file = TRADE_RECAP_LAUNCHER_FILE if launcher_file is None else launcher_file
    root_dir_abs = TRADE_RECAP_ABS_PATH if root_dir_abs is None else root_dir_abs
    raw_dir_abs = TREADE_RECAP_DATA_RAW_DIR_ABS_PATH if raw_dir_abs is None else raw_dir_abs

    script_path = os.path.join(root_dir_abs, launcher_file)

    if not os.path.isfile(script_path) :

        log(f"[-] Script not found : {script_path}", "error")
        return False

    os.makedirs(raw_dir_abs, exist_ok=True)

    cmd = [

        sys.executable,
        script_path,
        "--start-date", date_str,
        "--end-date", date_str,
        "--no-draft"

    ]

    log(f"[*] [Trade Recap] [Run] attempt={loopback}")

    try :
        
        proc = subprocess.run(

            cmd,
            capture_output=True,
            text=True,
            check=True,
            timeout=timeout_s,
            cwd=root_dir_abs,
            env=os.environ.copy(),
        
        )

        # Optional: print output if you want
        if proc.stdout :
            log(f"[*] {proc.stdout}")
        
        if proc.stderr :
            log(f"[!] {proc.stderr}", "warning")

    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e :
        
        log("[!] Retrying...", "warning")

        # Show debug info
        if isinstance(e, subprocess.CalledProcessError) :
            log(f"[-] {e.stderr}", "error")
        
        else :
            log(f"[*] [Timeout] after {timeout_s}s")

        time.sleep(retry_sleep_s)

        # Recursive call using keyword args => no arg shifting
        return trade_recap_launcher(

            date=date,
            regex=regex,
            launcher_file=launcher_file,
            root_dir_abs=root_dir_abs,
            raw_dir_abs=raw_dir_abs,
            loopback=loopback - 1,
            timeout_s=timeout_s,
            retry_sleep_s=retry_sleep_s,
            
        )
    
    return True

