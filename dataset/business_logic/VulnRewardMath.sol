// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

contract VulnRewardMath {
    uint256 public totalStake;
    uint256 public rewardPool;
    mapping(address => uint256) public stakes;

    // Vulnerability: Precision loss (dividing before multiplying) can lead to zero rewards
    function claimReward() external {
        uint256 userStake = stakes[msg.sender];
        require(userStake > 0, "No stake");

        uint256 reward = (userStake / totalStake) * rewardPool;
        
        // Transfer reward...
    }
}