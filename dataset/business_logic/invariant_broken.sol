// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract InvariantBroken {
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    function mint(address to, uint256 amount) external {
        balances[to] += amount;
        totalSupply += amount; // BUG: no invariant check
    }
}