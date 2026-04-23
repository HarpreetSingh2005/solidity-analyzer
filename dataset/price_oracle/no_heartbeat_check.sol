// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract NoHeartbeatCheck {
    uint256 public lastUpdate;
    function updatePrice() external {
        lastUpdate = block.timestamp;
    }
}