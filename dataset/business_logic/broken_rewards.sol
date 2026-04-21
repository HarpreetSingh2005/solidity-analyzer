// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * VULNERABILITY: Broken Staking Reward Distribution
 * CATEGORY: Business Logic — Division-Before-Multiplication Rounding
 *
 * The reward per share is computed as (totalRewards / totalStaked).
 * When totalStaked is large, integer division floors this to 0, meaning
 * ALL accumulated rewards are silently lost. An attacker can deposit a huge
 * amount before the reward epoch ends to dilute everyone else to zero.
 */
contract BrokenRewards {
    mapping(address => uint256) public staked;
    mapping(address => uint256) public rewardDebt;
    uint256 public totalStaked;
    uint256 public totalRewards;
    uint256 public rewardPerShare; // BUG: fixed-point not used → floors to 0

    function deposit(uint256 amount) external {
        _updateRewardPerShare();
        staked[msg.sender] += amount;
        totalStaked       += amount;
        // BUG: rewardDebt set AFTER totalStaked updated, skews debt calc
        rewardDebt[msg.sender] = rewardPerShare * staked[msg.sender];
    }

    function addRewards(uint256 amount) external {
        totalRewards += amount;
        _updateRewardPerShare();
    }

    function _updateRewardPerShare() internal {
        if (totalStaked == 0) return;
        // BUG: integer division truncates — when totalStaked >> totalRewards, result = 0
        rewardPerShare = totalRewards / totalStaked;
    }

    function claimRewards() external {
        _updateRewardPerShare();
        uint256 pending = rewardPerShare * staked[msg.sender] - rewardDebt[msg.sender];
        rewardDebt[msg.sender] = rewardPerShare * staked[msg.sender];
        // pending will be 0 for almost all users if totalStaked is large
        payable(msg.sender).transfer(pending);
    }

    receive() external payable { totalRewards += msg.value; }
}
