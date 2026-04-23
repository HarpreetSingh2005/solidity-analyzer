// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Spot price manipulated for flash loan liquidation.
contract VulnNewFlashPrice {
    uint256 public reserve;
    function liquidate(address user) external {
        // Spot price from reserve allows flash loan manipulation
        uint256 price = reserve * 1e18; 
    }
}