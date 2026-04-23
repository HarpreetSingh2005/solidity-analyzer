// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe vault avoiding donation inflation attacks by tracking internal state.
contract TestSafeVault {
    uint256 public totalShares;
    uint256 public totalAssets;
    
    // Safe: Tracks totalAssets internally rather than reading address(this).balance, preventing forced ETH attacks
    function deposit() external payable {
        uint256 shares;
        if (totalShares == 0) {
            shares = msg.value;
        } else {
            shares = (msg.value * totalShares) / totalAssets;
        }
        totalShares += shares;
        totalAssets += msg.value;
    }
}