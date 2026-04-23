// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Missing allowance decrease during transferFrom.
contract VulnNewDoubleSpend {
    mapping(address => mapping(address => uint256)) public allowance;
    mapping(address => uint256) public balances;
    function transferFrom(address from, address to, uint256 amount) external {
        require(allowance[from][msg.sender] >= amount, "No allowance");
        balances[from] -= amount;
        balances[to] += amount;
        // Forgot: allowance[from][msg.sender] -= amount;
    }
}