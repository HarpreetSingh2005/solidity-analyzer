// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract NoBoundsOracle {
    uint256 public price;
    function updatePrice(uint256 _newPrice) external {
        price = _newPrice; // BUG: no min/max bounds
    }
}