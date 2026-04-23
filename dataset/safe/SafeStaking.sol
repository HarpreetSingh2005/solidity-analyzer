// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

// @notice Safe staking pool using Checks-Effects-Interactions pattern and no reentrancy vulnerabilities.
contract SafeStaking {
    mapping(address => uint256) public balances;
    mapping(address => uint256) public lastStakeTime;

    uint256 public rewardRate = 100; // 100 tokens per day

    event Staked(address indexed user, uint256 amount);
    event Withdrawn(address indexed user, uint256 amount);
    event RewardClaimed(address indexed user, uint256 amount);

    function stake() external payable {
        require(msg.value > 0, "Cannot stake 0");
        
        // Effects
        balances[msg.sender] += msg.value;
        lastStakeTime[msg.sender] = block.timestamp;
        
        emit Staked(msg.sender, msg.value);
    }

    function withdraw() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "Nothing to withdraw");
        
        // Effects
        balances[msg.sender] = 0;
        
        // Interactions
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Withdrawn(msg.sender, amount);
    }
}