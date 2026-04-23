// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fallback oracle fails silently or returns 0.
contract VulnNewOracleFallback {
    function getPrice() public pure returns (uint256) {
        bool mainOracleWorks = false;
        if (mainOracleWorks) {
            return 1000;
        }
        // Fallback returns 0 instead of reverting, allowing free assets
        return 0;
    }
}