// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Dividend distribution vulnerable to flash loan.
contract VulnNewFlashDividend {
    uint256 public totalDividends = 1000 ether;
    function claimDividend(uint256 shares, uint256 totalShares) external {
        // Flash loan allows acquiring massive shares for 1 block to drain dividends
        uint256 payout = (shares * totalDividends) / totalShares;
    }
}