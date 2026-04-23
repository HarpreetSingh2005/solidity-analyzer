// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnVotingPower {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public votingPower;

    // Vulnerability: Can transfer to oneself to artificially inflate voting power
    function transfer(address to, uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
        
        votingPower[msg.sender] -= amount;
        votingPower[to] += amount; // If to == msg.sender, voting power increases!
    }
}