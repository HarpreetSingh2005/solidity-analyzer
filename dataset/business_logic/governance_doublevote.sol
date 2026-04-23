// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract GovernanceDoubleVote {
    mapping(address => uint256) public balance;
    mapping(uint256 => uint256) public votesFor;
    function vote(uint256 proposalId) external {
        votesFor[proposalId] += balance[msg.sender];
    }
    function transfer(address to, uint256 amount) external {
        balance[msg.sender] -= amount;
        balance[to] += amount;
        // BUG: can vote again after transfer (no snapshot)
    }
}