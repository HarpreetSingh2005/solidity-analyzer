// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Vault calculates withdrawal shares based on external balance subject to flash loans.
contract VulnNewFlashVault {
    // Shares calculation uses balance of target token
}