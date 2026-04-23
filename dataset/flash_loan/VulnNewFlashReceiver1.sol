// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Flash loan receiver lacks caller authentication.
contract VulnNewFlashReceiver1 {
    function executeOperation(address token, uint256 amount, uint256 fee, address initiator, bytes calldata params) external returns (bool) {
        // Anyone can call this and make the contract approve tokens
        return true;
    }
}