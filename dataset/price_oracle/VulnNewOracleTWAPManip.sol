// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Easily manipulated TWAP due to extremely low liquidity in the selected pool.
contract VulnNewOracleTWAPManip {
    uint256 public twapPrice;
    function setTWAP(uint256 _price) external {
        // Normally fetched from a low-liquidity pool where an attacker can easily push the price
        twapPrice = _price;
    }
}