// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SingleSourceOracle {
    uint256 public price;
    function setPrice(uint256 p) external {
        price = p; // BUG: single source of truth
    }
}