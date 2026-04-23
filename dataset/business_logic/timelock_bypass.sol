// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract TimelockBypass {
    uint256 public timelock = 7 days;
    function execute() external {
        require(block.timestamp > timelock, "Timelock not passed"); // BUG: timelock can be bypassed
    }
}