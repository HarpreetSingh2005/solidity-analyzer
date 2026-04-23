// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnWrongAccounting {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;

    // Vulnerability: Accounting mismatch
    function mint(address to, uint256 amount) external {
        totalSupply += amount;
        // Forgot to update balances[to]!
    }
}