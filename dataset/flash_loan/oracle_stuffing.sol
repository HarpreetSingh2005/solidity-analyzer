// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract OracleStuffing {
    uint256 public cumulative;
    function update(uint256 p) external {
        cumulative += p; // BUG: stuffing cumulative price
    }
}