// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashReceiver {
    address public owner;

    // Vulnerability: executeOperation has no caller validation
    function executeOperation(address asset, uint256 amount, uint256 premium, address initiator, bytes calldata params) external returns (bool) {
        // Anyone can call this and make the contract approve funds to them or do arbitrary actions
        // Missing: require(msg.sender == pool, "Not lending pool");
        return true;
    }
}