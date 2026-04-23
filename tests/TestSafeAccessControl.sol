// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe contract demonstrating correct access control pattern.
contract TestSafeAccessControl {
    address public immutable owner;
    error Unauthorized();

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        if (msg.sender != owner) revert Unauthorized();
        _;
    }

    // Safe: Only the owner can call this
    function adminAction() external onlyOwner {
        // Critical action
    }
}