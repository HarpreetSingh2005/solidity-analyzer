// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract VestingBypass {
    struct Vesting { uint256 amount; uint256 startTime; uint256 cliff; }
    mapping(address => Vesting) public vestings;
    mapping(address => uint256) public balances;
    function createVesting(uint256 amount, uint256 cliff) external {
        vestings[msg.sender] = Vesting(amount, block.timestamp, cliff);
        balances[msg.sender] = amount;
    }
    function transferVesting(address to, uint256 amount) external {
        balances[msg.sender] -= amount;
        balances[to] += amount;
        // BUG: vesting schedule not transferred → new address can claim immediately
    }
}