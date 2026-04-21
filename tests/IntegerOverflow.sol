// SPDX-License-Identifier: MIT
pragma solidity ^0.7.0;

// Test contract for Integer Overflow/Underflow detection
// Uses Solidity 0.7.0 which has NO built-in overflow protection
contract IntegerOverflow {
    mapping(address => uint256) public balances;
    uint256 public totalSupply;

    constructor() {
        totalSupply = 1000;
        balances[msg.sender] = totalSupply;
    }

    // VULNERABLE: uint256 can overflow if _value is crafted carefully
    function transfer(address _to, uint256 _value) public returns (bool) {
        // BUG: balances[msg.sender] -= _value can underflow if _value > balance
        // BUG: balances[_to] += _value can overflow if balance is near max
        balances[msg.sender] -= _value;
        balances[_to] += _value;
        return true;
    }

    // VULNERABLE: multiplication overflow
    function batchMint(address _to, uint256 _amount, uint256 _multiplier) public {
        // BUG: _amount * _multiplier can silently overflow
        uint256 total = _amount * _multiplier;
        balances[_to] += total;
        totalSupply += total;
    }
}
