// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
interface IERC20 { function approve(address, uint256) external; }
// Vulnerability: Receiver approves infinite tokens to msg.sender instead of pool.
contract VulnNewFlashReceiver2 {
    function executeOperation(address token, uint256 amount, uint256 fee) external returns (bool) {
        // Approves msg.sender (which could be an attacker calling directly)
        IERC20(token).approve(msg.sender, type(uint256).max);
        return true;
    }
}