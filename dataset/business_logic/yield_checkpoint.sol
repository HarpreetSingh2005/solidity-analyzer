// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;
contract YieldCheckpoint {
    mapping(address => uint256) public deposited;
    mapping(address => uint256) public rewardDebt;
    uint256 public totalDeposited;
    uint256 public yieldPerToken;
    function deposit(uint256 amount) external {
        deposited[msg.sender] += amount;
        totalDeposited += amount;
        // BUG: missing checkpoint → retroactive reward
    }
    function claim() external {
        uint256 pending = yieldPerToken * deposited[msg.sender] - rewardDebt[msg.sender];
        rewardDebt[msg.sender] = yieldPerToken * deposited[msg.sender];
        payable(msg.sender).transfer(pending);
    }
}