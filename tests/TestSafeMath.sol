// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe math relying on Solidity 0.8+ native checks.
contract TestSafeMath {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Safe: Solidity 0.8.x will automatically revert on underflow here without needing SafeMath
    function safeTransfer(address to, uint256 amount) external {
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
}