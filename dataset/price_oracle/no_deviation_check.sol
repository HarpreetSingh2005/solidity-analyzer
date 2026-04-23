// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract NoDeviationCheck {
    uint256 public price;
    function updatePrice(uint256 newPrice) external {
        price = newPrice; // BUG: no deviation check from previous price
    }
}