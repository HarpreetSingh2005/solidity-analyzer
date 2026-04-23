// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract InflatedPrice {
    uint256 public price = 1e18;
    function updatePrice(uint256 newPrice) external {
        price = newPrice; // BUG: can be inflated
    }
}