// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Donation attack inflates share price in ERC4626 vault.
contract VulnNewOracleManipulation1 {
    uint256 public totalAssets;
    uint256 public totalShares;
    function mint() external payable {
        uint256 shares = totalShares == 0 ? msg.value : (msg.value * totalShares) / totalAssets;
        totalShares += shares;
        totalAssets += msg.value; // Attacker bypasses this via selfdestruct
    }
}