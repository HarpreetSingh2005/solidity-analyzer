// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Hardcoded wrong heartbeat duration for the asset.
contract VulnNewOracleHeartbeat {
    function validateHeartbeat(uint256 updatedAt) public view {
        // Some feeds have 24h heartbeats, but this enforces 1h, leading to frequent reverts (DoS)
        require(block.timestamp - updatedAt <= 1 hours, "Stale");
    }
}