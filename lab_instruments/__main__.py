import sys
import os


def _ensure_scripts_on_path():
    """Add the Python Scripts dir to the user's PATH on Windows if missing.

    Uses winreg (stdlib, no admin required) so pip-installed console scripts
    like scpi-repl are discoverable after a terminal restart.  Safe no-op on
    non-Windows platforms or if the directory is already present.
    """
    if sys.platform != 'win32':
        return

    scripts_dir = os.path.join(sys.prefix, 'Scripts')

    # Already in the current process PATH — nothing to do.
    if scripts_dir.lower() in os.environ.get('PATH', '').lower():
        return

    try:
        import winreg

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r'Environment',
            0,
            winreg.KEY_READ | winreg.KEY_WRITE,
        )
        try:
            user_path, reg_type = winreg.QueryValueEx(key, 'PATH')
        except FileNotFoundError:
            user_path = ''
            reg_type = winreg.REG_EXPAND_SZ

        if scripts_dir.lower() not in user_path.lower():
            new_path = f"{scripts_dir};{user_path}" if user_path else scripts_dir
            winreg.SetValueEx(key, 'PATH', 0, reg_type, new_path)

            # Broadcast WM_SETTINGCHANGE so new terminals inherit the updated PATH.
            import ctypes
            ctypes.windll.user32.SendMessageTimeoutW(
                0xFFFF,   # HWND_BROADCAST
                0x001A,   # WM_SETTINGCHANGE
                0,
                'Environment',
                0x0002,   # SMTO_ABORTIFHUNG
                1000,
                None,
            )

            print(f"[scpi] Added Python Scripts to your PATH ({scripts_dir}).")
            print("[scpi] Open a new terminal and 'scpi-repl' will work.")

        winreg.CloseKey(key)
    except Exception:
        pass  # Never let a PATH fix crash the REPL.


_ensure_scripts_on_path()

from lab_instruments.repl import main  # noqa: E402

main()
