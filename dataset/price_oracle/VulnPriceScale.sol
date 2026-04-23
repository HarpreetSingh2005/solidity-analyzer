// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnPriceScale {
    uint256 public constant ORACLE_PRICE = 1000; // Let's assume it's fetched

    // Vulnerability: Incorrect scaling factor for collateral math
    function calculateCollateralValue(uint256 amount) public pure returns (uint256) {
        // Missing division by scaling factor (e.g., 1e18)
        return amount * ORACLE_PRICE;
    }
}