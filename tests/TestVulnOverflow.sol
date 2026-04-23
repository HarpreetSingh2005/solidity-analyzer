// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Vulnerable to Integer Underflow via misuse of unchecked block.
contract TestVulnOverflow {
    mapping(address => uint256) public balances;

    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }

    // Vulnerable: Improper use of unchecked block allows balance underflow
    function transfer(address to, uint256 amount) external {
        unchecked {
            // If amount > balances[msg.sender], it underflows and the sender gains massive artificial balance
            balances[msg.sender] -= amount;
            balances[to] += amount;
        }
    }
}