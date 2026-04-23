// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashYieldAggregator {
    uint256 public totalShares;

    // Vulnerability: Shares are minted based on the raw ratio, vulnerable to inflation attack
    function deposit() external payable {
        uint256 shares = (msg.value * totalShares) / address(this).balance;
        if (totalShares == 0) shares = msg.value;
        totalShares += shares;
    }
}