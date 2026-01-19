# /*
#  * PROJECT: Koushal Jha i Technologies
#  * AUTHOR: KOUSHAL JHA (CHIEF ARCHITECT)
#  * FILE: gatekeeper.py
#  * LOCATION: D:\koushal-jha-i-technologies\persistence-vault\security\
#  * VERSION: 0.0.5.1.8
#  * CLASSIFICATION: PROPRIETARY & CONFIDENTIAL
#  */

import psycopg2
import sys
import os
import socket
import getpass
from typing import Optional

# Standard KTI Import Pathing (Rule 30.1)
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    # Rule 28.1: Aliasing v1.3.0 logic to the local gatekeeper name
    from identity_provider import generate_sovereign_signature as get_hardware_signature
except ImportError:
    print("[FATAL] Security Dependency Missing: identity_provider.py not found.")
    sys.exit(1)

class VaultGatekeeper:
    """
    KTI UNIFIED GATEKEEPER
    Maintains parity between Laptop A and Laptop B.
    """

    def __init__(self):
        # --- ARCHITECTURAL CONSTANTS (DEEP BINDING) ---
        self.__MASTER_SIGNATURE = "26d0a47eb5b79e1e46d46eba4e67dc8ab585f304bd93563c980e348cbabff544"
        
        # Rule 11.2: Hybrid Failover Pathing (Static Bridge + Active Wi-Fi)
        self.__MASTER_HOSTS = ["192.168.56.1", "10.194.170.112"] 
        
        self.__vault_port = "5432"
        self.__vault_db = "kti_persistence_vault"
        self.__vault_user = "postgres"
        self.__vault_pwd = "shivani"

    def __log_intrusion_attempt(self, connection, signature: str):
        try:
            with connection.cursor() as audit_cursor:
                audit_cursor.execute("""
                    CREATE TABLE IF NOT EXISTS intrusion_logs (
                        log_id SERIAL PRIMARY KEY,
                        attempt_signature TEXT,
                        os_user TEXT,
                        hostname TEXT,
                        attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                audit_cursor.execute("""
                    INSERT INTO intrusion_logs (attempt_signature, os_user, hostname)
                    VALUES (%s, %s, %s);
                """, (signature, getpass.getuser(), socket.gethostname()))
                connection.commit()
        except Exception:
            pass

    def authenticate_node(self) -> bool:
        # 1. Capture local physical anchor (Rule 6.1)
        __local_anchor = get_hardware_signature()
        
        # 2. Logic to determine targets: Localhost if Master, else Failover List
        if __local_anchor == self.__MASTER_SIGNATURE:
            targets = ["localhost"]
        else:
            targets = self.__MASTER_HOSTS

        # 3. Failover Execution Loop (Rule 11.2)
        for __target_host in targets:
            __conn = None
            try:
                print(f"[DEBUG] KTI-LINK: Attempting connection to {__target_host}...")
                __conn = psycopg2.connect(
                    host=__target_host,
                    port=self.__vault_port,
                    database=self.__vault_db,
                    user=self.__vault_user,
                    password=self.__vault_pwd,
                    connect_timeout=3
                )
                
                with __conn.cursor() as __secure_cursor:
                    __challenge_sql = "SELECT node_name, is_active FROM hardware_anchor_registry WHERE silicon_signature = %s;"
                    __secure_cursor.execute(__challenge_sql, (__local_anchor,))
                    __registry_fact = __secure_cursor.fetchone()

                    if __registry_fact:
                        __node_name, __is_active = __registry_fact
                        if __is_active:
                            print(f"[SUCCESS] KTI-AUTH: Node '{__node_name}' Verified via {__target_host}")
                            return True
                    
                    self.__log_intrusion_attempt(__conn, __local_anchor)
                    print(f"[FATAL] KTI-UNKNOWN: Hardware ID unauthorized.")
                    sys.exit(1)

            except psycopg2.OperationalError:
                continue 
            finally:
                if __conn: __conn.close()

        print(f"[ERROR] KTI-VAULT-UNREACHABLE: No master nodes active at {self.__MASTER_HOSTS}")
        sys.exit(1)

if __name__ == "__main__":
    VaultGatekeeper().authenticate_node()