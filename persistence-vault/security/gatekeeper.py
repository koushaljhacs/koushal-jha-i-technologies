/*
 * PROJECT: Koushal Jha i Technologies
 * AUTHOR: KOUSHAL JHA (CHIEF ARCHITECT)
 * FILE: gatekeeper.py
 * LOCATION: D:\koushal-jha-i-technologies\persistence-vault\security\
 * VERSION: 0.0.5 (SILICON_ANCHOR_PHASE)
 * CLASSIFICATION: PROPRIETARY & CONFIDENTIAL
 */

import psycopg2
import sys
import os
import socket
import getpass
from typing import Optional

# Standard KTI Import Pathing for Security Modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from identity_provider import get_hardware_signature
except ImportError:
    print("[FATAL] Security Dependency Missing: identity_provider.py not found.")
    sys.exit(1)

class VaultGatekeeper:
    """
    KTI UNIFIED GATEKEEPER
    Maintains parity between Laptop A and Laptop B.
    Features: Deep Binding, Dynamic Routing, and Intrusion Auditing.
    """

    def __init__(self):
        # --- ARCHITECTURAL CONSTANTS (DEEP BINDING) ---
        # The Master Anchor for Laptop A (The Server Node)
        self.__MASTER_SIGNATURE = "26d0a47eb5b79e1e46d46eba4e67dc8ab585f304bd93563c980e348cbabff544"
        
        # The Internal IP of Laptop A (The SSOT Node)
        # Ensure this matches Laptop A's current IPv4 address
        self.__MASTER_NODE_IP = "192.168.56.1" 
        
        # DATABASE CREDENTIALS
        self.__vault_port = "5432"
        self.__vault_db = "kti_persistence_vault"
        self.__vault_user = "postgres"
        self.__vault_pwd = "shivani"

    def __resolve_target_host(self, current_silicon_id: str) -> str:
        """
        DETERMINISTIC ROUTING:
        On Master Node -> Connect via Localhost (High Performance).
        On Peer Nodes   -> Connect via Master IP (Network Path).
        """
        if current_silicon_id == self.__MASTER_SIGNATURE:
            return "localhost"
        return self.__MASTER_NODE_IP

    def __log_intrusion_attempt(self, connection, signature: str):
        """
        BLACK BOX RECORDER:
        Logs unauthorized access attempts to the Sovereign Vault.
        """
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
            pass # Fail-silent to proceed with immediate process termination

    def authenticate_node(self) -> bool:
        """
        The Sovereign Handshake.
        Binds physical silicon to the Persistent Database Registry.
        """
        # 1. Capture local physical anchor
        __local_anchor = get_hardware_signature()
        
        # 2. Resolve Network Route (Parity Logic)
        __target_host = self.__resolve_target_host(__local_anchor)
        
        __conn = None
        
        try:
            # 3. Establish Secure Link (5-second handshake timeout)
            __conn = psycopg2.connect(
                host=__target_host,
                port=self.__vault_port,
                database=self.__vault_db,
                user=self.__vault_user,
                password=self.__vault_pwd,
                connect_timeout=5
            )
            
            with __conn.cursor() as __secure_cursor:
                # 4. Challenge the Sovereign Registry
                __challenge_sql = """
                    SELECT node_name, is_active 
                    FROM hardware_anchor_registry 
                    WHERE silicon_signature = %s;
                """
                __secure_cursor.execute(__challenge_sql, (__local_anchor,))
                __registry_fact = __secure_cursor.fetchone()

                # 5. Deep Validation and Intrusion Trap
                if __registry_fact:
                    __node_name, __is_active = __registry_fact
                    
                    if __is_active:
                        print(f"[SUCCESS] KTI-AUTH: Node '{__node_name}' Verified via {__target_host}")
                        return True
                    else:
                        print(f"[CRITICAL] KTI-REVOKED: Node '{__node_name}' access is disabled.")
                else:
                    self.__log_intrusion_attempt(__conn, __local_anchor)
                    print(f"[FATAL] KTI-UNKNOWN: Hardware ID unauthorized. Intrusion Logged.")
                
                # Halt execution if validation fails
                sys.exit(1)

        except psycopg2.OperationalError:
            print(f"[ERROR] KTI-VAULT-UNREACHABLE: Ensure Master Node (Laptop A) is online at {__target_host}")
            sys.exit(1)
        except Exception as __err:
            print(f"[ERROR] KTI-SECURITY-EXCEPTION: {str(__err)}")
            sys.exit(1)
        finally:
            if __conn:
                __conn.close()

if __name__ == "__main__":
    # Execute Master Handshake
    VaultGatekeeper().authenticate_node()