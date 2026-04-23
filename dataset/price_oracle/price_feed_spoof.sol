// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract PriceFeedSpoof {
    uint256 public price = 1000e18;
    function setPrice(uint256 newPrice) external {
        price = newPrice; // BUG: no access control
    }
}