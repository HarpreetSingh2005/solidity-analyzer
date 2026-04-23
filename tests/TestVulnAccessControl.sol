// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Access Control. Missing onlyOwner modifier on destructive function.
contract TestVulnAccessControl {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    // Vulnerable: Anyone can call this function and destroy the contract
    function destroy() external {
        selfdestruct(payable(msg.sender));
    }
}