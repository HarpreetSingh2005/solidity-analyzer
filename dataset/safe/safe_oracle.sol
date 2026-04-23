// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeOracle {
    uint256 public price;
    uint256 public lastUpdate;

    function updatePrice(uint256 newPrice) external {
        price = newPrice;
        lastUpdate = block.timestamp;
    }
}