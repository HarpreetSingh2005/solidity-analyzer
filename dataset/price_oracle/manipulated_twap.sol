// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract ManipulatedTWAP {
    uint256 public cumulativePrice;
    function updatePrice(uint256 price) external {
        cumulativePrice += price; // BUG: manipulatable cumulative price
    }
}