// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract SafeBank {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;           // Effects
        payable(msg.sender).transfer(amount);     // Interactions (CEI)
    }
}