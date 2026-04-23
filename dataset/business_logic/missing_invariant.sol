// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract MissingInvariant {
    uint256 public total;
    function add(uint256 x) external {
        total += x; // BUG: no invariant check
    }
}