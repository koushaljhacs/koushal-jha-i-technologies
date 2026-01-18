"""
----------------------------------------------------------------------------------------------
AUTHOR:         KOUSHAL JHA (CHIEF ARCHITECT)
PROJECT:        KOSHIV_SOVEREIGN_INFRA
FILE_VERSION:   1.3.0 [MIGRATION: POWERSHELL BACKEND]
CLASSIFICATION: CORE_SECURITY_PROTOCOL
DESCRIPTION:    Multi-dimensional hardware entanglement.
                Includes Physical RAM markers and Volume logic
                Aligned with Consititution v0.0.4 
-----------------------------------------------------------------------------------------------
"""

import hashlib
import subprocess
import platform
import uuid
import psutil

def get_pwsh_data(cmd):
    """ Helper to run modern PowerShell Commands."""
    try:
        return subprocess.check_output(f'powershell -command "{cmd}"', shell=True).decode().strip()
    except:
        return "UNKNOWN"
def generate_sovereign_signature():
    try:
        # 1. SILICON ANCHOR: Motherboard UUID
        _m_uuid = get_pwsh_data("(Get-CimInstance Win32_ComputerSystemProduct).UUID")

        # 2. STORAGE ANCHOR: Physical Drive Serial (Hard-bound)
        _d_serial = get_pwsh_data("(Get-CimInstance Win32_PhsicalMedia | Select-Object -First 1).SerialNumber")

        # 3. MEMORY ANCHOR: Total Physical RAM (Entropy factor) -> It's highly unlikely two machines have the exact same byte-count of total RAM
        _ram = str(psutil.virtual_memory().total)

        # 4. OS ANCHOR: Volume Serial Number of C
        _vol = get_pwsh_data("(Get_Volume -DriveLetter C).SerialNumber")

        # 5.  DEEP ENTANGLEMENT VECTOR -> We blend Phsical Silicon, Storage, Memory, and OS Logic
        _vector = f"{_m_uuid}--{_d_serial}--{_ram}--{_vol}-KOSHIV_VAULT_DEEP_SYNC_2026"
        _signature = hashlib.sha256(_vector.encode()).hexdigest()

        print(f"\n[INTERNAL] SOVEREIGN IDENTITY GENERATED (V1.3.0)")
        print(f"NODE_NAME: {platform.node()}")
        print(f"SIGNATURE: {_signature}")
        print("_" * 64)

        return _signature

    except Exception as e:
        print(f"[CRITICAL] IDENTITY_FAILURE: {e}")
        return None 
if __name__ == "__main__":
    generate_sovereign_signature()
