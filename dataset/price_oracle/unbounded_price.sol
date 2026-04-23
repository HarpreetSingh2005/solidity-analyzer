// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract UnboundedPrice {
    uint256 public price;
    function updatePrice(uint256 p) external {
        price = p; // BUG: no upper bound
    }
}