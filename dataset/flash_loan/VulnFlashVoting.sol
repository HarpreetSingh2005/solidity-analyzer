// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnFlashVoting {
    mapping(address => uint256) public balances;
    mapping(address => bool) public hasVoted;
    uint256 public yesVotes;

    // Vulnerability: Spot voting allows a flash loan to skew the results
    function vote(bool support) external {
        require(!hasVoted[msg.sender], "Already voted");
        hasVoted[msg.sender] = true;
        
        uint256 votingPower = balances[msg.sender];
        if (support) yesVotes += votingPower;
    }
}