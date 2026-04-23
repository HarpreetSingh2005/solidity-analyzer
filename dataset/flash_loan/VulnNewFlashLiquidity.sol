// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Adding and removing liquidity in the same block allows flash loan extraction.
contract VulnNewFlashLiquidity {
    // Missing lock or delay between deposit and withdrawal
}