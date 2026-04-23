// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnBurnMissingCheck {
    mapping(address => uint256) public balanceOf;

    // Vulnerability: Missing allowance check for burning someone else's tokens
    function burnFrom(address from, uint256 amount) external {
        require(balanceOf[from] >= amount, "Insufficient balance");
        
        // No check if msg.sender is allowed to burn `from` tokens!
        balanceOf[from] -= amount;
    }
}