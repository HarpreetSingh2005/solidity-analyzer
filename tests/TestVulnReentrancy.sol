// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Reentrancy. State is updated after external call.
contract TestVulnReentrancy {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Vulnerable: Interaction before Effect (violates CEI)
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");

        balances[msg.sender] -= amount;
    }
}