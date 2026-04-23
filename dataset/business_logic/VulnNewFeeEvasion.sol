// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
// Vulnerability: Fee evasion. Small transfers result in 0 fee due to integer division rounding down.
contract VulnNewFeeEvasion {
    mapping(address => uint256) public balances;
    function transfer(address to, uint256 amount) external {
        uint256 fee = amount / 100; // 1% fee. If amount < 100, fee is 0
        balances[msg.sender] -= amount;
        balances[to] += (amount - fee);
    }
}