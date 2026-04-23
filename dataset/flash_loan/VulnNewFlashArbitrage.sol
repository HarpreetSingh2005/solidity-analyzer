// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan arbitrage contract missing slippage checks.
contract VulnNewFlashArbitrage {
    function executeArbitrage() external {
        // Sandwich attackers can extract value because there's no minAmountOut check
    }
}