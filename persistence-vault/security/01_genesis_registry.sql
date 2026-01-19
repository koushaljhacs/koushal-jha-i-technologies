/*
 * PROJECT: Koushal Jha i Technologies
 * AUTHOR: KOUSHAL JHA (CHIEF ARCHITECT)
 * FILE: 01_genesis_registry.sql
 * LOCATION: D:\koushal-jha-i-technologies\persistence-vault\security\
 * VERSION: 1.3.0.1.0
 * CLASSIFICATION: PROPRIETARY & CONFIDENTIAL
 * RATIONALE: Initializes the physical hardware-to-database lock for KTI v1.3.0.
 */

-- STEP 1: INITIALIZE THE VAULT REGISTRY (SSOT)
-- This table creates a persistent link between physical silicon and database access.
CREATE TABLE IF NOT EXISTS hardware_anchor_registry (
    node_id SERIAL PRIMARY KEY,
    node_name VARCHAR(50) UNIQUE NOT NULL,
    silicon_signature CHAR(64) UNIQUE NOT NULL,
    authorized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- STEP 2: REGISTER MASTER NODES (GENESIS ENTRY)
-- Note: Replace LAPTOP_B_MASTER signature once generated on that machine.
INSERT INTO hardware_anchor_registry (node_name, silicon_signature)
VALUES 
('LAPTOP_A_MASTER', '5a9a513cceb1e9433c0ce5d0c7c13b9c46219d988006be8dca45b05e1357ae1b'),
('LAPTOP_B_MASTER', 'PENDING_V1.3.0_SIGNATURE_FROM_LAPTOP_B')
ON CONFLICT (node_name) DO UPDATE 
SET silicon_signature = EXCLUDED.silicon_signature;

-- STEP 3: LOCK & VERIFY
-- Establishing the baseline for authorized environment nodes (Rule 29.1).
SELECT node_name, authorized_at, is_active FROM hardware_anchor_registry;

/* END OF SECURE PROTOCOL */