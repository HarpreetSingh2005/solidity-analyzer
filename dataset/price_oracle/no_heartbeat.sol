// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract NoHeartbeat {
    uint256 public price;
    function update(uint256 p) external {
        price = p; // BUG: no heartbeat validation
    }
}