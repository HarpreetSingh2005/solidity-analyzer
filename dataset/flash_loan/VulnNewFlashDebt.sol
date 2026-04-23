// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan causes integer underflow in debt tracking.
contract VulnNewFlashDebt {
    // Exploits unchecked block to erase debt
}